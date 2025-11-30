from flask import Blueprint,render_template,request,redirect,session,flash,url_for,jsonify
from utils import query_all,query_one,execute
import datetime

patient_bp=Blueprint("patient",__name__,url_prefix="/patient")

def patient_required():
    return session.get("role")=="patient"
@patient_bp.route("",methods=["GET"])
def dashboard():
    if not patient_required(): return redirect("/login")

    user_id=session.get("user_id")
    pat=query_one("SELECT id, fullname FROM patients WHERE user_id=?",(user_id,))
    if not pat:
        flash("Patient profile not found.","danger")

        return redirect("/login")
    
    departments=query_all("SELECT DISTINCT specialization FROM doctors WHERE specialization IS NOT NULL AND specialization != ''")
    appointments=query_all("""SELECT a.id, d.fullname, d.specialization, a.date, a.time_slot, a.status FROM appointments a LEFT JOIN doctors d ON a.doctor_id = d.id WHERE a.patient_id=? AND a.status = 'Booked' ORDER BY a.date ASC""",(pat[0],))
    return render_template("patient_dashboard.html",patient=pat,departments=departments,appointments=appointments)
@patient_bp.route("/department/<string:dept_name>",methods=["GET"])

def department_detail(dept_name):
    if not patient_required(): return redirect("/login")

    doctors=query_all("SELECT id, fullname, bio FROM doctors WHERE specialization=?",(dept_name,))
    return render_template("department_detail.html",dept_name=dept_name,doctors=doctors)
@patient_bp.route("/doctor/<int:doc_id>",methods=["GET"])
def doctor_availability(doc_id):

    if not patient_required(): return redirect("/login")
    doctor=query_one("SELECT id, fullname, specialization, bio FROM doctors WHERE id=?",(doc_id,))
    if not doctor:
        flash("Doctor not found.","danger")
        return redirect(url_for("patient.dashboard"))
    today=datetime.date.today()
    week_dates=[(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    availability={}
    for date in week_dates:
        slots=query_all("""SELECT id, time_slot, is_available FROM availability WHERE doctor_id=? AND date=? ORDER BY time_slot""",(doc_id,date))
        availability[date]=slots
    return render_template("doctor_availability.html",doctor=doctor,availability=availability,week_dates=week_dates)
@patient_bp.route("/book",methods=["POST"])

def book():
    if not patient_required(): return redirect("/login")
    user_id=session.get("user_id")
    pat=query_one("SELECT id FROM patients WHERE user_id=?",(user_id,))

    if not pat:
        flash("Patient profile missing","danger"); return redirect(url_for("patient.dashboard"))
    
    patient_id=pat[0]
    avail_id=request.form.get("availability_id")
    doc_id=request.form.get("doctor_id")
    if not avail_id:
        flash("Please select an availability slot.","warning")

        return redirect(url_for("patient.doctor_availability",doc_id=doc_id))
    try: avail_id=int(avail_id)
    except:
        flash("Invalid slot selected.","danger")
        return redirect(url_for("patient.doctor_availability",doc_id=doc_id))
    av=query_one("SELECT id, doctor_id, date, time_slot, is_available FROM availability WHERE id=?",(avail_id,))
    if not av or av[4]!=1:
        flash("Selected slot is no longer available.","warning")

        return redirect(url_for("patient.doctor_availability",doc_id=doc_id))
    try:
        
        execute("INSERT INTO appointments (patient_id, doctor_id, date, time_slot, status) VALUES (?,?,?,?,?)",(patient_id,av[1],av[2],av[3],"Booked"))
        execute("UPDATE availability SET is_available=0 WHERE id=?",(avail_id,))
        flash("Appointment booked successfully!","success")
    except Exception:
        
        flash("Could not book appointment due to a system error.","danger")
        return redirect(url_for("patient.doctor_availability",doc_id=doc_id))
    return redirect(url_for("patient.dashboard"))
@patient_bp.route("/appointment/cancel/<int:aid>",methods=["POST"])
def cancel(aid):
    if not patient_required(): return redirect("/login")
    
    user_id=session.get("user_id")
    pat_id=query_one("SELECT id FROM patients WHERE user_id=?",(user_id,))[0]
    try:
        
        ap=query_one("SELECT doctor_id, date, time_slot FROM appointments WHERE id=? AND patient_id=?",(aid,pat_id))
        if ap:
            execute("""UPDATE availability SET is_available=1 WHERE doctor_id=? AND date=? AND time_slot=? AND is_available=0""",(ap[0],ap[1],ap[2]))
        execute("UPDATE appointments SET status='Cancelled' WHERE id=? AND patient_id=?",(aid,pat_id))
        flash("Appointment cancelled.","success")
    except Exception:
        flash("Could not cancel appointment.","danger")
    return redirect(url_for("patient.dashboard"))
@patient_bp.route("/history",methods=["GET"])
def history():
    if not patient_required(): return redirect("/login")
    user_id=session.get("user_id")
    pat=query_one("SELECT id, fullname FROM patients WHERE user_id=?",(user_id,))
    if not pat: return redirect("/login")
    treatments=query_all("""SELECT t.id, t.diagnosis, t.prescription, t.created_at, a.date, d.fullname as doctor_name, d.specialization FROM treatments t JOIN appointments a ON t.appointment_id = a.id JOIN doctors d ON a.doctor_id = d.id WHERE a.patient_id=? ORDER BY t.created_at DESC""",(pat[0],))
    return render_template("patient_history.html",treatments=treatments,patient=pat)
@patient_bp.route("/profile",methods=["GET","POST"])
def edit_profile():
    if not patient_required(): return redirect("/login")
    user_id=session.get("user_id")
    if request.method=="POST":
        fullname=request.form.get("fullname","").strip()
        contact=request.form.get("contact","").strip()
        age=request.form.get("age") or None
        gender=request.form.get("gender","").strip()
        execute("UPDATE patients SET fullname=?, contact=?, age=?, gender=? WHERE user_id=?",(fullname,contact,age,gender,user_id))
        flash("Profile updated","success")
        return redirect(url_for("patient.dashboard"))
    pat=query_one("SELECT id, fullname, contact, age, gender FROM patients WHERE user_id=?",(user_id,))
    return render_template("patient_edit.html",patient=pat)
@patient_bp.route("/search_doctor",methods=["GET"])
def search_doctor():
    if not patient_required(): return redirect("/login")
    q=request.args.get("q","").strip()
    doctors=query_all("""SELECT id, fullname, specialization, bio FROM doctors WHERE fullname LIKE ? OR specialization LIKE ?""",(f"%{q}%",f"%{q}%"))
    return render_template("department_detail.html",dept_name=f"Search Results for '{q}'",doctors=doctors)