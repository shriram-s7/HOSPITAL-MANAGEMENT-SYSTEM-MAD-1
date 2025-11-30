from flask import Blueprint,render_template,request,redirect,session,flash,url_for
from utils import query_all,query_one,execute
from database import get_conn

from werkzeug.security import generate_password_hash
admin_bp=Blueprint("admin",__name__,url_prefix="/admin")
def admin_required():
    return session.get("role")=="admin"

@admin_bp.route("",methods=["GET"])
def dashboard():
    if not admin_required(): return redirect("/login")
    total_doctors=query_one("SELECT COUNT(*) FROM doctors")[0]
    total_patients=query_one("SELECT COUNT(*) FROM patients")[0]
    total_appointments=query_one("SELECT COUNT(*) FROM appointments")[0]
    doctors=query_all("SELECT d.id, u.username, d.fullname, d.specialization, u.id FROM doctors d JOIN users u ON d.user_id=u.id")
    patients=query_all("SELECT p.id, u.username, p.fullname, p.contact, u.id FROM patients p JOIN users u ON p.user_id=u.id")
    
    upcoming_appointments=query_all("""SELECT a.id, p.fullname, d.fullname, a.date, a.time_slot, a.status, d.specialization FROM appointments a LEFT JOIN patients p ON a.patient_id=p.id LEFT JOIN doctors d ON a.doctor_id=d.id WHERE a.status = 'Booked' ORDER BY a.date ASC""")
    past_appointments=query_all("""SELECT a.id, p.fullname, d.fullname, a.date, a.time_slot, a.status, d.specialization FROM appointments a LEFT JOIN patients p ON a.patient_id=p.id LEFT JOIN doctors d ON a.doctor_id=d.id WHERE a.status IN ('Completed', 'Cancelled') ORDER BY a.date DESC""")
    
    return render_template("admin_dashboard.html",doctors=doctors,patients=patients,upcoming_appointments=upcoming_appointments,past_appointments=past_appointments,stats=(total_doctors,total_patients,total_appointments))
@admin_bp.route("/doctor/add",methods=["POST"])
def add_doctor():

    if not admin_required(): return redirect("/login")
    username=request.form.get("username","").strip()
    password=request.form.get("password","").strip()
    fullname=request.form.get("fullname","").strip()
    specialization=request.form.get("specialization","").strip()
    if not username or not password:
        flash("Provide username and password for doctor","warning")
        return redirect(url_for("admin.dashboard"))
    conn=get_conn()

    cur=conn.cursor()
    try:
        hashed=generate_password_hash(password)
        cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",(username,hashed,"doctor"))
        user_id=cur.lastrowid
        cur.execute("INSERT INTO doctors (user_id, fullname, specialization) VALUES (?,?,?)",(user_id,fullname,specialization))
        conn.commit()

        flash("Doctor added","success")
    except Exception:
        conn.rollback()
        import traceback,sys
        traceback.print_exc(file=sys.stdout)

        flash("Could not add doctor. Username may exist.","danger")
    finally: conn.close()
    return redirect(url_for("admin.dashboard"))
@admin_bp.route("/search",methods=["GET"])

def search():
    if not admin_required(): return redirect("/login")
    q=request.args.get("q","").strip()
    kind=request.args.get("kind","all")
    doctors=[]
    patients=[]

    if q:
        if kind in ("all","doctor"):
            doctors=query_all("""SELECT d.id, u.username, d.fullname, d.specialization, u.id FROM doctors d JOIN users u ON d.user_id=u.id WHERE d.fullname LIKE ? OR d.specialization LIKE ? OR u.username LIKE ?""",(f"%{q}%",f"%{q}%",f"%{q}%"))
        if kind in ("all","patient"):
            patients=query_all("""SELECT p.id, u.username, p.fullname, p.contact FROM patients p JOIN users u ON p.user_id=u.id WHERE p.fullname LIKE ? OR u.username LIKE ? OR p.contact LIKE ? OR CAST(p.id AS TEXT) LIKE ?""",(f"%{q}%",f"%{q}%",f"%{q}%",f"%{q}%"))
    return render_template("admin_search.html",doctors=doctors,patients=patients,q=q,kind=kind)
@admin_bp.route("/doctor/edit/<int:doc_id>",methods=["GET","POST"])
def edit_doctor(doc_id):
    if not admin_required(): return redirect("/login")
    conn=get_conn()
    cur=conn.cursor()
    if request.method=="POST":
        fullname=request.form.get("fullname","").strip()
        specialization=request.form.get("specialization","").strip()
        try:
            cur.execute("UPDATE doctors SET fullname=?, specialization=? WHERE id=?",(fullname,specialization,doc_id))
            conn.commit()
            flash("Doctor updated","success")
        except Exception:
            conn.rollback()
            flash("Could not update doctor","danger")
        finally: conn.close()
        return redirect(url_for("admin.dashboard"))
    doc=query_one("SELECT d.id, d.fullname, d.specialization, u.username, u.id FROM doctors d JOIN users u ON d.user_id=u.id WHERE d.id=?",(doc_id,))
    return render_template("admin_edit_doctor.html",doc=doc)
@admin_bp.route("/patient/edit/<int:patient_id>",methods=["GET","POST"])
def edit_patient(patient_id):
    if not admin_required(): return redirect("/login")
    conn=get_conn()
    cur=conn.cursor()
    if request.method=="POST":
        fullname=request.form.get("fullname","").strip()
        contact=request.form.get("contact","").strip()
        try:
            cur.execute("UPDATE patients SET fullname=?, contact=? WHERE id=?",(fullname,contact,patient_id))
            conn.commit()
            flash("Patient updated","success")
        except Exception:
            conn.rollback()
            flash("Could not update patient","danger")
        finally: conn.close()
        return redirect(url_for("admin.dashboard"))
    pat=query_one("SELECT id, fullname, contact FROM patients WHERE id=?",(patient_id,))
    return render_template("admin_edit_patient.html",patient=pat)
@admin_bp.route("/blacklist/user/<int:user_id>",methods=["POST"])
def blacklist_user(user_id):
    if not admin_required(): return redirect("/login")
    conn=get_conn()
    cur=conn.cursor()
    try:
        cur.execute("INSERT INTO blacklist (user_id, reason) VALUES (?,?)",(user_id,"Blacklisted by admin"))
        conn.commit()
        flash("User blacklisted","success")
    except Exception:
        conn.rollback()
        flash("Could not blacklist user","danger")
    finally: conn.close()
    return redirect(url_for("admin.dashboard"))