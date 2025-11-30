import sqlite3
import os
from werkzeug.security import generate_password_hash
BASE_DIR=os.path.dirname(os.path.abspath(__file__))

DB_PATH=os.path.join(BASE_DIR,"hospital.db")
def get_conn(): return sqlite3.connect(DB_PATH)
def init_db():
    conn=sqlite3.connect(DB_PATH)
    c=conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, fullname TEXT, specialization TEXT, bio TEXT, FOREIGN KEY(user_id) REFERENCES users(id))""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, fullname TEXT, contact TEXT, age INTEGER, gender TEXT, FOREIGN KEY(user_id) REFERENCES users(id))""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, doctor_id INTEGER, date TEXT, time_slot TEXT, status TEXT DEFAULT 'Booked', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(patient_id) REFERENCES patients(id), FOREIGN KEY(doctor_id) REFERENCES doctors(id))""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS treatments (id INTEGER PRIMARY KEY AUTOINCREMENT, appointment_id INTEGER, diagnosis TEXT, prescription TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(appointment_id) REFERENCES appointments(id))""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS availability (id INTEGER PRIMARY KEY AUTOINCREMENT, doctor_id INTEGER, date TEXT, time_slot TEXT, is_available INTEGER DEFAULT 1, FOREIGN KEY(doctor_id) REFERENCES doctors(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, reason TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    try:
        c.execute("SELECT id FROM users WHERE role='admin' LIMIT 1")
        if not c.fetchone():
            hashed=generate_password_hash("admin123")
            c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",("admin",hashed,"admin"))
    except Exception: pass
    conn.commit()
    conn.close()