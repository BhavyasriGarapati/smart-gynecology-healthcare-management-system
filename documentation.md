# Documentation: Smart Gynecology Healthcare Management System (BloomCare)

Welcome to the documentation for **BloomCare Hospital's Smart Gynecology Healthcare Management System**. This is a complete Django 5 production-ready healthcare management workspace designed to lower patient anxiety using spa-like aesthetic colors.

---

## 1. Technical Architecture & Architecture Design

The application is built on **Django 5** and **Bootstrap 5**, storing data in a decoupled **SQLite 3** relational database.

### Database Schema Models (`core/models.py`)

1. **`User` (Custom AbstractUser)**:
   - Extends Django's base Auth User to support role choices: `PATIENT`, `DOCTOR`, or `ADMIN`.
2. **`DoctorProfile`**:
   - Holds doctor age, credentials, department selection (Obstetrics, Fertility, etc.), working days, slot hours, and custom registration details.
   - Exposes a dynamic method `calculate_age_based_fee(patient_age)` implementing age-specific rates.
3. **`PatientProfile`**:
   - Stores patient profile Gmail.
4. **`Appointment`**:
   - Stores consultation vitals (Blood group, Height, Weight, Age, Symptoms), target Doctor, Date, Time Slot, and Status (`Pending`, `Accepted`, `In Progress`, `Completed`, `Cancelled`).
5. **`LaboratoryTest`** & **`PrescribedMedicine`**:
   - Support back-end clinical prescription logs ordered by specialist doctors.

---

## 2. Dynamic Portals & Features

### A. Patient Portal
* **Registration**: Register with Full Name, Gmail, and Password. Displays a success notification modal.
* **Custom Sign-In**: Login using *Full Name* and *Password*.
* **Symptom Checker**: Evaluates selected symptoms against specialist departments (e.g. Obstetrics for Pregnancy) to recommend available gynecologists.
* **Appointment Booking**: Requests time slots by logging diagnostic vitals.

### B. Doctor Portal
* **Registration**: Profiles qualifications, work hours, department mapping, and photo.
* **Specialist Login**: Verifies Doctor Name, Specialization, Department, and Password.
* **Workspace Dashboard**: Split into:
  1. *Today's Appointments*: Immediate list of scheduled slots with status controls (Accept, In Progress, Complete).
  2. *Pending Cases*: Active patient list with worksheets (Notes, Lab Test Orders, Pharmacy Prescription entries).
  3. *Completed Cases*: History archive of completed consultations.

### C. Admin Portal
* **Custom Login**: Authenticates using standard Django superuser credentials (no hardcoded defaults).
* **Database Console**: View, delete, and search across registered patient profiles, specialists, and active appointments using clean tables-only grid layouts.
* **Directory Drill-down**: Click *View Records* or *View Profile* to view detailed patient medical logs or doctor clinical details.

---

## 3. UI/UX Style & Design Tokens (`style.css`)
Designed around a calming spa-like aesthetic:
* **Background Cream/Ivory (`#FAF7F2`)**: Replaces clinical clinical white.
* **Blush Rose Accent (`#D9A08B`)**: Warm, comforting primary color.
* **Sage Green Accent (`#789B8C`)**: Muted, natural tone for buttons and highlights.
* **Curved Layouts & Soft Shadows**: Rounded cards (`border-radius: 16px`) and gentle shadows to create a premium feel.

---

## 4. Setup & Running Instructions

1. **Install Dependencies**:
   ```bash
   pip install django pillow
   ```
2. **Apply Database Migrations**:
   ```bash
   python manage.py makemigrations core
   python manage.py migrate
   ```
3. **Create Custom Admin Credentials**:
   ```bash
   python manage.py createsuperuser
   ```
4. **Start the local server**:
   ```bash
   python manage.py runserver
   ```
