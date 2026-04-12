from backend.core.celery_worker import celery_app
from backend.models import db, Appointment, Patient, Doctor, User
import logging
import os
from flask_mail import Mail, Message
log_file = os.path.join(os.path.dirname(__file__), "..", "reminders.log")
logger = logging.getLogger("zen_reminders")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(handler)

@celery_app.task(
    name="backend.tasks.send_appointment_confirmation.send_confirmation_email",
    bind=True,
    max_retries=3,
)

def send_confirmation_email(self, appointment_id):
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            mail = Mail(app)
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return {"status": "error", "message": "Appointment not found"}
            patient = Patient.query.get(appointment.patient_id)
            doctor = Doctor.query.get(appointment.doctor_id)
            user = User.query.get(patient.user_id) if patient else None
            if not user or not user.email:
                logger.error(f"No email for patient {appointment.patient_id}")
                return {"status": "error", "message": "No email address"}
            doctor_name = doctor.full_name if doctor else "Your Doctor"
            apt_date = (
                appointment.date.strftime("%B %d, %Y") if appointment.date else "TBD"
            )
            apt_time = (
                appointment.time.strftime("%I:%M %p") if appointment.time else "TBD"
            )
            msg = Message(
                subject="Appointment Confirmation - Zencura HMS",
                recipients=[user.email],
                html=f"""
                <html>
                <body style="font-family: Arial; background-color: 
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h2 style="color: 
                    <p>Dear {patient.full_name},</p>
                    <p>Your appointment has been successfully booked. Here are your appointment details:</p>
                    <div style="background-color: 
                        <p><strong>Appointment ID:</strong> 
                        <p><strong>Date:</strong> {apt_date}</p>
                        <p><strong>Time:</strong> {apt_time}</p>
                        <p><strong>Doctor:</strong> Dr. {doctor_name}</p>
                        <p><strong>Status:</strong> {appointment.status}</p>
                    </div>
                    <p style="color: 
                        <strong>Important:</strong> Please arrive 10 minutes early to your appointment. 
                        If you need to reschedule or cancel, please do so at least 24 hours in advance.
                    </p>
                    <p>Thank you for choosing Zencura Hospital!</p>
                    <p style="color: 
                        Zencura Hospital Management System
                    </p>
                </div>
                </body>
                </html>
                """,
            )
            mail.send(msg)
            logger.info(
                f"Confirmation email sent to {user.email} for appointment {appointment_id}"
            )
            return {
                "status": "success",
                "email": user.email,
                "appointment_id": appointment_id,
            }
    except Exception as e:
        logger.error(
            f"Error sending confirmation email for appointment {appointment_id}: {str(e)}"
        )
        return {"status": "error", "message": str(e)}
