from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
import random

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT')

    def is_admin_role(self):
        return self.role == 'ADMIN' or self.is_superuser

    def is_doctor_role(self):
        return self.role == 'DOCTOR'

    def is_patient_role(self):
        return self.role == 'PATIENT'

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    age = models.PositiveIntegerField(default=35)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    department = models.CharField(max_length=100, choices=(
        ('General Gynecology', 'General Gynecology'),
        ('Obstetrics', 'Obstetrics'),
        ('Fertility & IVF', 'Fertility & IVF'),
        ('Gynecological Oncology', 'Gynecological Oncology'),
        ('Menopause Care', 'Menopause Care'),
    ), default='General Gynecology')
    experience = models.PositiveIntegerField(default=5)
    hospital_name = models.CharField(max_length=100, default='BloomCare Hospital')
    work_timings = models.CharField(max_length=100, default='09:00 AM - 05:00 PM')
    working_days = models.CharField(max_length=100, default='Monday to Saturday')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    profile_photo = models.ImageField(upload_to='doctors/', blank=True, null=True)

    def calculate_age_based_fee(self, patient_age):
        try:
            age = int(patient_age)
        except (ValueError, TypeError):
            return self.consultation_fee
            
        if age >= 1 and age <= 5:
            return 1500
        elif age >= 6 and age <= 10:
            return 2000
        elif age >= 11 and age <= 18:
            return 2500
        elif age >= 19 and age <= 40:
            return 3000
        elif age > 40:
            return 3500
        return self.consultation_fee

    def __str__(self):
        return f"Dr. {self.user.username} ({self.qualification})"

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    gmail = models.EmailField()

    def __str__(self):
        return f"Patient: {self.user.username}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    appointment_number = models.CharField(max_length=20, unique=True, blank=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'}, related_name='appointments_as_patient')
    patient_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    blood_group = models.CharField(max_length=10)
    height = models.CharField(max_length=20)
    weight = models.CharField(max_length=20)
    selected_symptom = models.CharField(max_length=100)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=50)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    doctor_notes = models.TextField(blank=True, null=True)
    is_case_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.appointment_number:
            self.appointment_number = f"APT{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.appointment_number} - {self.patient_name} with {self.doctor}"

class LaboratoryTest(models.Model):
    TEST_CHOICES = (
        ('Blood Test', 'Blood Test'),
        ('Urine Test', 'Urine Test'),
        ('Pregnancy Test', 'Pregnancy Test'),
        ('Hormone Test', 'Hormone Test'),
        ('Ultrasound Scan', 'Ultrasound Scan'),
        ('Pelvic Scan', 'Pelvic Scan'),
        ('Thyroid Test', 'Thyroid Test'),
        ('Blood Sugar Test', 'Blood Sugar Test'),
        ('Vitamin D Test', 'Vitamin D Test'),
        ('CBC Test', 'CBC Test'),
    )
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='lab_tests')
    test_name = models.CharField(max_length=50, choices=TEST_CHOICES)
    pdf_report = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    prescribed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Prescribed') # Prescribed, Uploaded

    def __str__(self):
        return f"{self.test_name} for {self.appointment.patient_name}"

class PrescribedMedicine(models.Model):
    MEDICINE_CHOICES = (
        ('Metformin', 'Metformin'),
        ('Letrozole', 'Letrozole'),
        ('Clomiphene', 'Clomiphene'),
        ('Folic Acid', 'Folic Acid'),
        ('Iron Tablets', 'Iron Tablets'),
        ('Calcium Tablets', 'Calcium Tablets'),
        ('Progesterone', 'Progesterone'),
        ('Dydrogesterone', 'Dydrogesterone'),
        ('Tranexamic Acid', 'Tranexamic Acid'),
        ('Ibuprofen', 'Ibuprofen'),
        ('Paracetamol', 'Paracetamol'),
        ('Prenatal Vitamins', 'Prenatal Vitamins'),
    )
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=50, choices=MEDICINE_CHOICES)
    purpose = models.CharField(max_length=150)
    dosage_morning = models.BooleanField(default=False)
    dosage_afternoon = models.BooleanField(default=False)
    dosage_night = models.BooleanField(default=False)
    duration = models.CharField(max_length=50) # e.g. "5 days", "1 month"
    prescribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} for {self.appointment.patient_name}"
