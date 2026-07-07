import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_prescription_pdf(record):
    buffer = io.BytesIO()
    
    # Create the document shell
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#D9A08B'), # Primary Rose
        spaceAfter=6
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#3A322F')
    )
    
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#789B8C'), # Accent Teal
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#3A322F'),
        spaceAfter=4
    )

    # 1. Clinic Header
    story.append(Paragraph("BloomCare Clinic", title_style))
    story.append(Paragraph("123 Wellness Way, Floor 2 • gyne@bloomcare.com", meta_style))
    story.append(Spacer(1, 15))
    
    # 2. Patient / Doctor info table
    patient_name = record.patient.get_full_name()
    visit_date = record.visit_date.strftime("%B %d, %Y")
    doctor_name = f"Dr. {record.doctor.get_full_name()}"
    
    info_data = [
        [Paragraph(f"<b>Patient:</b> {patient_name}", meta_style), Paragraph(f"<b>Date:</b> {visit_date}", meta_style)],
        [Paragraph(f"<b>Age/DOB:</b> {record.patient.patient_profile.date_of_birth or 'N/A'}", meta_style), Paragraph(f"<b>Prescription No:</b> #Rx-10{record.id}", meta_style)],
        [Paragraph(f"<b>Blood Group:</b> {record.patient.patient_profile.blood_group or 'N/A'}", meta_style), Paragraph(f"<b>Consultant:</b> {doctor_name}", meta_style)]
    ]
    
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FCFAF7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#ECE5DE')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECE5DE')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # 3. Vitals Section
    story.append(Paragraph("Clinical Vitals", section_title))
    vitals_data = [
        [
            Paragraph(f"<b>Weight:</b> {record.weight_kg or 'N/A'} kg", meta_style),
            Paragraph(f"<b>Blood Pressure:</b> {record.blood_pressure or 'N/A'}", meta_style),
            Paragraph(f"<b>Temp:</b> {record.temperature_f or 'N/A'} F", meta_style),
            Paragraph(f"<b>Heart Rate:</b> {record.heart_rate_bpm or 'N/A'} bpm", meta_style)
        ]
    ]
    vitals_table = Table(vitals_data, colWidths=[130, 130, 130, 130])
    vitals_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAF4EE')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#ECE5DE')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(vitals_table)
    story.append(Spacer(1, 15))
    
    # 4. Diagnostics & Symptoms
    story.append(Paragraph("Examination Details", section_title))
    story.append(Paragraph(f"<b>Symptoms Logged:</b> {record.symptoms or 'None logged.'}", body_style))
    story.append(Paragraph(f"<b>Clinical Diagnosis:</b> {record.diagnosis or 'Under evaluation.'}", body_style))
    story.append(Spacer(1, 10))
    
    # 5. Rx Medicines
    story.append(Paragraph("Rx (Pharmacotherapy Instructions)", section_title))
    
    rx_content = record.prescription_medicines or "No specific medicines logged."
    story.append(Paragraph(rx_content.replace('\n', '<br/>'), body_style))
    
    if record.prescription_dosage:
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>Instructions:</b> {record.prescription_dosage}", body_style))
        
    story.append(Spacer(1, 35))
    
    # 6. Doctor Signature
    sig_data = [
        ["", ""],
        ["", f"_____________________________\nDr. {record.doctor.get_full_name()}\nElectronic Signature Verified"]
    ]
    sig_table = Table(sig_data, colWidths=[300, 220])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1,1), (1,1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('FONTNAME', (1,1), (1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (1,1), (1,1), 9),
    ]))
    story.append(sig_table)
    
    # Build Document
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()
