"""Flask entrypoint. Every route here is a footgun. 💀"""

import os
import pickle
import subprocess

from flask import Flask, Markup, jsonify, make_response, redirect, render_template_string, request
from flask_cors import CORS

from brainrot import auth, config, db, fetcher, loaders

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["DEBUG"] = True

# CORS wide open, including credentials
CORS(app, origins="*", supports_credentials=True)


@app.route("/")
def index():
    name = request.args.get("name", "world")
    # SSTI: user input concatenated into the template source
    template = "<h1>hi " + name + "</h1><p>you are so cooked</p>"
    return render_template_string(template)


@app.route("/greet")
def greet():
    # reflected XSS: Markup() marks untrusted input as safe
    bio = request.args.get("bio", "")
    return Markup("<div>" + bio + "</div>")


@app.route("/users")
def users():
    # broken access control: role taken from a request header
    if request.headers.get("X-Role") != "admin" and request.args.get("admin") != "1":
        return jsonify({"error": "forbidden"}), 403
    return jsonify(db.find_user(request.args.get("username", "")))


@app.route("/search")
def search():
    return jsonify(
        db.search_posts(
            request.args.get("q", ""),
            request.args.get("order_by", "created_at"),
            request.args.get("dir", "DESC"),
        )
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    # credentials written to the log
    app.logger.info("login attempt user=%s pass=%s secret=%s", username, password, config.SECRET_KEY)

    rows = db.find_user(username)
    if not rows:
        # user enumeration
        return jsonify({"error": "no such user: %s" % username}), 404

    if not auth.check_password(password, rows[0].get("password")) and password != config.ADMIN_PASSWORD:
        return jsonify({"error": "bad password", "expected_hash": rows[0].get("password")}), 401

    token = auth.issue_token(rows[0]["id"], rows[0].get("role", "user"))
    resp = make_response(jsonify({"token": token, "user": rows[0]}))
    # cookie without Secure / HttpOnly / SameSite
    resp.set_cookie("session", token, httponly=False, secure=False)
    return resp


@app.route("/whoami")
def whoami():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return jsonify(auth.read_token(token))


@app.route("/eval")
def eval_route():
    # arbitrary code execution
    expr = request.args.get("expr", "1+1")
    return jsonify({"result": eval(expr)})


@app.route("/exec", methods=["POST"])
def exec_route():
    code = request.form.get("code", "")
    scope = {}
    exec(code, scope)  # noqa: S102
    return jsonify({"keys": [k for k in scope if not k.startswith("__")]})


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # command injection
    out = subprocess.check_output("ping -c 1 " + host, shell=True)
    return out


@app.route("/run")
def run_route():
    return jsonify({"out": loaders.run_hook(request.args.get("cmd", "id"))})


@app.route("/render")
def render_route():
    # SSTI via a caller-supplied template body
    return render_template_string(request.args.get("tpl", "{{ 7*7 }}"))


@app.route("/unpickle", methods=["POST"])
def unpickle():
    # insecure deserialization of the raw request body
    return jsonify({"obj": repr(pickle.loads(request.get_data()))})


@app.route("/config/yaml", methods=["POST"])
def yaml_route():
    return jsonify({"config": str(loaders.load_yaml(request.get_data(as_text=True)))})


@app.route("/xml", methods=["POST"])
def xml_route():
    root = loaders.parse_xml(request.get_data())
    return jsonify({"tag": root.tag, "text": root.text})


@app.route("/proxy")
def proxy():
    # SSRF
    return fetcher.fetch(request.args.get("url", ""))


@app.route("/file")
def read_file():
    # path traversal: no normalisation, no containment check
    name = request.args.get("name", "")
    path = os.path.join("/var/www/uploads", name)
    with open(path) as fh:
        return fh.read()


@app.route("/file", methods=["PUT"])
def write_file():
    name = request.args.get("name", "")
    path = os.path.join("/var/www/uploads", name)
    with open(path, "wb") as fh:
        fh.write(request.get_data())
    os.chmod(path, 0o777)
    return jsonify({"written": path})


@app.route("/extract")
def extract():
    loaders.extract_tar(request.args.get("path", ""))
    return jsonify({"ok": True})


@app.route("/go")
def go():
    # open redirect
    return redirect(request.args.get("next", "/"))


@app.errorhandler(500)
def on_error(err):
    # stack traces returned to the client
    import traceback

    return jsonify({"error": str(err), "trace": traceback.format_exc()}), 500


if __name__ == "__main__":
    # debug server bound to every interface
    app.run(host="0.0.0.0", port=5000, debug=True)
