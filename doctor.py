from flask import Blueprint, render_template, session, redirect, request, flash, url_for
from utils import query_all, query_one, execute
from database import get_conn

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")

def doctor_required():
    return session.get("role") == "doctor"

@doctor_bp.route("", methods=["GET"])
def dashboard():
    if not doctor_required():
        return redirect("/login")
    user_id = session.get("user_id")
    doc = query_one("SELECT id, fullname FROM doctors WHERE user_id=?", (user_id,))
    if not doc:
        flash("Doctor profile not found", "warning")
        return redirect("/login")
    
    doc_id = doc[0]
    appointments = query_all("""SELECT a.id, p.fullname, a.date, a.time_slot, a.status, a.patient_id
                                FROM appointments a
                                LEFT JOIN patients p ON a.patient_id=p.id
                                WHERE a.doctor_id=? AND a.status='Booked'
                                ORDER BY a.date""", (doc_id,))
    
    availability = query_all("SELECT id, date, time_slot, is_available FROM availability WHERE doctor_id=? ORDER BY date", (doc_id,))
    
    patient_history = query_all("""
        SELECT p.id, p.fullname, MAX(t.created_at) as last_visit
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        LEFT JOIN treatments t ON a.id = t.appointment_id
        WHERE a.doctor_id = ? AND a.status = 'Completed'
        GROUP BY p.id, p.fullname
        ORDER BY last_visit DESC
    """, (doc_id,))

    return render_template("doctor_dashboard.html", 
                           appointments=appointments, 
                           doctor=doc, 
                           availability=availability,
                           patient_history=patient_history)

@doctor_bp.route("/appointment/complete/<int:aid>", methods=["POST"])
def complete_appointment(aid):
    if not doctor_required():
        return redirect("/login")
    
    # Get form data from the correct form
    diagnosis = request.form.get(f"diagnosis_{aid}","").strip()
    prescription = request.form.get(f"prescription_{aid}","").strip()
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE appointments SET status=? WHERE id=?", ("Completed", aid))
        cur.execute("INSERT INTO treatments (appointment_id, diagnosis, prescription, notes) VALUES (?,?,?,?)",
                    (aid, diagnosis, prescription, ""))
        conn.commit()
        flash("Marked completed & treatment saved", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Could not save treatment: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("doctor.dashboard"))

@doctor_bp.route("/availability", methods=["POST"])
def provide_availability():
    if not doctor_required():
        return redirect("/login")
    user_id = session.get("user_id")
    doc = query_one("SELECT id FROM doctors WHERE user_id=?", (user_id,))
    if not doc:
        flash("Doctor not found", "danger")
        return redirect(url_for("doctor.dashboard"))
    
    doc_id = doc[0]
    date = request.form.get("date")
    slot = request.form.get("time_slot")
    
    if not date or not slot:
        flash("Provide date and time slot", "warning")
        return redirect(url_for("doctor.dashboard"))
    
    # Check for duplicates
    existing = query_one("SELECT id FROM availability WHERE doctor_id=? AND date=? AND time_slot=?", (doc_id, date, slot))
    if existing:
        flash("This availability slot already exists.", "warning")
        return redirect(url_for("doctor.dashboard"))
        
    try:
        execute("INSERT INTO availability (doctor_id, date, time_slot, is_available) VALUES (?,?,?,1)",
                (doc_id, date, slot))
        flash("Availability added", "success")
    except Exception:
        flash("Could not add availability", "danger")
    return redirect(url_for("doctor.dashboard"))

# (Find this function in doctor.py and replace it)

# (Find this function in doctor.py and replace it)

@doctor_bp.route("/patient/<int:patient_id>/history", methods=["GET"])
def patient_history(patient_id):
    if not doctor_required():
        return redirect("/login")
    
    # UPDATED QUERY: We have removed t.notes from the SELECT list
    treatments = query_all("""
        SELECT t.id, t.appointment_id, t.diagnosis, t.prescription, t.created_at, a.date, d.fullname
        FROM treatments t
        JOIN appointments a ON t.appointment_id=a.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id=? ORDER BY t.created_at DESC
    """, (patient_id,))
    
    patient = query_one("SELECT id, fullname FROM patients WHERE id=?", (patient_id,))
    
    return render_template("doctor_patient_history.html", treatments=treatments, patient=patient)
@doctor_bp.route("/availability/delete/<int:avail_id>", methods=["POST"])
def delete_availability(avail_id):
    if not doctor_required():
        return redirect("/login")
    user_id = session.get("user_id")
    doc_id = query_one("SELECT id FROM doctors WHERE user_id=?", (user_id,))[0]
    
    # Ensure doctor can only delete their own
    execute("DELETE FROM availability WHERE id=? AND doctor_id=? AND is_available=1", (avail_id, doc_id))
    flash("Availability slot removed.", "success")
    return redirect(url_for("doctor.dashboard"))