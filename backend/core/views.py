from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from datetime import date, datetime
from django.db.models import Q

from .models import User, DoctorProfile, PatientProfile, Appointment, LaboratoryTest, PrescribedMedicine
from .forms import (
    PatientRegistrationForm, DoctorRegistrationForm, AppointmentBookingForm,
    LabPrescriptionForm, MedicinePrescriptionForm
)
from .utils import generate_prescription_pdf

# Home Page View
def home(request):
    doctors = DoctorProfile.objects.all()[:6] # display 6 doctors
    quotes = [
        "Caring today for a healthier tomorrow.",
        "Hope, Healing and Happiness begin with good health.",
        "Your health is our priority, caring with empathy.",
        "A healthy woman is the powerhouse of a healthy family.",
        "Empowering women through specialized, compassionate care."
    ]
    import random
    footer_quote = random.choice(quotes)
    return render(request, 'index.html', {'doctors': doctors, 'footer_quote': footer_quote})

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
            
            # Message trigger for popup
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
                profile_photo=form.cleaned_data['doctor_photo']
            )
            messages.success(request, "Registration Successful. Welcome Doctor.")
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
    return render(request, 'dashboards/patient_home.html')

@login_required
def patient_profile(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    return render(request, 'dashboards/patient_profile.html', {'profile': profile})

@login_required
def patient_symptom_checker(request):
    doctors = None
    selected_symptoms = []
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
            
        doctors = DoctorProfile.objects.filter(department=dept)
    return render(request, 'dashboards/patient_symptom_checker.html', {
        'doctors': doctors,
        'selected_symptoms': selected_symptoms,
        'symptoms_list': symptoms_list
    })

@login_required
def patient_doctor_recommendation(request):
    doctors = DoctorProfile.objects.all()
    return render(request, 'dashboards/patient_doctor_recommendation.html', {'doctors': doctors})

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
            appointment.save()
            messages.success(request, "Appointment Booked Successfully.")
            return redirect('patient_appointment_tracking')
    else:
        form = AppointmentBookingForm(initial={'doctor': selected_doctor})
    return render(request, 'dashboards/patient_book_appointment.html', {'form': form, 'selected_doctor': selected_doctor})

@login_required
def patient_appointment_tracking(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'dashboards/patient_appointment_tracking.html', {'appointments': appointments})

@login_required
def patient_lab_reports(request):
    appointments = Appointment.objects.filter(patient=request.user)
    lab_tests = LaboratoryTest.objects.filter(appointment__in=appointments).order_by('-prescribed_at')
    return render(request, 'dashboards/patient_lab_reports.html', {'reports': lab_tests})

@login_required
def patient_medicine_details(request):
    appointments = Appointment.objects.filter(patient=request.user, status='Completed')
    medicines = PrescribedMedicine.objects.filter(appointment__in=appointments)
    return render(request, 'dashboards/patient_medicine_details.html', {'medicines': medicines})

# Doctor Portal Views
@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor_role():
        return redirect('dashboard_router')
    profile = request.user.doctor_profile
    today = date.today()
    
    today_appointments = Appointment.objects.filter(doctor=profile, appointment_date=today).order_by('time_slot')
    pending_cases = Appointment.objects.filter(doctor=profile, status__in=['Pending', 'Accepted', 'In Progress']).order_by('-created_at')
    completed_cases = Appointment.objects.filter(doctor=profile, status='Completed').order_by('-created_at')
    
    return render(request, 'dashboards/doctor_home.html', {
        'today_appointments': today_appointments,
        'pending_cases': pending_cases,
        'completed_cases': completed_cases
    })

@login_required
def doctor_appointments_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user.doctor_profile)
    appointment.status = status
    if status == 'Completed':
        appointment.is_case_completed = True
        messages.success(request, "Case Completed.")
    elif status == 'Accepted':
        messages.success(request, "Appointment Accepted.")
    else:
        messages.success(request, f"Appointment status marked as {status}.")
        
    appointment.save()
    return redirect('doctor_dashboard')

@login_required
def doctor_patient_records(request):
    profile = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=profile).order_by('-created_at')
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
            messages.success(request, "Report Uploaded Successfully.")
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
            messages.success(request, "Medicine Added Successfully.")
            return redirect('doctor_prescription', appointment_id=appointment.id)
    else:
        form = MedicinePrescriptionForm()
        
    medicines = PrescribedMedicine.objects.filter(appointment=appointment)
    return render(request, 'dashboards/doctor_prescription.html', {
        'form': form,
        'appointment': appointment,
        'medicines': medicines
    })

# Custom Admin Dashboard (Tables Only)
@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
        
    search_q = request.GET.get('q', '')
    
    patients = PatientProfile.objects.all()
    doctors = DoctorProfile.objects.all()
    appointments = Appointment.objects.all().order_by('-created_at')
    lab_reports = LaboratoryTest.objects.all().order_by('-prescribed_at')
    prescriptions = PrescribedMedicine.objects.all().order_by('-prescribed_at')
    
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
        'lab_reports': lab_reports,
        'prescriptions': prescriptions,
        'search_q': search_q
    })

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

# Admin Portal Login View
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

# General Laboratory View
@login_required
def laboratory_page(request):
    search_q = request.GET.get('q', '')
    tests = LaboratoryTest.objects.all().order_by('-prescribed_at')
    if search_q:
        tests = tests.filter(Q(test_name__icontains=search_q) | Q(appointment__patient_name__icontains=search_q))
    return render(request, 'laboratory.html', {'tests': tests, 'search_q': search_q})

# General Pharmacy View
@login_required
def pharmacy_page(request):
    search_q = request.GET.get('q', '')
    medicines = PrescribedMedicine.objects.all().order_by('-prescribed_at')
    if search_q:
        medicines = medicines.filter(Q(medicine_name__icontains=search_q) | Q(appointment__patient_name__icontains=search_q))
    return render(request, 'pharmacy.html', {'medicines': medicines, 'search_q': search_q})

# Admin Patient Details
@login_required
def admin_patient_detail(request, pk):
    if not request.user.is_admin_role():
        return redirect('dashboard_router')
    patient = get_object_or_404(User, pk=pk, role='PATIENT')
    appointments = Appointment.objects.filter(patient=patient).order_by('-created_at')
    lab_reports = LaboratoryTest.objects.filter(appointment__in=appointments).order_by('-prescribed_at')
    prescriptions = PrescribedMedicine.objects.filter(appointment__in=appointments).order_by('-prescribed_at')
    return render(request, 'dashboards/admin_patient_detail.html', {
        'patient': patient,
        'appointments': appointments,
        'reports': lab_reports,
        'prescriptions': prescriptions
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

