from flask import Blueprint,render_template,request,redirect,session,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
from database import get_conn
from utils import query_one
auth_bp=Blueprint("auth",__name__)
@auth_bp.route("/",methods=["GET"])
def home(): return redirect(url_for("auth.login"))
@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username","").strip()
        password=request.form.get("password","").strip()
        if not username or not password:
            flash("Enter username and password","warning")
            return render_template("login.html")
        try:
            user=query_one("SELECT id, username, password, role FROM users WHERE username=?",(username,))
            if not user:
                flash("Invalid username or password","danger")
                print(f"[login] no user found for username={username}")
                return render_template("login.html")
            user_id,user_name,stored_hash,role=user
            blk=query_one("SELECT id FROM blacklist WHERE user_id=?",(user_id,))
            if blk:
                flash("Account disabled/blacklisted. Contact admin.","danger")
                return render_template("login.html")
            if check_password_hash(stored_hash,password):
                session.clear()
                session["user_id"]=user_id
                session["username"]=user_name
                session["role"]=role
                print(f"[login] success for user_id={user_id} role={role}")
                if role=="admin": return redirect("/admin")
                elif role=="doctor": return redirect("/doctor")
                else: return redirect("/patient")
            else:
                flash("Invalid username or password","danger")
                print(f"[login] password mismatch for username={username}")
                return render_template("login.html")
        except Exception:
            import traceback,sys
            traceback.print_exc(file=sys.stdout)
            flash("Login error - check server console","danger")
            return render_template("login.html")
    return render_template("login.html")
@auth_bp.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        fullname=request.form.get("fullname","").strip()
        username=request.form.get("username","").strip()
        password=request.form.get("password","").strip()
        if not fullname or not username or not password:
            flash("Please fill all fields.","warning")
            return render_template("register.html")
        try:
            conn=get_conn()
            cur=conn.cursor()
            cur.execute("SELECT id FROM users WHERE username=?",(username,))
            if cur.fetchone():
                conn.close()
                flash("Username already exists. Try another.","warning")
                return render_template("register.html")
            hashed=generate_password_hash(password)
            cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",(username,hashed,"patient"))
            user_id=cur.lastrowid
            cur.execute("INSERT INTO patients (user_id, fullname) VALUES (?,?)",(user_id,fullname))
            conn.commit()
            conn.close()
            flash("Registered successfully. Please login.","success")
            return redirect(url_for("auth.login"))
        except Exception:
            import traceback,sys
            traceback.print_exc(file=sys.stdout)
            try: conn.close()
            except: pass
            flash("Registration failed due to an unexpected error. Check server logs.","danger")
    return render_template("register.html")
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))