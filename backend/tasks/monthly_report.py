from datetime import date
import logging
import os

from dateutil.relativedelta import relativedelta
from sqlalchemy import extract

from backend.core.celery_worker import celery_app
from model import Appointment, Department, Doctor, Patient, Payment, Treatment, db

logger = logging.getLogger(__name__)


@celery_app.task(name='backend.tasks.monthly_report.generate_monthly_report', bind=True, max_retries=3)
def generate_monthly_report(self):
    try:
        today = date.today()
        first_day = today.replace(day=1)
        last_month_start = first_day - relativedelta(months=1)
        last_month_end = first_day - relativedelta(days=1)
        month_name = last_month_start.strftime("%B_%Y")

        reports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        total_apts = Appointment.query.filter(
            Appointment.date >= last_month_start,
            Appointment.date <= last_month_end,
        ).count()

        completed_apts = Appointment.query.filter(
            Appointment.date >= last_month_start,
            Appointment.date <= last_month_end,
            Appointment.status == 'Completed',
        ).count()

        revenue = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.status == 'Completed',
            extract('year', Payment.created_at) == last_month_start.year,
            extract('month', Payment.created_at) == last_month_start.month,
        ).scalar() or 0.0

        pending_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.status == 'Pending',
            extract('year', Payment.created_at) == last_month_start.year,
            extract('month', Payment.created_at) == last_month_start.month,
        ).scalar() or 0.0

        unique_patients = db.session.query(Patient.id).join(
            Appointment, Appointment.patient_id == Patient.id
        ).filter(
            Appointment.date >= last_month_start,
            Appointment.date <= last_month_end,
        ).distinct().count()

        dept_stats = db.session.query(
            Department.name,
            db.func.count(Appointment.id).label('count'),
        ).outerjoin(Doctor, Doctor.department_id == Department.id)\
         .outerjoin(Appointment, Appointment.doctor_id == Doctor.id)\
         .filter(Appointment.date >= last_month_start, Appointment.date <= last_month_end)\
         .group_by(Department.id, Department.name).all()

        top_doctors = db.session.query(
            Doctor.full_name,
            db.func.count(Appointment.id).label('count'),
        ).join(Appointment, Appointment.doctor_id == Doctor.id)\
         .filter(Appointment.date >= last_month_start, Appointment.date <= last_month_end)\
         .group_by(Doctor.id, Doctor.full_name)\
         .order_by(db.func.count(Appointment.id).desc())\
         .limit(10).all()

        payment_stats = db.session.query(
            Payment.status,
            db.func.count(Payment.id).label('count'),
            db.func.sum(Payment.amount).label('amount'),
        ).filter(
            extract('year', Payment.created_at) == last_month_start.year,
            extract('month', Payment.created_at) == last_month_start.month,
        ).group_by(Payment.status).all()

        billing_rows_data = db.session.query(
            Payment, Treatment, Appointment, Patient, Doctor
        ).join(Treatment, Payment.treatment_id == Treatment.id)\
         .join(Appointment, Treatment.appointment_id == Appointment.id)\
         .join(Patient, Appointment.patient_id == Patient.id)\
         .join(Doctor, Appointment.doctor_id == Doctor.id)\
         .filter(
            extract('year', Payment.created_at) == last_month_start.year,
            extract('month', Payment.created_at) == last_month_start.month,
         ).order_by(Payment.created_at.desc()).limit(8).all()

        dept_rows = ''.join(
            f'<tr><td>{name or "Unassigned"}</td><td>{count}</td><td>{round((count / max(total_apts, 1) * 100), 1)}%</td></tr>'
            for name, count in dept_stats
        )

        doc_rows = ''.join(
            f'<tr><td>{name}</td><td>{count}</td><td>{round((count / max(total_apts, 1) * 100), 1)}%</td></tr>'
            for name, count in top_doctors
        )

        payment_rows = ''.join(
            f'<tr><td>{status}</td><td>{count}</td><td>Rs. {float(amount or 0.0):,.2f}</td></tr>'
            for status, count, amount in payment_stats
        )

        billing_rows = ''.join(
            f'<tr><td>{patient.full_name}</td><td>{doctor.full_name}</td><td>{treatment.diagnosis}</td><td>Rs. {float(payment.amount):,.2f}</td><td>{payment.status}</td></tr>'
            for payment, treatment, appointment, patient, doctor in billing_rows_data
        )

        completion_rate = round((completed_apts / max(total_apts, 1) * 100), 1)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Monthly Report - {month_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #eef4f8; color: #163047; }}
        .container {{ max-width: 1080px; margin: 0 auto; background: white; padding: 34px; }}
        h1 {{ color: #163047; text-align: center; margin-bottom: 10px; letter-spacing: 0.04em; }}
        h2 {{ color: #197f71; margin-top: 32px; margin-bottom: 15px; border-bottom: 2px solid #bde5df; padding-bottom: 10px; }}
        .lead {{ text-align: center; color: #64748b; margin-bottom: 28px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 30px; }}
        .metric-card {{ background: linear-gradient(135deg, #1f9d8b, #15665a); color: white; padding: 20px; border-radius: 14px; text-align: center; }}
        .metric-value {{ font-size: 30px; font-weight: bold; }}
        .metric-label {{ font-size: 14px; margin-top: 10px; opacity: 0.9; }}
        .split {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 24px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th {{ background: #197f71; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; vertical-align: top; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .summary-box {{ background: #f6f9fb; border: 1px solid #dbe5ec; border-radius: 14px; padding: 18px; margin-bottom: 16px; }}
        .summary-box p {{ margin: 0 0 10px; color: #40586e; }}
        .footer {{ text-align: center; color: #666; margin-top: 40px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ZENCURA HOSPITAL MANAGEMENT</h1>
        <p class="lead">Monthly Report for {last_month_start.strftime('%B %Y')}</p>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{total_apts}</div>
                <div class="metric-label">Total Appointments</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{completed_apts}</div>
                <div class="metric-label">Completed Visits</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">Rs. {revenue:,.0f}</div>
                <div class="metric-label">Collected Revenue</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{completion_rate}%</div>
                <div class="metric-label">Completion Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{unique_patients}</div>
                <div class="metric-label">Patients Seen</div>
            </div>
        </div>

        <div class="split">
            <div>
                <h2>Department Performance</h2>
                <table>
                    <tr><th>Department</th><th>Appointments</th><th>Percentage</th></tr>
                    {dept_rows or '<tr><td colspan="3">No department data available</td></tr>'}
                </table>
            </div>
            <div>
                <h2>Payment Summary</h2>
                <div class="summary-box">
                    <p><strong>Collected Revenue:</strong> Rs. {float(revenue):,.2f}</p>
                    <p><strong>Pending Revenue:</strong> Rs. {float(pending_revenue):,.2f}</p>
                    <p><strong>Report Window:</strong> {last_month_start.isoformat()} to {last_month_end.isoformat()}</p>
                </div>
                <table>
                    <tr><th>Status</th><th>Transactions</th><th>Amount</th></tr>
                    {payment_rows or '<tr><td colspan="3">No payment entries available</td></tr>'}
                </table>
            </div>
        </div>

        <h2>Top Performing Doctors</h2>
        <table>
            <tr><th>Doctor Name</th><th>Appointments</th><th>Percentage</th></tr>
            {doc_rows or '<tr><td colspan="3">No doctor performance data available</td></tr>'}
        </table>

        <h2>Recent Billing Activity</h2>
        <table>
            <tr><th>Patient</th><th>Doctor</th><th>Diagnosis</th><th>Amount</th><th>Status</th></tr>
            {billing_rows or '<tr><td colspan="5">No billing activity captured for this month</td></tr>'}
        </table>

        <div class="footer">
            <p>Generated on {date.today().strftime('%Y-%m-%d %H:%M:%S')} | Zencura HMS 2026</p>
            <p>Confidential - Internal Use Only</p>
        </div>
    </div>
</body>
</html>"""

        report_file = f"Monthly_Report_{month_name}.html"
        report_path = os.path.join(reports_dir, report_file)

        with open(report_path, 'w', encoding='utf-8') as file:
            file.write(html)

        logger.info(f'Report generated: {report_file}')
        return {'status': 'success', 'report': report_file}

    except Exception as error:
        logger.error(f'Report generation failed: {error}')
        return {'status': 'error', 'message': str(error)}
