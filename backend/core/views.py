from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from datetime import date, datetime
from django.db.models import Q
import random

from .models import User, DoctorProfile, PatientProfile, Appointment, LaboratoryTest, PrescribedMedicine, Review, Notification, OTPVerification
from .forms import (
    PatientRegistrationForm, DoctorRegistrationForm, AppointmentBookingForm,
    LabPrescriptionForm, MedicinePrescriptionForm, ReviewForm
)

# Helper function to create notification
def create_notification(user, message):
    Notification.objects.create(user=user, message=message)

# Home Page View
def home(request):
    doctors = DoctorProfile.objects.filter(approval_status='Approved')[:6] # display 6 approved doctors
    quotes = [
        "Caring today for a healthier tomorrow.",
        "Hope, Healing and Happiness begin with good health.",
        "Your health is our priority, caring with empathy.",
        "A healthy woman is the powerhouse of a healthy family.",
        "Empowering women through specialized, compassionate care."
    ]
    footer_quote = random.choice(quotes)
    
    # Fetch public reviews: latest first
    public_reviews = Review.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'index.html', {
        'doctors': doctors,
        'footer_quote': footer_quote,
        'public_reviews': public_reviews
    })

# Patient Auth Portals
def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            gmail = form.cleaned_data['gmail']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=full_name).exists():
                messages.error(request, "A patient with this name already exists.")
                return render(request, 'register_patient.html', {'form': form})
                
            user = User.objects.create_user(username=full_name, email=gmail, password=password, role='PATIENT')
            PatientProfile.objects.create(user=user, gmail=gmail)
            
            messages.success(request, "Registration Successful. Welcome to BloomCare.")
            return redirect('patient_login')
    else:
        form = PatientRegistrationForm()
    return render(request, 'register_patient.html', {'form': form})

def patient_login(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        user = authenticate(username=full_name, password=password)
        if user is not None and user.role == 'PATIENT':
            login(request, user)
            messages.success(request, "Login Successful. Welcome to Patient Portal.")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Invalid Full Name or Password.")
    return render(request, 'login_patient.html')

# Forgot Password Functionality for Patient
def patient_forgot_password(request):
    if request.method == 'POST':
        gmail = request.POST.get('gmail')
        # Check if patient exists with this gmail
        try:
            profile = PatientProfile.objects.get(gmail=gmail)
            # Generate simulated OTP
            otp_val = str(random.randint(100000, 999999))
            OTPVerification.objects.filter(gmail=gmail).delete()
            OTPVerification.objects.create(gmail=gmail, otp=otp_val)
            
            # Output OTP in standard messages for simulator purposes
            messages.success(request, f"Verification OTP sent to {gmail}. (Simulated OTP: {otp_val})")
            return redirect(f"/login/patient/reset-password/?gmail={gmail}")
        except PatientProfile.DoesNotExist:
            messages.error(request, "No registered patient account found with this Gmail.")
    return render(request, 'forgot_password_patient.html')

def patient_reset_password(request):
    gmail = request.GET.get('gmail', '')
    if request.method == 'POST':
        gmail = request.POST.get('gmail')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'reset_password_patient.html', {'gmail': gmail})
            
        try:
            verification = OTPVerification.objects.get(gmail=gmail, otp=otp)
            # Update password
            profile = PatientProfile.objects.get(gmail=gmail)
            user = profile.user
            user.set_password(new_password)
            user.save()
            verification.delete()
            
            messages.success(request, "Password updated successfully. Please login again.")
            return redirect('patient_login')
        except OTPVerification.DoesNotExist:
            messages.error(request, "Invalid OTP or Verification details.")
            
    return render(request, 'reset_password_patient.html', {'gmail': gmail})

# Doctor Auth Portals
def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            doc_name = form.cleaned_data['doctor_name']
            gmail = form.cleaned_data['gmail']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=doc_name).exists():
                messages.error(request, "A doctor with this name already exists.")
                return render(request, 'register_doctor.html', {'form': form})
                
            user = User.objects.create_user(username=doc_name, email=gmail, password=password, role='DOCTOR')
            # Doctor account starts as Pending Approval
            DoctorProfile.objects.create(
                user=user,
                age=form.cleaned_data['age'],
                qualification=form.cleaned_data['qualification'],
                specialization=form.cleaned_data['specialization'],
                department=form.cleaned_data['department'],
                experience=form.cleaned_data['experience'],
                hospital_name=form.cleaned_data['hospital_name'],
                work_timings=form.cleaned_data['work_timings'],
                working_days=form.cleaned_data['working_days'],
                consultation_fee=form.cleaned_data['consultation_fees'],
                profile_photo=form.cleaned_data['doctor_photo'],
                approval_status='Pending'
            )
            
            # Send notification to admins
            admins = User.objects.filter(role='ADMIN')
            for admin in admins:
                create_notification(admin, f"New Doctor Registration: Dr. {doc_name} is pending approval.")
                
            messages.success(request, "Registration Successful. Welcome Doctor. Your account is pending admin approval.")
            return redirect('doctor_login')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'register_doctor.html', {'form': form})

def doctor_login(request):
    if request.method == 'POST':
        doctor_name = request.POST.get('doctor_name')
        department = request.POST.get('department')
        specialization = request.POST.get('specialization')
        password = request.POST.get('password')
        
        user = authenticate(username=doctor_name, password=password)
        if user is not None and user.role == 'DOCTOR':
            profile = user.doctor_profile
            # Verify admin approval status
            if profile.approval_status != 'Approved':
                messages.error(request, f"Your doctor account is not approved. Status: {profile.approval_status}")
                return render(request, 'login_doctor.html', {'departments': DoctorProfile.department.field.choices})
                
            if profile.department == department and profile.specialization == specialization:
                login(request, user)
                messages.success(request, "Welcome Doctor.")
                return redirect('doctor_dashboard')
            else:
                messages.error(request, "Department or Specialization details do not match.")
        else:
            messages.error(request, "Invalid Credentials.")
    return render(request, 'login_doctor.html', {'departments': DoctorProfile.department.field.choices})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

@login_required
def dashboard_router(request):
    if request.user.is_admin_role():
        return redirect('admin_dashboard')
    elif request.user.is_doctor_role():
        return redirect('doctor_dashboard')
    else:
        return redirect('patient_dashboard')

# Patient Portal Views
@login_required
def patient_dashboard(request):
    if not request.user.is_patient_role():
        return redirect('dashboard_router')
    # Fetch notifications for patient
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # "My Doctor Status" section
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    
    return render(request, 'dashboards/patient_home.html', {
        'notifications': notes,
        'appointments': appointments
    })

@login_required
def patient_profile(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    return render(request, 'dashboards/patient_profile.html', {'profile': profile})

@login_required
def patient_symptom_checker(request):
    doctors = None
    selected_symptoms = []
    sort_by = request.GET.get('sort_by', 'rating')
    
    symptoms_list = [
        'Pregnancy', 'PCOS', 'Irregular Periods', 'Heavy Bleeding', 
        'Pelvic Pain', 'Fibroids', 'Infertility', 'Menopause', 
        'Ovarian Cyst', 'Endometriosis', 'White Discharge', 'Severe Cramps'
    ]
    if request.method == 'POST':
        symptoms = request.POST.getlist('symptoms')
        selected_symptoms = symptoms
        
        # Mapping symptoms to departments
        dept = 'General Gynecology'
        if any(s in symptoms for s in ['Pregnancy']):
            dept = 'Obstetrics'
        elif any(s in symptoms for s in ['PCOS', 'Infertility']):
            dept = 'Fertility & IVF'
        elif any(s in symptoms for s in ['Heavy Bleeding', 'Pelvic Pain', 'Fibroids', 'Endometriosis']):
            dept = 'Gynecological Oncology'
        elif any(s in symptoms for s in ['Menopause']):
            dept = 'Menopause Care'
            
        doctors_qs = DoctorProfile.objects.filter(department=dept, approval_status='Approved')
        
        # Sort doctors based on selection
        if sort_by == 'rating':
            doctors = sorted(doctors_qs, key=lambda d: d.average_rating, reverse=True)
        elif sort_by == 'experience':
            doctors = doctors_qs.order_by('-experience')
        elif sort_by == 'earliest_slot':
            # Available first
            doctors = sorted(doctors_qs, key=lambda d: 0 if d.status == 'Available' else 1)
        elif sort_by == 'waiting_time':
            # Lowest waiting time
            doctors = sorted(doctors_qs, key=lambda d: 0 if d.status == 'Available' else 1)
            
    return render(request, 'dashboards/patient_symptom_checker.html', {
        'doctors': doctors,
        'selected_symptoms': selected_symptoms,
        'symptoms_list': symptoms_list,
        'sort_by': sort_by
    })

@login_required
def patient_doctor_recommendation(request):
    sort_by = request.GET.get('sort_by', 'rating')
    doctors_qs = DoctorProfile.objects.filter(approval_status='Approved')
    
    if sort_by == 'rating':
        doctors = sorted(doctors_qs, key=lambda d: d.average_rating, reverse=True)
    elif sort_by == 'experience':
        doctors = doctors_qs.order_by('-experience')
    elif sort_by == 'earliest_slot':
        doctors = sorted(doctors_qs, key=lambda d: 0 if d.status == 'Available' else 1)
    else:
        doctors = doctors_qs
        
    return render(request, 'dashboards/patient_doctor_recommendation.html', {
        'doctors': doctors,
        'sort_by': sort_by
    })

@login_required
def patient_book_appointment(request):
    doctor_id = request.GET.get('doctor_id')
    selected_doctor = None
    if doctor_id:
        selected_doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
        
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'Pending'
            
            # Admin approval required first before appearing on doctor dashboard
            appointment.admin_approved = 'Pending'
            
            # Doctor Schedule Management Checks (one patient per 30-min slot)
            existing_apt = Appointment.objects.filter(
                doctor=appointment.doctor,
                appointment_date=appointment.appointment_date,
                time_slot=appointment.time_slot
            ).exclude(status='Cancelled')
            
            if existing_apt.exists():
                messages.error(request, "This slot is unavailable. Please choose another available time.")
                return render(request, 'dashboards/patient_book_appointment.html', {'form': form, 'selected_doctor': selected_doctor})
                
            # If Doctor is Busy/Emergency Surgery
            if appointment.doctor.status == 'Busy':
                messages.error(request, "The doctor is currently unavailable. We will contact you shortly.")
                # We can save it but set message accordingly
                appointment.doctor_message = "The doctor is currently unavailable. We will contact you shortly."
                
            appointment.save()
            messages.success(request, "Appointment Booked. Awaiting Admin Approval.")
            return redirect('patient_appointment_tracking')
    else:
        form = AppointmentBookingForm(initial={'doctor': selected_doctor})
    return render(request, 'dashboards/patient_book_appointment.html', {'form': form, 'selected_doctor': selected_doctor})

@login_required
def patient_appointment_tracking(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'dashboards/patient_appointment_tracking.html', {'appointments': appointments})

# Submit Review
@login_required
def patient_write_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, patient=request.user, status='Completed')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.patient = request.user
            review.doctor = appointment.doctor
            review.save()
            messages.success(request, "Review Submitted.")
            return redirect('patient_dashboard')
    else:
        form = ReviewForm()
    return render(request, 'dashboards/patient_write_review.html', {'form': form, 'appointment': appointment})

# Doctor Portal Views
@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor_role():
        return redirect('dashboard_router')
    profile = request.user.doctor_profile
    today = date.today()
    
    # Only list appointments approved by Admin
    today_appointments = Appointment.objects.filter(doctor=profile, appointment_date=today, admin_approved='Approved').order_by('time_slot')
    pending_cases = Appointment.objects.filter(doctor=profile, admin_approved='Approved', status__in=['Pending', 'Accepted', 'In Progress']).order_by('-created_at')
    completed_cases = Appointment.objects.filter(doctor=profile, status='Completed').order_by('-created_at')
    
    # Doctor Schedule Availability Statuses
    if request.method == 'POST':
        if 'toggle_emergency' in request.POST:
            profile.status = 'Emergency Surgery' if profile.status != 'Emergency Surgery' else 'Available'
            profile.save()
            
            # Postpone all remaining doctor appointments & notify affected patients
            if profile.status == 'Emergency Surgery':
                affected_apts = Appointment.objects.filter(doctor=profile, appointment_date=today, status__in=['Pending', 'Accepted', 'In Progress'])
                for apt in affected_apts:
                    apt.status = 'Cancelled'
                    apt.doctor_message = "The doctor is attending an emergency surgery. Your appointment has been temporarily postponed. Our team will contact you shortly."
                    apt.save()
                    create_notification(apt.patient, apt.doctor_message)
                messages.success(request, "Emergency Activated.")
                
        elif 'update_status' in request.POST:
            new_status = request.POST.get('doctor_status')
            profile.status = new_status
            profile.save()
            
            if new_status == 'Busy':
                messages.success(request, "Doctor Busy Mode Activated.")
            else:
                messages.success(request, f"Status updated to: {new_status}")
            
            # Notify patients if busy
            if new_status in ['Busy', 'On Leave']:
                apts = Appointment.objects.filter(doctor=profile, status='Pending')
                for apt in apts:
                    create_notification(apt.patient, "The doctor is currently unavailable. We will contact you shortly.")
                    
    return render(request, 'dashboards/doctor_home.html', {
        'today_appointments': today_appointments,
        'pending_cases': pending_cases,
        'completed_cases': completed_cases,
        'profile': profile
    })

@login_required
def doctor_appointments_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user.doctor_profile)
    appointment.status = status
    if status == 'Completed':
        appointment.is_case_completed = True
        create_notification(appointment.patient, f"Case Completed for Appt: {appointment.appointment_number}")
        messages.success(request, "Appointment Completed.")
    elif status == 'Accepted':
        appointment.doctor_message = "Your appointment has been approved. Please attend on time."
        create_notification(appointment.patient, appointment.doctor_message)
        messages.success(request, "Appointment Approved.")
    elif status == 'Rejected':
        appointment.doctor_message = "Doctor is unavailable today. Our team will contact you shortly."
        create_notification(appointment.patient, appointment.doctor_message)
        messages.success(request, "Appointment Rejected.")
        
    appointment.save()
    return redirect('doctor_dashboard')

@login_required
def doctor_patient_records(request):
    profile = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=profile, admin_approved='Approved').order_by('-created_at')
    return render(request, 'dashboards/doctor_patient_records.html', {'appointments': appointments})

@login_required
def doctor_medical_notes(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        notes = request.POST.get('doctor_notes')
        appointment.doctor_notes = notes
        appointment.save()
        messages.success(request, "Medical Notes Saved.")
        return redirect('doctor_dashboard')
    return render(request, 'dashboards/doctor_medical_notes.html', {'appointment': appointment})

@login_required
def doctor_lab_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        form = LabPrescriptionForm(request.POST)
        if form.is_valid():
            lab_test = form.save(commit=False)
            lab_test.appointment = appointment
            lab_test.status = 'Prescribed'
            lab_test.save()
            messages.success(request, "Laboratory Test Prescribed.")
            return redirect('doctor_dashboard')
    else:
        form = LabPrescriptionForm()
    
    tests = LaboratoryTest.objects.filter(appointment=appointment)
    return render(request, 'dashboards/doctor_lab_prescription.html', {
        'form': form,
        'appointment': appointment,
        'tests': tests
    })

@login_required
def doctor_upload_lab_report(request, test_id):
    lab_test = get_object_or_404(LaboratoryTest, pk=test_id)
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_report')
        if pdf_file:
            lab_test.pdf_report = pdf_file
            lab_test.status = 'Uploaded'
            lab_test.save()
            # Notify patient
            create_notification(lab_test.appointment.patient, f"Lab Report Uploaded for {lab_test.test_name}")
            messages.success(request, "Lab Report Uploaded.")
    return redirect('doctor_dashboard')

@login_required
def doctor_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        form = MedicinePrescriptionForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.appointment = appointment
            
            # Map default purposes
            medicine_purposes = {
                'Metformin': 'PCOS Management & Insulin Resistance',
                'Letrozole': 'Ovulation Induction',
                'Clomiphene': 'Fertility Treatment',
                'Folic Acid': 'Prenatal Neural Tube Protection',
                'Iron Tablets': 'Anemia Prevention & Blood Support',
                'Calcium Tablets': 'Bone Strength Support',
                'Progesterone': 'Hormonal Balance & Pregnancy Support',
                'Dydrogesterone': 'Menstrual Regulation & Progesterone Support',
                'Tranexamic Acid': 'Heavy Menstrual Bleeding Reduction',
                'Ibuprofen': 'Pain and Severe Cramps Relief',
                'Paracetamol': 'Pain and Fever Management',
                'Prenatal Vitamins': 'Maternal & Fetal Nutritional Supplementation'
            }
            medicine.purpose = medicine_purposes.get(medicine.medicine_name, medicine.purpose)
            medicine.save()
            
            # Notify Patient of prescription details
            create_notification(appointment.patient, "Prescription Uploaded.")
            messages.success(request, "Prescription Uploaded.")
            return redirect('doctor_prescription', appointment_id=appointment.id)
    else:
        form = MedicinePrescriptionForm()
        
    medicines = PrescribedMedicine.objects.filter(appointment=appointment)
    return render(request, 'dashboards/doctor_prescription.html', {
        'form': form,
        'appointment': appointment,
        'medicines': medicines
    })

# Custom Admin Dashboard
@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
        
    search_q = request.GET.get('q', '')
    
    patients = PatientProfile.objects.all()
    doctors = DoctorProfile.objects.all()
    appointments = Appointment.objects.all().order_by('-created_at')
    
    if search_q:
        patients = patients.filter(Q(user__username__icontains=search_q) | Q(gmail__icontains=search_q))
        doctors = doctors.filter(Q(user__username__icontains=search_q) | Q(specialization__icontains=search_q))
        appointments = appointments.filter(Q(patient_name__icontains=search_q) | Q(appointment_number__icontains=search_q))
        
    pending_cases = appointments.filter(status__in=['Pending', 'Accepted', 'In Progress'])
    completed_cases = appointments.filter(status='Completed')
    
    return render(request, 'dashboards/admin_home.html', {
        'patients': patients,
        'doctors': doctors,
        'appointments': appointments,
        'pending_cases': pending_cases,
        'completed_cases': completed_cases,
        'search_q': search_q
    })

# Admin Doctor Approvals
@login_required
def admin_doctor_status(request, pk, status):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    doctor.approval_status = status
    doctor.save()
    
    # Notify Doctor
    if status == 'Approved':
        create_notification(doctor.user, "Your account has been approved. You may now login.")
        messages.success(request, "Doctor Approved.")
    else:
        messages.success(request, f"Doctor status updated to: {status}")
        
    return redirect('admin_dashboard')

# Admin Appointment Approval & Assignment
@login_required
def admin_appointment_status(request, pk, status):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.admin_approved = status
    appointment.save()
    
    if status == 'Approved':
        # Automatically notify corresponding Doctor & Patient
        create_notification(appointment.doctor.user, f"New Patient Assigned: {appointment.patient_name}")
        create_notification(appointment.patient, "Appointment Approved")
        messages.success(request, "Appointment Approved.")
    else:
        create_notification(appointment.patient, "Appointment Rejected")
        messages.success(request, "Appointment Rejected.")
        
    return redirect('admin_dashboard')

@login_required
def admin_assign_patient(request, pk):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
        appointment.doctor = doctor
        appointment.save()
        create_notification(doctor.user, f"New Patient Assigned: {appointment.patient_name}")
        messages.success(request, "Patient Assigned successfully.")
    return redirect('admin_dashboard')

@login_required
def admin_delete_user(request, pk):
    if request.user.is_admin_role():
        user = get_object_or_404(User, pk=pk)
        user.delete()
        messages.success(request, "User account deleted successfully.")
    return redirect('admin_dashboard')

@login_required
def admin_delete_appointment(request, pk):
    if request.user.is_admin_role():
        appt = get_object_or_404(Appointment, pk=pk)
        appt.delete()
        messages.success(request, "Appointment deleted successfully.")
    return redirect('admin_dashboard')

# Admin Patient Details
@login_required
def admin_patient_detail(request, pk):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
    patient = get_object_or_404(User, pk=pk, role='PATIENT')
    appointments = Appointment.objects.filter(patient=patient).order_by('-created_at')
    return render(request, 'dashboards/admin_patient_detail.html', {
        'patient': patient,
        'appointments': appointments
    })

# Admin Doctor Details
@login_required
def admin_doctor_detail(request, pk):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-created_at')
    return render(request, 'dashboards/admin_doctor_detail.html', {
        'doctor': doctor,
        'appointments': appointments
    })

# Admin Login View
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and (user.role == 'ADMIN' or user.is_superuser):
            login(request, user)
            messages.success(request, "Login Successful. Welcome to Admin Portal.")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid Admin Credentials.")
    return render(request, 'login_admin.html')

