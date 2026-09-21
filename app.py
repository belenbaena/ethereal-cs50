import os
import sqlite3
from datetime import timedelta
from functools import wraps

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "ethereal.db"))
IS_PRODUCTION = os.environ.get("APP_ENV") == "production"

app = Flask(__name__)

secret_key = os.environ.get("SECRET_KEY")
if IS_PRODUCTION and not secret_key:
    raise RuntimeError("SECRET_KEY must be set in production.")

app.secret_key = secret_key or "dev-secret-change-me"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    MAX_CONTENT_LENGTH=1024 * 1024,
)


def get_db():
    if "db" not in g:
        database_dir = os.path.dirname(DATABASE)
        if database_dir:
            os.makedirs(database_dir, exist_ok=True)

        g.db = sqlite3.connect(DATABASE, timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        user = get_db().execute(
            "SELECT id, name, email FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()

        if user is None:
            session.clear()

    return {"current_user": user}


@app.route("/")
def index():
    bubbles = get_db().execute("SELECT * FROM bubbles ORDER BY id").fetchall()
    return render_template("index.html", bubbles=bubbles)


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("my_bubbles"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not name or not email or not password or not confirmation:
            flash("Please complete every field.", "error")
            return render_template("register.html")

        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        if password != confirmation:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("register.html")

        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        session.clear()
        session.permanent = True
        session["user_id"] = cursor.lastrowid
        return redirect(url_for("my_bubbles"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("my_bubbles"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session.clear()
        session.permanent = True
        session["user_id"] = user["id"]
        return redirect(url_for("my_bubbles"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/my-bubbles")
@login_required
def my_bubbles():
    db = get_db()
    all_bubbles = db.execute("SELECT * FROM bubbles ORDER BY id").fetchall()
    saved_rows = db.execute(
        "SELECT bubble_id FROM user_bubbles WHERE user_id = ?",
        (session["user_id"],),
    ).fetchall()
    saved_ids = {row["bubble_id"] for row in saved_rows}

    return render_template(
        "my_bubbles.html",
        bubbles=all_bubbles,
        saved_ids=saved_ids,
    )


@app.route("/api/bubbles/<int:bubble_id>/toggle", methods=["POST"])
@login_required
def toggle_bubble(bubble_id):
    db = get_db()
    bubble = db.execute(
        "SELECT id FROM bubbles WHERE id = ?",
        (bubble_id,),
    ).fetchone()

    if bubble is None:
        return jsonify({"error": "Bubble not found"}), 404

    existing = db.execute(
        "SELECT 1 FROM user_bubbles WHERE user_id = ? AND bubble_id = ?",
        (session["user_id"], bubble_id),
    ).fetchone()

    if existing:
        db.execute(
            "DELETE FROM user_bubbles WHERE user_id = ? AND bubble_id = ?",
            (session["user_id"], bubble_id),
        )
        saved = False
    else:
        db.execute(
            "INSERT INTO user_bubbles (user_id, bubble_id) VALUES (?, ?)",
            (session["user_id"], bubble_id),
        )
        saved = True

    db.commit()
    return jsonify({"saved": saved})


@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Initialized ETHEREAL database.")


# Ensure a new deployment has its schema and six ETHEREAL worlds available.
with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
