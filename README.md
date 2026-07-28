# pip install brainrot 💀

> requirements.txt is not a suggestion, it's a cry for help

⚠️ **Intentionally vulnerable.** Python sibling of `package-broken🥀`, built to exercise Safeguard
scanning and remediation on the PyPI ecosystem. Never deploy it, never expose it to a network,
never copy code out of it.

## Dependency situation

61 pinned packages across `requirements.txt` + `requirements-dev.txt`, all frozen around 2018.
Queried against OSV.dev:

- **683 raw advisory matches**
- **47 of 61 packages** carry at least one advisory

(Raw count — OSV returns both GHSA and PYSEC records for the same CVE, so a deduping scanner will
report a smaller number. Still a lot.)

Worst offenders: Pillow 5.2.0 (108), aiohttp 3.5.4 (83), Django 2.2.0 (65), ansible 2.6.1 (60),
tornado 5.1 (27), urllib3 1.24.1 (24), Twisted 18.7.0 (24), Scrapy 1.5.0 (21), Werkzeug 0.14.1 (20).
Plus the classics: Flask 0.12.2, Jinja2 2.10, PyYAML 3.13, requests 2.19.1, PyJWT 1.5.3,
cryptography 2.3, pycrypto 2.6.1, paramiko 2.4.1, itsdangerous 0.24, setuptools 39.0.1.

## Code-level issues

| File | Issue classes |
|---|---|
| `brainrot/config.py` | hardcoded secrets, dummy private key, `VERIFY_TLS = False` |
| `brainrot/db.py` | SQL injection (f-string, `%`, concat), interpolated `ORDER BY`, `executescript`, unbound `text()` |
| `brainrot/auth.py` | MD5/SHA1 hashing, `jwt.decode(verify=False)`, `none` alg, `random` for tokens, guessable reset token, `assert` as authz |
| `brainrot/loaders.py` | `pickle.loads` / `marshal.loads`, `yaml.load`, XXE via lxml, tar/zip slip, `shell=True`, `os.system` |
| `brainrot/fetcher.py` | SSRF, `verify=False`, `AutoAddPolicy`, telnet/ftp cleartext, hardcoded creds |
| `app.py` | SSTI (`render_template_string`), `eval`/`exec` on request data, command injection, path traversal, arbitrary write + `chmod 777`, open redirect, insecure cookies, CORS `*` with credentials, header-based authz, creds logged, stack traces returned, `debug=True` on `0.0.0.0` |
| `settings.py` | `DEBUG=True`, hardcoded `SECRET_KEY`, `ALLOWED_HOSTS=['*']`, CSRF middleware removed, MD5 password hashers, all security headers off, `X_FRAME_OPTIONS=ALLOWALL`, DRF `AllowAny` |
| `scripts/sigma_worker.py` | Celery `pickle` serializer, `pickle.loads` of queue payloads, Mako template injection, insecure temp files, MD5 checksums |
| `templates/index.html` | `\|safe` on untrusted values, DOM XSS from `location.hash`, `eval` of a query param, no CSRF token |
| `Dockerfile` | EOL `python:3.6.8-stretch`, root user, secrets in ENV, `PYTHONHTTPSVERIFY=0`, `chmod -R 777` |
| `docker-compose.yml` | `privileged: true`, docker socket + `/` mounted, mysql:5.6, redis 4.0.9 with protected-mode off |
| `.github/workflows/ci.yml` | `pull_request_target` + PR-head checkout, `permissions: write-all`, script injection via PR title, `curl \| bash` |
| `.env.example` | placeholder secrets committed |

All modules are syntactically valid (`py_compile` clean) so AST-based SAST can actually walk them.

## Running it

Not needed for scanning — SCA reads the requirements files, SAST reads the source.

A real `pip install -r requirements.txt` **will fail on Python 3.12** (this box has 3.12.10):
cryptography 2.3, lxml 4.2.5, numpy 1.16.0, and Pillow 5.2.0 all predate modern build backends.
That's expected and doesn't affect scan results. If you need it importable, use Python 3.6–3.8 in a
container.

## Using it for remediation testing

1. Push to a private repo and onboard it in Safeguard.
2. Deep scan — expect SCA, SAST, secrets, and container/IaC findings.
3. Trigger remediation. Python fixes rewrite the pinned versions in `requirements.txt` /
   `requirements-dev.txt` — that diff is the thing to verify.
4. Reset between runs: `git checkout -- requirements.txt requirements-dev.txt`.
