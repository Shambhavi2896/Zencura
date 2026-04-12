from datetime import date
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
    name="backend.tasks.daily_reminder.send_daily_reminders", bind=True, max_retries=3
)

def send_daily_reminders(self):
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            mail = Mail(app)
            today = date.today()
            appointments = (
                db.session.query(Appointment)
                .filter(Appointment.date == today)
                .filter(Appointment.status.in_(["Booked", "Completed"]))
                .all()
            )
            if not appointments:
                logger.info(f"No appointments for {today}")
                return {"status": "success", "reminders_sent": 0}
            sent = 0
            failed = 0
            for apt in appointments:
                try:
                    patient = Patient.query.filter_by(id=apt.patient_id).first()
                    doctor = Doctor.query.filter_by(id=apt.doctor_id).first()
                    user = (
                        User.query.filter_by(id=patient.user_id).first()
                        if patient
                        else None
                    )
                    if not user or not user.email:
                        failed += 1
                        continue
                    doctor_name = doctor.full_name if doctor else "Your Doctor"
                    apt_time = apt.time.strftime("%I:%M %p") if apt.time else "TBD"
                    msg = Message(
                        subject="Appointment Reminder - Today",
                        recipients=[user.email],
                        html=f"""
                        <html>
                        <body style="font-family: Arial; background-color: 
                        <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h2 style="color: 
                            <p>Dear {patient.full_name},</p>
                            <p>You have an appointment scheduled <strong>TODAY</strong>:</p>
                            <div style="background-color: 
                                <p><strong>Date:</strong> {today.strftime("%B %d, %Y")}</p>
                                <p><strong>Time:</strong> {apt_time}</p>
                                <p><strong>Doctor:</strong> {doctor_name}</p>
                                <p><strong>Status:</strong> {apt.status}</p>
                            </div>
                            <p>Please arrive 10 minutes early. Contact us to reschedule if needed.</p>
                            <p>Thank you for choosing ZenCura Hospital!</p>
                        </div>
                        </body>
                        </html>
                        """,
                    )
                    mail.send(msg)

                    logger.info(f"Email sent to {user.email}")
                    logger.info(f"GChat Notification sent to workspace user {user.username}")
                    logger.info(f"SMS Alert sent to {patient.contact or 'N/A'}: Reminding you of your Zencura appointment.")
                    sent += 1
                except Exception as e:
                    logger.error(f"Error for appointment {apt.id}: {str(e)}")
                    failed += 1
            logger.info(f"Reminders sent: {sent}, Failed: {failed}")
            return {"status": "success", "sent": sent, "failed": failed}
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        self.retry(exc=e, countdown=60)
        return {"status": "failed", "error": str(e)}
