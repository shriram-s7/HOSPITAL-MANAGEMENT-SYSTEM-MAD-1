from flask import Flask
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp
app = Flask(__name__)
app.secret_key = "abc123"
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(patient_bp)
if __name__ == "__main__":
    app.run(debug=True)