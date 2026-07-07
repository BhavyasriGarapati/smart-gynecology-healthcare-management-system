# Smart Gynecology Healthcare Management System (BloomCare)

A web-based platform tailored for modern obstetrics and gynecology healthcare. It is designed using **Django 5**, **Bootstrap 5**, and a custom **Spa-Like Organic Wellness Palette** to help lower patient anxiety.

The project code is cleanly organized into separated directories for academic and student recognition:
- `/backend/` - Django source files, views, models, forms, and core application modules.
- `/frontend/` - Static files (CSS/JS) and HTML templates containing the spa-like aesthetics.
- `/database/` - Stores the SQLite database file (`db.sqlite3`).
- `/documentation/` - Comprehensive system documentation, SRS report, and setup manuals.

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher.
- Pip (Python Package Installer).

### 2. Set Up the Project
Open your terminal/command prompt and navigate to the project directory:

```bash
cd smart_gynecology_system
```

### 3. Run Migrations
Run the standard Django database migrations to set up schema mapping inside your SQLite database:
```bash
cd backend
python manage.py migrate
```

### 4. Create Your Admin Credentials
To ensure full security, the database does **not** contain hardcoded default credentials. Create your own custom administrator account manually:
```bash
python manage.py createsuperuser
```
Follow the prompts in your terminal to specify your username, email, and password.

### 5. Start the Server
Run the local development server:
```bash
python manage.py runserver
```

Once running, open your web browser and navigate to:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Creating Staff and Doctors
1. Log in to the system database admin site at: [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)
2. Navigate to **Users** -> **Add User**.
3. Create accounts for your staff, selecting their appropriate roles:
   - `DOCTOR` (Gynecologist Specialist)
   - `NURSE` (Clinical Nurse)
   - `RECEPTIONIST` (Administrative Front Desk)
   - `PATIENT` (Regular Patient)
4. For Doctor profiles, remember to create a corresponding **Doctor Profile** entry in the admin interface to define specialization, fee, and available hours.
