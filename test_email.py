#!/usr/bin/env python
"""Test appointment confirmation email sending"""
import os
import sys
from app import create_app
from model import db, Patient, Appointment, Doctor
from datetime import date, time
from flask_mail import Mail, Message

app = create_app()

with app.app_context():
    mail = Mail(app)
    
    print("\n=== Email Configuration Check ===")
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
    
    # Get a recent appointment
    appointment = Appointment.query.order_by(Appointment.id.desc()).first()
    
    if not appointment:
        print("\n❌ No appointments found in database")
        sys.exit(1)
    
    print(f"\n=== Testing Email Send ===")
    print(f"Appointment ID: {appointment.id}")
    print(f"Patient ID: {appointment.patient_id}")
    print(f"Doctor ID: {appointment.doctor_id}")
    
    patient = Patient.query.get(appointment.patient_id)
    doctor = Doctor.query.get(appointment.doctor_id)
    user = patient.user if patient else None
    
    if not user:
        print(f"❌ User not found for patient {appointment.patient_id}")
        sys.exit(1)
    
    email = user.email
    print(f"Patient Email: {email}")
    
    if not email:
        print(f"❌ No email address for user")
        sys.exit(1)
    
    try:
        doctor_name = doctor.full_name if doctor else 'Your Doctor'
        apt_date = appointment.date.strftime("%B %d, %Y") if appointment.date else 'TBD'
        apt_time = appointment.time.strftime('%I:%M %p') if appointment.time else 'TBD'
        
        msg = Message(
            subject='Appointment Confirmation - Zencura HMS',
            recipients=[email],
            html=f"""
            <html>
            <body style="font-family: Arial; background-color: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #14b8a6; margin-top: 0;">Appointment Confirmed!</h2>
                <p>Dear {patient.full_name},</p>
                <p>Your appointment has been successfully booked. Here are your appointment details:</p>
                <div style="background-color: #f0fdf4; border-left: 4px solid #14b8a6; padding: 15px; margin: 20px 0;">
                    <p><strong>Appointment ID:</strong> #{appointment.id}</p>
                    <p><strong>Date:</strong> {apt_date}</p>
                    <p><strong>Time:</strong> {apt_time}</p>
                    <p><strong>Doctor:</strong> Dr. {doctor_name}</p>
                    <p><strong>Status:</strong> {appointment.status}</p>
                </div>
                <p style="color: #666; font-size: 14px; margin-top: 20px;">
                    <strong>Important:</strong> Please arrive 10 minutes early to your appointment. 
                    If you need to reschedule or cancel, please do so at least 24 hours in advance.
                </p>
                <p>Thank you for choosing Zencura Hospital!</p>
            </div>
            </body>
            </html>
            """
        )
        
        print(f"\n📧 Sending email to: {email}")
        mail.send(msg)
        print(f"✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()
