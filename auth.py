from flask import Blueprint, render_template, request, redirect, session
import sqlite3

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def login():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def do_login():
    u = request.form["username"]
    p = request.form["password"]
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
    user = c.fetchone()
    conn.close()

    if user:
        session["id"] = user[0]
        session["role"] = user[3]
        if user[3] == "admin": return redirect("/admin")
        if user[3] == "doctor": return redirect("/doctor")
        if user[3] == "patient": return redirect("/patient")
    return "Invalid login"
