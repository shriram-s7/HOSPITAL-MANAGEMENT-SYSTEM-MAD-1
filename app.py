from flask import Flask
import os
from database import init_db
from auth import auth_bp
from admin import admin_bp
from doctor import doctor_bp
from patient import patient_bp
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-please-change")
init_db()
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(patient_bp)
if __name__ == "__main__":
    app.run(debug=True)