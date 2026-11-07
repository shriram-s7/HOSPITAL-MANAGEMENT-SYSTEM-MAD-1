# Hospital Management System (MAD 1)

A server-rendered hospital management web app built with **Flask** and **SQLite** for the IITM BS *Modern Application Development 1* course. It lets an admin manage doctors and patients, lets doctors publish availability and record treatments, and lets patients find doctors and book appointments.

## What it does

| Role | Capabilities |
|---|---|
| **Admin** (pre-created) | Dashboard with counts; add, edit and search doctors and patients; blacklist users; view upcoming and past appointments |
| **Doctor** (created by admin) | Set availability on a 7-day slot grid; see assigned appointments; mark them complete (with diagnosis, prescription and notes) or cancel; view a patient's history |
| **Patient** (self-registers) | Register and log in; search doctors by name or department; book from the availability grid; cancel; view own treatment history; edit profile |

## Stack

- Python 3 and Flask (blueprints: `auth`, `admin`, `doctor`, `patient`)
- SQLite through the standard `sqlite3` module; tables are created automatically on first run (`users`, `doctors`, `patients`, `appointments`, `treatments`, `availability`, `blacklist`)
- Jinja2 templates in `templates/`, CSS in `static/`
- API description in `api.yaml`

## Run it

```bash
pip install Flask
python app.py
```

Open http://127.0.0.1:5000/. The database file `hospital.db` is created on first start.

On first run the app creates an `admin` account (the default password is set in `database.py`); change it for any real use. Create doctors from the admin dashboard, then log in as them. Patients register from the login page.

## Project layout

```
app.py        Flask app factory and blueprint registration
auth.py       login, register, logout
admin.py      admin dashboard, doctor/patient management, blacklist
doctor.py     availability, appointments, treatment records
patient.py    doctor search, booking, history, profile
database.py   schema creation and DB helpers
utils.py      small helpers
templates/    Jinja2 pages
static/       stylesheet
api.yaml      API description
project_report.pdf   course project report
```

The demo video (`24F3004661_MAD1_VIDEO.mp4`) is kept locally and is not part of the repository.

## Notes

- Passwords are hashed with Werkzeug. This is still a coursework project without production hardening (default admin password, Flask development server), so do not deploy it as is.
