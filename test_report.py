#!/usr/bin/env python
"""Test monthly report generation directly"""
import os
import sys
from app import create_app
from model import db, Appointment, Payment
from backend.tasks.monthly_report import generate_monthly_report

app = create_app()

with app.app_context():
    total_apts = Appointment.query.count()
    total_payments = Payment.query.count()
    total_dirs = len(os.listdir('frontend/static/reports'))
    
    print(f"\n=== Database Status ===")
    print(f"Total Appointments: {total_apts}")
    print(f"Total Payments: {total_payments}")
    print(f"Reports Directory: frontend/static/reports/")
    print(f"Files in reports dir: {total_dirs}")
    
    print(f"\n=== Running Monthly Report Task ===")
    
    try:
        result = generate_monthly_report()
        print(f"Task Result: {result}")
        
        # Check if file was created
        reports_dir = 'frontend/static/reports'
        files = os.listdir(reports_dir)
        print(f"\n=== After Task Execution ===")
        print(f"Files in reports dir: {len(files)}")
        if files:
            for f in files:
                print(f"  - {f}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
