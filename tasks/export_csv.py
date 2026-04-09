from celery_worker import celery_app
from model import Appointment
import csv
import os
import time

@celery_app.task(name='tasks.export_csv.generate_patient_export')
def generate_patient_export(patient_id):
    # Retrieve all appointments for the patient 
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    # Introduce an artificial sleep of 5 seconds to demonstrate async UI loaders
    time.sleep(5)
    
    exports_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    filename = f"patient_{patient_id}_history_{int(time.time())}.csv"
    file_path = os.path.join(exports_dir, filename)
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write Headers
        writer.writerow(['Record ID', 'Date', 'Time', 'Doctor', 'Department', 'Status', 'Diagnosis', 'Prescription', 'Notes', 'Next Visit'])
        
        # Write rows
        for apt in appointments:
            t_diag = apt.treatment.diagnosis if apt.treatment else ""
            t_presc = apt.treatment.prescription if apt.treatment else ""
            t_notes = apt.treatment.notes if apt.treatment else ""
            t_next = apt.treatment.next_visit.isoformat() if apt.treatment and apt.treatment.next_visit else ""
            
            writer.writerow([
                apt.id,
                apt.date.isoformat(),
                apt.time.strftime('%H:%M'),
                apt.doctor.full_name,
                apt.doctor.department.name,
                apt.status,
                t_diag,
                t_presc,
                t_notes,
                t_next
            ])
            
    # Return the URL path to the generated file
    return f"/static/exports/{filename}"
