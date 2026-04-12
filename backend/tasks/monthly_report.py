from datetime import date
import logging
import os
from dateutil.relativedelta import relativedelta
from backend.core.celery_worker import celery_app
from backend.models import Appointment, Doctor, User, db
from flask_mail import Mail, Message
logger = logging.getLogger(__name__)

@celery_app.task(
    name="backend.tasks.monthly_report.generate_monthly_report",
    bind=True,
    max_retries=3,
)

def generate_monthly_report(self):
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            mail = Mail(app)
            
            today = date.today()
            first_day = today.replace(day=1)
            last_month_start = first_day - relativedelta(months=1)
            last_month_end = first_day - relativedelta(days=1)
            month_name = last_month_start.strftime("%B_%Y")
            
            doctors = Doctor.query.all()
            
            sent_count = 0
            for doctor in doctors:
                user = User.query.get(doctor.user_id)
                if not user or not user.email:
                    continue

                apts = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.date >= last_month_start,
                    Appointment.date <= last_month_end
                ).all()
                
                # If no data for last month, check this month (for testing convenience)
                if not apts:
                    this_month_start = today.replace(day=1)
                    apts = Appointment.query.filter(
                        Appointment.doctor_id == doctor.id,
                        Appointment.date >= this_month_start,
                        Appointment.date <= today
                    ).all()
                
                total_apts = len(apts)
                
                if total_apts == 0:
                    continue
                    
                completed_apts = sum(1 for a in apts if a.status == "Completed")
                completion_rate = round((completed_apts / max(total_apts, 1) * 100), 1)

                revenue = 0.0
                billing_rows = ""
                for a in apts:
                    if a.status == "Completed" and a.treatment:
                        diag = a.treatment.diagnosis
                        presc = a.treatment.prescription
                        payment_status = "Unpaid"
                        amount = 0.0
                        if a.treatment.payment:
                            amount = a.treatment.payment.amount
                            if a.treatment.payment.status == "Completed" or a.treatment.payment.status == "Paid":
                                revenue += amount
                            payment_status = a.treatment.payment.status
                        
                        billing_rows += f"<tr><td>{a.patient.full_name}</td><td>{a.date.strftime('%b %d, %Y')}</td><td>{diag}</td><td>{presc}</td><td>Rs. {amount:,.2f}</td></tr>"
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Monthly Activity Report - {month_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        h1 {{ text-align: center; color: #1e3a8a; margin-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
        th {{ background: #f8fafc; color: #475569; text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; font-size: 0.85rem; text-transform: uppercase; }}
        td {{ padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }}
        .metrics {{ display: flex; justify-content: space-between; gap: 20px; margin-top: 30px; }}
        .metric-card {{ background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 10px; flex: 1; text-align: center; }}
        .metric-value {{ font-size: 28px; font-weight: bold; color: #14b8a6; display: block; }}
        .metric-label {{ font-size: 13px; color: #64748b; text-transform: uppercase; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Monthly Activity Report - Dr. {doctor.full_name}</h1>
        <p style="text-align: center; color: #64748b; margin-top: 0;">Practice Summary for {last_month_start.strftime('%B %Y')}</p>
        
        <div class="metrics">
            <div class="metric-card">
                <span class="metric-value">{total_apts}</span>
                <span class="metric-label">Total Appointments</span>
            </div>
            <div class="metric-card">
                <span class="metric-value">{completed_apts}</span>
                <span class="metric-label">Completed ({completion_rate}%)</span>
            </div>
            <div class="metric-card">
                <span class="metric-value">Rs. {revenue:,.0f}</span>
                <span class="metric-label">Revenue Generated</span>
            </div>
        </div>
        <h2 style="margin-top: 40px; font-size: 1.2rem; color: #334155;">Patient Cases & Treatments</h2>
        <table>
            <thead><tr><th>Patient</th><th>Date</th><th>Diagnosis</th><th>Treatments</th><th>Cost</th></tr></thead>
            <tbody>
                {billing_rows or '<tr><td colspan="5" style="text-align: center; color: #94a3b8; padding: 40px;">No completed cases recorded in this period</td></tr>'}
            </tbody>
        </table>
        <p style="text-align: center; margin-top: 50px; color: #94a3b8; font-size: 12px;">Automated Report generated by Zencura Hospital Management System v2.0</p>
    </div>
</body>
</html>
"""
                msg = Message(
                    subject=f"Monthly Activity Report - {last_month_start.strftime('%B %Y')}",
                    recipients=[user.email],
                    html=html
                )
                mail.send(msg)
                logger.info(f"Sent monthly report to Dr. {doctor.full_name} at {user.email}")
                sent_count += 1
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "static", "reports")
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            archive_filename = f"Hospital_Summary_{month_name}.html"
            archive_path = os.path.join(reports_dir, archive_filename)
            summary_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Zencura Global Summary - {month_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; padding: 40px; }}
        .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center; }}
        h1 {{ color: #1e3a8a; }}
        .timestamp {{ font-size: 14px; color: #94a3b8; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Global Hospital Monthly Report Hub</h1>
        <p>This archive contains the activity overview for {last_month_start.strftime('%B %Y')}.</p>
        <div class="timestamp">Generated on {today.strftime('%B %d, %Y')}</div>
    </div>
</body>
</html>
"""
            with open(archive_path, "w", encoding="utf-8") as f:
                f.write(summary_html)
                
        return {"status": "success", "msg": f"Sent {sent_count} monthly reports successfully"}
        
    except Exception as error:
        logger.error(f"Report generation failed: {error}")
        return {"status": "error", "message": str(error)}
