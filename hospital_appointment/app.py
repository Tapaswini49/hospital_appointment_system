from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("hospital.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT,
                    doctor_name TEXT,
                    date TEXT,
                    time TEXT,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id))""")
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        try:
            conn = sqlite3.connect("hospital.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect("/login")
        except:
            flash("Username already exists!", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("hospital.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/dashboard")
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("hospital.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments WHERE user_id=?", (session["user_id"],))
    appointments = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", username=session["username"], appointments=appointments)

@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        date = request.form["date"]
        time = request.form["time"]

        conn = sqlite3.connect("hospital.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO appointments (patient_name, doctor_name, date, time, user_id) VALUES (?, ?, ?, ?, ?)",
                    (patient_name, doctor_name, date, time, session["user_id"]))
        conn.commit()
        conn.close()
        flash("Appointment booked successfully!", "success")
        return redirect("/dashboard")

    return render_template("appointment.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
