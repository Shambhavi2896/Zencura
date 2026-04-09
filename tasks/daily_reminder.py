from celery_worker import celery_app
from model import Appointment
from datetime import date
import logging
import os

# Set up local logger for mock external requests
log_file = os.path.join(os.path.dirname(__file__), '..', 'reminders.log')
logger = logging.getLogger('zen_reminders')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(handler)

@celery_app.task(name='tasks.daily_reminder.send_reminders')
def send_reminders():
    today = date.today()
    # Find all Booked appointments for today
    upcoming = Appointment.query.filter_by(date=today, status='Booked').all()
    
    sent_count = 0
    for apt in upcoming:
        try:
            # Logic to send SMS/Email/GChat goes here using external APIs.
            # We mock the interaction by logging it.
            message = f"Reminder: {apt.patient.full_name}, you have an appointment with {apt.doctor.full_name} today at {apt.time.strftime('%H:%M')}."
            logger.info(f"SENT TO [{apt.patient.contact} / {apt.patient.user.email}]: {message}")
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send reminder to patient ID {apt.patient_id}: {str(e)}")

    return f"Successfully sent {sent_count} reminders for {today}"
