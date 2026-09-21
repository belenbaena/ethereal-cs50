import os
import sqlite3
from functools import wraps
from flask import Flask, g, redirect, render_template, request, session, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "ethereal.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
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


@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        user = get_db().execute(
            "SELECT id, name, email FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
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
        "SELECT bubble_id FROM user_bubbles WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    saved_ids = {row["bubble_id"] for row in saved_rows}
    return render_template("my_bubbles.html", bubbles=all_bubbles, saved_ids=saved_ids)


@app.route("/api/bubbles/<int:bubble_id>/toggle", methods=["POST"])
@login_required
def toggle_bubble(bubble_id):
    db = get_db()
    bubble = db.execute("SELECT id FROM bubbles WHERE id = ?", (bubble_id,)).fetchone()
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


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
