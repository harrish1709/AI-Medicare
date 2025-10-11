from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os
import pandas as pd
import openai

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- LLM API Setup (Groq AI with LLaMA 3) ---
openai.api_key = os.getenv("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")
openai.api_base = "https://api.groq.com/openai/v1"

# --- Constants ---
DB = "governance.db"
DATASET_PATH = "healthcare_data.csv"  # Replace with actual path

# --- Initialize DB ---
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            user TEXT,
            role TEXT,
            prompt TEXT,
            output TEXT,
            status TEXT,
            reason TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            user TEXT,
            helpful TEXT,
            comment TEXT
        )''')
        conn.commit()

init_db()

def ml_prompt_guard(prompt):
    try:
        response = requests.post(  # ✅ Changed from request.post
            "https://toxic-bert.onrender.com/moderate",  # Make sure this endpoint exists
            json={"text": prompt},
            timeout=30
        )
        data = response.json()
        toxic_score = data.get("toxic_score", 0)
        if toxic_score > 0.6:
            return False, f"Prompt flagged as toxic (score: {toxic_score:.2f})"
        return True, ""
    except Exception as e:
        print("Toxic BERT Error:", e)
        return True, ""  # fail-safe if microservice fails

def keyword_prompt_guard(prompt):
    medical_banned = [
        "overdose", "inject", "suicide", "self-harm", "euthanasia", "snort", "meth", "opioid",
        "prescribe", "self-medicate", "cure cancer", "natural cure", "miracle treatment",
        "abortion", "antivax", "homeopathy", "iv drip", "experimental drug", "black market"]
    banned = ["bomb", "kill", "attack", "password", "rape", "terrorist", "drugs", "murder", "abuse"] + medical_banned
    for word in banned:
        if word in prompt.lower():
            return False, "Prompt contains restricted terms."
    return True, ""

def prompt_guard(prompt):
    passed, reason = ml_prompt_guard(prompt)
    if not passed:
        return False, reason
    return keyword_prompt_guard(prompt)

def policy_enforcer(prompt, role):
    if "data" in prompt.lower() and role != "admin":
        return False, "Only Admins can access structured medical datasets."
    return True, ""

def output_auditor(output):
    flagged = [
        "violence", "fake news", "disinformation", "misinformation", "self-harm", "suicide",
        "hate speech", "extremism", "terrorism", "abuse", "murder", "rape", "torture", "genocide",
        "racist", "sexist", "homophobic", "transphobic", "pedophile", "incest", "drug trafficking",
        "illegal activity", "black market", "child abuse", "grooming", "weaponize", "radicalize",
        "dangerous advice", "unethical", "harmful", "offensive", "exploit", "coerce", "harass",
        "bully", "false claims"]
    for word in flagged:
        if word in output.lower():
            return False, "Output contains sensitive or non-compliant content."
    return True, ""

def generate_advice(reason):
    return f"⚠️ Reason: {reason} Please rephrase your prompt or contact admin."

def sanitize_output(text):
    return text.encode("utf-8", "replace").decode("utf-8")

# --- Dataset Handling ---
def handle_dataset_request(prompt):
    try:
        df = pd.read_csv(DATASET_PATH)
        prompt_lower = prompt.lower()

        if "cancer" in prompt_lower:
            result = df[df["Condition"].str.lower().str.contains("cancer")].head()
        elif "heart" in prompt_lower:
            result = df[df["Condition"].str.lower().str.contains("heart")].head()
        elif "diabetes" in prompt_lower:
            result = df[df["Condition"].str.lower().str.contains("diabetes")].head()
        else:
            result = df.head(5)

        return f"<h5>📊 Medical Data (Preview):</h5>{result.to_html(index=False, classes='table table-striped table-bordered table-hover')}"
    except Exception as e:
        return f"⚠️ Error accessing dataset: {str(e)}"

# --- LLM Call ---
def call_llm(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,  # increased from 512
            temperature=0.7
        )
        return sanitize_output(response['choices'][0]['message']['content'])
    except Exception as e:
        return f"Error calling model: {str(e)}"

# --- Logging ---
def log_action(user, role, prompt, output, status, reason):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO logs VALUES (NULL,?,?,?,?,?,?,?)",
                  (datetime.now(), user, role, prompt, output, status, reason))
        conn.commit()

# --- Pagination ---
def paginate(query, page, per_page=10):
    start = (page - 1) * per_page
    end = start + per_page
    return query[start:end]

# --- Routes ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        hashed_pw = generate_password_hash(password)
        try:
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                          (username, hashed_pw, role))
                conn.commit()
                flash("Signup successful. Please login.", "success")
                return redirect(url_for("login"))
        except:
            flash("Username already exists.", "danger")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            if row and check_password_hash(row[0], password):
                session["username"] = username
                session["role"] = row[1]
                return redirect(url_for("dashboard") if row[1] == "analyst" else url_for("index"))
            else:
                flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    output = advice = ""
    if request.method == "POST":
        prompt = request.form["prompt"]
        user = session["username"]
        role = session["role"]

        passed, reason = prompt_guard(prompt)
        if not passed:
            advice = generate_advice(reason)
            log_action(user, role, prompt, "", "Rejected", reason)
            return render_template("index.html", output="❌ Blocked", advice=advice)

        passed, reason = policy_enforcer(prompt, role)
        if not passed:
            advice = generate_advice(reason)
            log_action(user, role, prompt, "", "Denied", reason)
            return render_template("index.html", output="🚫 Access Denied", advice=advice)

        response = handle_dataset_request(prompt) if role == "admin" and "data" in prompt.lower() else call_llm(prompt)

        passed, reason = output_auditor(response)
        if not passed:
            advice = generate_advice(reason)
            log_action(user, role, prompt, response, "Filtered", reason)
            return render_template("index.html", output="⚠️ Output filtered", advice=advice)

        log_action(user, role, prompt, response, "Approved", "")
        output = response

    return render_template("index.html", output=output, advice=advice, user=session["username"], role=session["role"])

@app.route("/feedback", methods=["POST"])
def feedback():
    if "username" not in session:
        return redirect(url_for("login"))
    helpful = request.form["helpful"]
    comment = request.form["comment"]
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO feedback VALUES (NULL,?,?,?,?)",
                  (datetime.now(), session["username"], helpful, comment))
        conn.commit()
    flash("Thanks for your feedback!", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if session.get("role") != "analyst":
        return abort(403)
    page = int(request.args.get("page", 1))
    per_page = 10
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = c.fetchall()
        c.execute("SELECT * FROM feedback ORDER BY timestamp DESC")
        feedback = c.fetchall()
    logs_paginated = paginate(logs, page, per_page)
    feedback_paginated = paginate(feedback, page, per_page)
    return render_template("dashboard.html", logs=logs_paginated, feedback=feedback_paginated, page=page)

@app.route("/users", methods=["GET", "POST"])
def manage_users():
    if session.get("role") != "admin":
        return abort(403)
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        if request.method == "POST":
            to_delete = request.form["username"]
            if to_delete != session["username"]:
                c.execute("DELETE FROM users WHERE username = ?", (to_delete,))
                conn.commit()
                flash(f"Deleted user: {to_delete}", "info")
            else:
                flash("You cannot delete your own account.", "warning")
        c.execute("SELECT id, username, role FROM users")
        users = c.fetchall()
    return render_template("users.html", users=users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
