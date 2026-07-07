from django import forms
from .models import User, DoctorProfile, PatientProfile, Appointment, LaboratoryTest, PrescribedMedicine

class PatientRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    gmail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Gmail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class DoctorRegistrationForm(forms.Form):
    doctor_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doctor Name'}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}))
    gmail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Gmail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    
    qualification = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Qualification'}))
    specialization = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialization'}))
    department = forms.ChoiceField(choices=DoctorProfile.department.field.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    experience = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Experience (Years)'}))
    hospital_name = forms.CharField(max_length=100, initial='BloomCare Hospital', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'}))
    work_timings = forms.CharField(max_length=100, initial='09:00 AM - 05:00 PM', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work Timings'}))
    working_days = forms.CharField(max_length=100, initial='Monday to Saturday', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Working Days'}))
    consultation_fees = forms.DecimalField(initial=500.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Base Consultation Fees'}))
    doctor_photo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'patient_name', 'age', 'blood_group', 'height', 'weight',
            'selected_symptom', 'doctor', 'appointment_date', 'time_slot', 'remarks'
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. O+'}),
            'height': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 165 cm'}),
            'weight': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 58 kg'}),
            'selected_symptom': forms.Select(choices=(
                ('Pregnancy', 'Pregnancy'),
                ('PCOS', 'PCOS'),
                ('Irregular Periods', 'Irregular Periods'),
                ('Heavy Bleeding', 'Heavy Bleeding'),
                ('Pelvic Pain', 'Pelvic Pain'),
                ('Fibroids', 'Fibroids'),
                ('Infertility', 'Infertility'),
                ('Menopause', 'Menopause'),
                ('Ovarian Cyst', 'Ovarian Cyst'),
                ('Endometriosis', 'Endometriosis'),
                ('White Discharge', 'White Discharge'),
                ('Severe Cramps', 'Severe Cramps'),
            ), attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(choices=(
                ('09:00 AM - 10:00 AM', '09:00 AM - 10:00 AM'),
                ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
                ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
                ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
                ('03:00 PM - 04:00 PM', '03:00 PM - 04:00 PM'),
                ('04:00 PM - 05:00 PM', '04:00 PM - 05:00 PM'),
            ), attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = DoctorProfile.objects.all()

class LabPrescriptionForm(forms.ModelForm):
    class Meta:
        model = LaboratoryTest
        fields = ['test_name']
        widgets = {
            'test_name': forms.Select(attrs={'class': 'form-select'}),
        }

class MedicinePrescriptionForm(forms.ModelForm):
    class Meta:
        model = PrescribedMedicine
        fields = ['medicine_name', 'purpose', 'dosage_morning', 'dosage_afternoon', 'dosage_night', 'duration']
        widgets = {
            'medicine_name': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. PCOS Management'}),
            'dosage_morning': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dosage_afternoon': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dosage_night': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5 days'}),
        }
