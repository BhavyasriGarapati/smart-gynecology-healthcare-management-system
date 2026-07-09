from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Portals Registration and Logins
    path('register/patient/', views.patient_register, name='patient_register'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Forgot Password Flow
    path('login/patient/forgot-password/', views.patient_forgot_password, name='patient_forgot_password'),
    path('login/patient/reset-password/', views.patient_reset_password, name='patient_reset_password'),
    
    # Router
    path('dashboard/', views.dashboard_router, name='dashboard'),
    
    # Patient Dashboard Routes
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/patient/profile/', views.patient_profile, name='patient_profile'),
    path('dashboard/patient/symptom-checker/', views.patient_symptom_checker, name='patient_symptom_checker'),
    path('dashboard/patient/recommendation/', views.patient_doctor_recommendation, name='patient_doctor_recommendation'),
    path('dashboard/patient/book-appointment/', views.patient_book_appointment, name='patient_book_appointment'),
    path('dashboard/patient/appointment-tracking/', views.patient_appointment_tracking, name='patient_appointment_tracking'),
    path('dashboard/patient/review/<int:appointment_id>/', views.patient_write_review, name='patient_write_review'),
    
    # Doctor Dashboard Routes
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/doctor/appointment/<int:pk>/status/<str:status>/', views.doctor_appointments_status, name='doctor_appointments_status'),
    path('dashboard/doctor/patient-records/', views.doctor_patient_records, name='doctor_patient_records'),
    path('dashboard/doctor/medical-notes/<int:appointment_id>/', views.doctor_medical_notes, name='doctor_medical_notes'),
    path('dashboard/doctor/lab-prescription/<int:appointment_id>/', views.doctor_lab_prescription, name='doctor_lab_prescription'),
    path('dashboard/doctor/upload-lab-report/<int:test_id>/', views.doctor_upload_lab_report, name='doctor_upload_lab_report'),
    path('dashboard/doctor/prescription/<int:appointment_id>/', views.doctor_prescription, name='doctor_prescription'),
    
    # Admin Dashboard Routes
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/delete-user/<int:pk>/', views.admin_delete_user, name='admin_delete_user'),
    path('dashboard/admin/delete-appointment/<int:pk>/', views.admin_delete_appointment, name='admin_delete_appointment'),
    path('dashboard/admin/patient/<int:pk>/', views.admin_patient_detail, name='admin_patient_detail'),
    path('dashboard/admin/doctor/<int:pk>/', views.admin_doctor_detail, name='admin_doctor_detail'),
    path('dashboard/admin/doctor/<int:pk>/status/<str:status>/', views.admin_doctor_status, name='admin_doctor_status'),
    path('dashboard/admin/appointment/<int:pk>/status/<str:status>/', views.admin_appointment_status, name='admin_appointment_status'),
    path('dashboard/admin/appointment/<int:pk>/assign/', views.admin_assign_patient, name='admin_assign_patient'),
    
    # Custom Portals & Pages
    path('login/admin/', views.admin_login, name='admin_login'),
]
