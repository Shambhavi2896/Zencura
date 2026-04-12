


from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from datetime import date, datetime

from io import BytesIO

from reportlab.lib.pagesizes import letter, A4

from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.lib.units import inch

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from model import db, Appointment, Treatment, Payment, Doctor, Department

from sqlalchemy import extract



pdf_bp = Blueprint('pdf_export', __name__)





def is_admin():


    claims = get_jwt()

    return claims.get('role') == 'admin'





def generate_monthly_report_pdf(year, month):


    start_date = date(year, month, 1)

    if month == 12:

        end_date = date(year + 1, 1, 1)

    else:

        end_date = date(year, month + 1, 1)

    

    appointments = Appointment.query.filter(

        Appointment.date >= start_date,

        Appointment.date < end_date

    ).all()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    story = []

    

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(

        'CustomTitle',

        parent=styles['Heading1'],

        fontSize=24,

        textColor=colors.HexColor('#1e3a8a'),

        spaceAfter=6,

        alignment=TA_CENTER

    )

    heading_style = ParagraphStyle(

        'CustomHeading',

        parent=styles['Heading2'],

        fontSize=14,

        textColor=colors.HexColor('#003d61'),

        spaceAfter=12,

        spaceBefore=12

    )

    story.append(Paragraph("ZENCURA HOSPITAL MANAGEMENT", title_style))

    story.append(Paragraph(f"Monthly Activity Report - {start_date.strftime('%B %Y')}", heading_style))

    story.append(Spacer(1, 0.2*inch))

    total_apts = len(appointments)

    completed = sum(1 for a in appointments if a.status == 'Completed')

    booked = sum(1 for a in appointments if a.status == 'Booked')

    cancelled = sum(1 for a in appointments if a.status == 'Cancelled')

    

    revenue = db.session.query(db.func.sum(Payment.amount)).filter(

            Payment.status == 'Completed',

            extract('year', Payment.created_at) == year,

            extract('month', Payment.created_at) == month

        ).scalar() or 0.0

    

    summary_data = [

        ['Metric', 'Value'],

        ['Total Appointments', str(total_apts)],

        ['Completed', str(completed)],

        ['Booked', str(booked)],

        ['Cancelled', str(cancelled)],

        ['Total Revenue', f'${float(revenue):.2f}']

    ]

    

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])

    summary_table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('FONTSIZE', (0, 0), (-1, 0), 12),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

        ('GRID', (0, 0), (-1, -1), 1, colors.black)

    ]))

    

    story.append(summary_table)

    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("Department Performance", heading_style))

    

    dept_data = db.session.query(

        Department.name,

        db.func.count(Appointment.id).label('count')

    ).outerjoin(Doctor, Doctor.department_id == Department.id).outerjoin(Appointment, Appointment.doctor_id == Doctor.id).filter(

        Appointment.date >= start_date,

        Appointment.date < end_date

    ).group_by(Department.id, Department.name).all()

    

    dept_table_data = [['Department', 'Appointments']]

    for dept_name, count in dept_data:

        dept_table_data.append([dept_name or 'Unassigned', str(count or 0)])

    

    dept_table = Table(dept_table_data, colWidths=[3*inch, 2*inch])

    dept_table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#14b8a6')),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        ('GRID', (0, 0), (-1, -1), 1, colors.grey)

    ]))

    

    story.append(dept_table)

    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("Doctor Performance", heading_style))

    

    doc_data = db.session.query(

        Doctor.full_name,

        db.func.count(Appointment.id).label('count')

    ).join(Appointment, Appointment.doctor_id == Doctor.id).filter(

        Appointment.date >= start_date,

        Appointment.date < end_date

    ).group_by(Doctor.id, Doctor.full_name).order_by(db.func.count(Appointment.id).desc()).all()

    

    doc_table_data = [['Doctor', 'Appointments']]

    for doc_name, count in doc_data:

        doc_table_data.append([doc_name, str(count)])

    

    doc_table = Table(doc_table_data, colWidths=[3*inch, 2*inch])

    doc_table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        ('GRID', (0, 0), (-1, -1), 1, colors.grey)

    ]))

    

    story.append(doc_table)

    story.append(Spacer(1, 0.3*inch))

    footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Zencura HMS"

    story.append(Spacer(1, 0.5*inch))

    story.append(Paragraph(footer_text, ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))

    doc.build(story)

    buffer.seek(0)

    return buffer





@pdf_bp.route('/api/reports/export/monthly/<int:year>/<int:month>', methods=['GET'])

@jwt_required()

def export_monthly_pdf(year, month):


    if not is_admin():

        return jsonify(msg='Forbidden'), 403

    

    try:

        buffer = generate_monthly_report_pdf(year, month)

        filename = f"Monthly_Report_{year}_{month:02d}.pdf"

        

        return send_file(

            buffer,

            mimetype='application/pdf',

            as_attachment=True,

            download_name=filename

        )

    except Exception as e:

        return jsonify(msg=f'Error generating PDF: {str(e)}'), 500





@pdf_bp.route('/api/reports/export/summary', methods=['GET'])

@jwt_required()

def export_summary_pdf():


    if not is_admin():

        return jsonify(msg='Forbidden'), 403

    

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    story = []

    

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(

        'CustomTitle',

        parent=styles['Heading1'],

        fontSize=20,

        textColor=colors.HexColor('#1e3a8a'),

        spaceAfter=6,

        alignment=TA_CENTER

    )

    story.append(Paragraph("ZENCURA HOSPITAL MANAGEMENT", title_style))

    story.append(Paragraph(f"Summary Report - {date.today().strftime('%B %d, %Y')}", title_style))

    story.append(Spacer(1, 0.2*inch))

    total_doctors = db.session.query(db.func.count(Doctor.id)).scalar()

    total_appointments = Appointment.query.count()

    completed_appointments = Appointment.query.filter_by(status='Completed').count()

    pending_payments = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'Pending').scalar() or 0.0

    

    overview_data = [

        ['KPI', 'Value'],

        ['Total Doctors', str(total_doctors)],

        ['Total Appointments', str(total_appointments)],

        ['Completed Appointments', str(completed_appointments)],

        ['Pending Revenue', f'${float(pending_payments):.2f}']

    ]

    

    overview_table = Table(overview_data, colWidths=[3*inch, 2*inch])

    overview_table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('GRID', (0, 0), (-1, -1), 1, colors.black)

    ]))

    

    story.append(overview_table)

    doc.build(story)

    buffer.seek(0)

    

    filename = f"Summary_Report_{date.today().isoformat()}.pdf"

    return send_file(

        buffer,

        mimetype='application/pdf',

        as_attachment=True,

        download_name=filename

    )



