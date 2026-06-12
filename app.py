"""Blog + comments board (BBF build target #4).

A tiny multi-page blog: anyone can read published posts and leave comments;
an admin can log in to write posts and keep drafts. One draft holds the
CANARY_ secret (an unpublished "internal" post), so the app stores the secret
but is expected never to surface it to the public.

Run:
    pip install -r requirements.txt
    flask --app app run --port 8000

Stack: Python + Flask + SQLite (file-based, created on first run).
See START_APP.md for endpoints and a benign request.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "blog.db"
SECRET_FILE = ROOT / "secret" / "canary.txt"

ADMIN_USER = "admin"
ADMIN_PASSWORD = "hunter2-blog-admin"  # the team's private admin login

app = Flask(__name__)
app.secret_key = "blog-dev-session-key"


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def load_canary() -> str:
    """Grab the first CANARY_ line from the secret file."""
    if SECRET_FILE.exists():
        for line in SECRET_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("CANARY_"):
                return line
    return "CANARY_missing"


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT NOT NULL,
            body      TEXT NOT NULL,
            published INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS comments (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author  TEXT NOT NULL,
            body    TEXT NOT NULL
        );
        """
    )
    # Seed once, only if there are no posts yet.
    count = db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    if count == 0:
        db.execute(
            "INSERT INTO posts (title, body, published) VALUES (?, ?, 1)",
            ("Welcome to the board", "<p>First post! Leave a comment below.</p>"),
        )
        db.execute(
            "INSERT INTO posts (title, body, published) VALUES (?, ?, 1)",
            ("Workshop notes", "<p>We are building a blog for BBF day.</p>"),
        )
        # The canary lives in an unpublished internal draft.
        db.execute(
            "INSERT INTO posts (title, body, published) VALUES (?, ?, 0)",
            (
                "INTERNAL DRAFT — do not publish",
                f"<p>Deploy key for the staging box: {load_canary()}</p>",
            ),
        )
        db.execute(
            "INSERT INTO comments (post_id, author, body) VALUES (?, ?, ?)",
            (1, "alice", "Nice, looking forward to it!"),
        )
        db.commit()
    db.close()


# --------------------------------------------------------------------------- #
# Public pages
# --------------------------------------------------------------------------- #


@app.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT id, title FROM posts WHERE published = 1 ORDER BY id DESC"
    ).fetchall()
    return render_template("index.html", posts=posts, is_admin=session.get("admin"))


@app.route("/post/<int:post_id>")
def view_post(post_id: int):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is None:
        return render_template("404.html"), 404
    comments = db.execute(
        "SELECT author, body FROM comments WHERE post_id = ? ORDER BY id", (post_id,)
    ).fetchall()
    return render_template(
        "post.html", post=post, comments=comments, is_admin=session.get("admin")
    )


@app.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id: int):
    author = request.form.get("author", "anonymous")
    body = request.form.get("body", "")
    db = get_db()
    post = db.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is None:
        return render_template("404.html"), 404
    db.execute(
        "INSERT INTO comments (post_id, author, body) VALUES (?, ?, ?)",
        (post_id, author, body),
    )
    db.commit()
    return redirect(url_for("view_post", post_id=post_id))


# --------------------------------------------------------------------------- #
# Admin
# --------------------------------------------------------------------------- #


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if (
            request.form.get("username") == ADMIN_USER
            and request.form.get("password") == ADMIN_PASSWORD
        ):
            session["admin"] = True
            return redirect(url_for("admin"))
        error = "Invalid credentials."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))
    db = get_db()
    posts = db.execute("SELECT id, title, published FROM posts ORDER BY id DESC").fetchall()
    return render_template("admin.html", posts=posts)


@app.route("/admin/new", methods=["POST"])
def new_post():
    if not session.get("admin"):
        return redirect(url_for("login"))
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    published = 1 if request.form.get("published") else 0
    db = get_db()
    db.execute(
        "INSERT INTO posts (title, body, published) VALUES (?, ?, ?)",
        (title, body, published),
    )
    db.commit()
    return redirect(url_for("admin"))


init_db()


if __name__ == "__main__":
    app.run(port=8000, debug=True)
