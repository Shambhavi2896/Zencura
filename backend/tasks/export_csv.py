from backend.core.celery_worker import celery_app
from model import Appointment
import csv
import os
import time

@celery_app.task(name='backend.tasks.export_csv.generate_patient_export')
def generate_patient_export(patient_id):
    apts = Appointment.query.filter_by(patient_id=patient_id)\
        .order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    time.sleep(5)
    
    exports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    filename = f"patient_{patient_id}_history_{int(time.time())}.csv"
    filepath = os.path.join(exports_dir, filename)
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Record ID', 'Date', 'Time', 'Doctor', 'Department', 'Status', 'Diagnosis', 'Prescription', 'Notes', 'Next Visit'])
        
        for apt in apts:
            diag = apt.treatment.diagnosis if apt.treatment else ""
            presc = apt.treatment.prescription if apt.treatment else ""
            notes = apt.treatment.notes if apt.treatment else ""
            next_visit = apt.treatment.next_visit.isoformat() if apt.treatment and apt.treatment.next_visit else ""
            
            writer.writerow([
                apt.id,
                apt.date.isoformat(),
                apt.time.strftime('%H:%M'),
                apt.doctor.full_name,
                apt.doctor.department.name,
                apt.status,
                diag,
                presc,
                notes,
                next_visit
            ])
            
    return f"/static/exports/{filename}"
