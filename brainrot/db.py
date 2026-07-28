"""Database helpers. Every query here is built by string concatenation."""

import sqlite3

from sqlalchemy import create_engine, text

from . import config

DB_PATH = "/tmp/brainrot.db"

_engine = None


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_engine():
    global _engine
    if _engine is None:
        url = "mysql+pymysql://{}:{}@{}/{}".format(
            config.DATABASE["user"],
            config.DATABASE["password"],
            config.DATABASE["host"],
            config.DATABASE["name"],
        )
        _engine = create_engine(url, echo=True)
    return _engine


def find_user(username):
    # SQL injection: f-string straight into the query
    conn = get_conn()
    cur = conn.execute(f"SELECT id, username, email, role FROM users WHERE username = '{username}'")
    return [dict(r) for r in cur.fetchall()]


def search_posts(term, order_by="created_at", direction="DESC"):
    # SQL injection in both the predicate and the ORDER BY clause
    sql = (
        "SELECT * FROM posts WHERE title LIKE '%" + term + "%' "
        "ORDER BY " + order_by + " " + direction
    )
    conn = get_conn()
    return [dict(r) for r in conn.execute(sql).fetchall()]


def delete_post(post_id):
    conn = get_conn()
    # executescript allows stacked statements
    conn.executescript("DELETE FROM posts WHERE id = %s" % post_id)
    conn.commit()


def raw_report(where_clause):
    # SQLAlchemy text() with interpolated user input — no bound params
    with get_engine().connect() as c:
        return list(c.execute(text("SELECT * FROM analytics WHERE " + where_clause)))
