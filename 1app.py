import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import stripe

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

DB_NAME = "users.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            stripe_customer_id TEXT,
            is_pro INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    return user

@app.route("/", methods=["GET"])
@login_required
def index():
    user = current_user()
    return render_template("dashboard.html", user=user, base_url=BASE_URL)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for("signup"))

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("That username is already taken.")
            return redirect(url_for("signup"))

        conn.close()
        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if not user:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    user = current_user()
    if not STRIPE_PRICE_ID:
        return "Missing STRIPE_PRICE_ID", 500

    if user["stripe_customer_id"]:
        customer_id = user["stripe_customer_id"]
    else:
        customer = stripe.Customer.create(
            email=user["email"] or None,
            metadata={"user_id": user["id"], "username": user["username"]}
        )
        customer_id = customer["id"]
        conn = get_db()
        conn.execute("UPDATE users SET stripe_customer_id = ? WHERE id = ?", (customer_id, user["id"]))
        conn.commit()
        conn.close()

    session_checkout = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        success_url=f"{BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{BASE_URL}/cancel",
    )
    return redirect(session_checkout.url, code=303)

@app.route("/success")
@login_required
def success():
    return redirect(url_for("index"))

@app.route("/cancel")
@login_required
def cancel():
    flash("Checkout canceled.")
    return redirect(url_for("index"))

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    if not STRIPE_WEBHOOK_SECRET:
        return "Missing STRIPE_WEBHOOK_SECRET", 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception:
        return "Bad webhook", 400

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        customer_id = session_obj.get("customer")
        if customer_id:
            conn = get_db()
            conn.execute("UPDATE users SET is_pro = 1 WHERE stripe_customer_id = ?", (customer_id,))
            conn.commit()
            conn.close()

    if event["type"] in ("customer.subscription.deleted", "customer.subscription.updated"):
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        status = sub.get("status")
        is_pro = 1 if status == "active" else 0
        conn = get_db()
        conn.execute("UPDATE users SET is_pro = ? WHERE stripe_customer_id = ?", (is_pro, customer_id))
        conn.commit()
        conn.close()

    return "", 200

@app.route("/doclens", methods=["GET", "POST"])
@login_required
def doclens():
    user = current_user()
    if not user["is_pro"]:
        flash("This feature is for Pro users only.")
        return redirect(url_for("index"))

    if request.method == "POST":
        document = request.form.get("document", "")
        simplified = document
        return render_template("dashboard.html", user=user, base_url=BASE_URL, document=document, simplified=simplified)

    return render_template("dashboard.html", user=user, base_url=BASE_URL)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

