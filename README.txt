HOSPITAL MANAGEMENT SYSTEM (HMS)
==================================================

A web-based application built with Flask for managing hospital operations,
including doctor profiles, patient appointments, and medical history tracking.


FRAMEWORKS USED
--------------------------------------------------
- Backend: Flask (Python)
- Database: SQLite (Native, created programmatically)
- Frontend: HTML, CSS, Jinja2 Templates


HOW TO RUN THE APPLICATION
--------------------------------------------------

1. Prerequisites
   Ensure you have Python installed on your system.

2. Installation
   Navigate to the project folder in your terminal/command prompt and 
   install the required package:
   
   pip install Flask

3. Running the App
   Run the main application file:
   
   python app.py

   The application will start on http://127.0.0.1:5000/


DATABASE SETUP
--------------------------------------------------
The SQLite database (hospital.db) is created programmatically and 
automatically when you run the app for the first time. 
You do NOT need to create it manually.


LOGIN CREDENTIALS
--------------------------------------------------

1. Admin (Pre-configured)
   - Username: admin
   - Password: admin123
   (Note: Use this account to create Doctor profiles first)

2. Doctor
   - Doctors must be created by the Admin via the Admin Dashboard.
   - Once created, use the username and password set by the Admin to log in.

3. Patient
   - Patients can register themselves via the "Register" link on the login page.


KEY FEATURES
--------------------------------------------------
- Admin: Dashboard with stats, manage doctors/patients, split view for 
  upcoming/past appointments, blacklist users.

- Doctor: Manage availability (dynamic 7-day grid), view assigned patients, 
  complete or cancel appointments.

- Patient: Search for doctors by name/department, book appointments via 
  availability grid, view medical history.