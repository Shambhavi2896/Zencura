import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, date, timedelta
from sqlalchemy import extract
from backend.models import db, Appointment, Treatment, Payment, Doctor, Patient, Department
from backend.core.utils import error_response, success_response
reports_bp = Blueprint("reports", __name__)

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

def get_month_range(target_date):
    start_date = date(target_date.year, target_date.month, 1)
    if target_date.month == 12:
        end_date = date(target_date.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)
    return start_date, end_date

def get_report_archives():
    reports_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "static", "reports"
    )
    if not os.path.exists(reports_dir):
        return []
    archives = []
    for filename in os.listdir(reports_dir):
        if filename.endswith(".html"):
            archives.append(
                {
                    "name": filename,
                    "url": f"/static/reports/{filename}",
                }
            )
    archives.sort(key=lambda item: item["name"], reverse=True)
    return archives

@reports_bp.route("/api/reports/analytics/appointments", methods=["GET"])

@jwt_required()

def analytics_appointments():
    if not is_admin():
        return error_response("Forbidden", 403)
    days = int(request.args.get("days", 30))
    start_date = date.today() - timedelta(days=days)
    daily_data = (
        db.session.query(
            Appointment.date,
            db.func.count(Appointment.id).label("count"),
            db.func.sum(db.case((Appointment.status == "Completed", 1), else_=0)).label(
                "completed"
            ),
        )
        .filter(Appointment.date >= start_date)
        .group_by(Appointment.date)
        .order_by(Appointment.date)
        .all()
    )
    dates = [d[0].isoformat() for d in daily_data]
    counts = [d[1] for d in daily_data]
    completed = [d[2] or 0 for d in daily_data]
    status_counts = (
        db.session.query(
            Appointment.status, db.func.count(Appointment.id).label("count")
        )
        .filter(Appointment.date >= start_date)
        .group_by(Appointment.status)
        .all()
    )
    status_labels = [s[0] for s in status_counts]
    status_data = [s[1] for s in status_counts]
    dept_data = (
        db.session.query(Department.name, db.func.count(Appointment.id).label("count"))
        .join(Doctor, Doctor.department_id == Department.id)
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.date >= start_date)
        .group_by(Department.id, Department.name)
        .order_by(db.func.count(Appointment.id).desc())
        .all()
    )
    dept_labels = [d[0] for d in dept_data]
    dept_counts = [d[1] for d in dept_data]
    return success_response(
        {
            "daily_trends": {
                "dates": dates,
                "appointments": counts,
                "completed": completed,
            },
            "status_breakdown": {"labels": status_labels, "data": status_data},
            "department_demand": {"labels": dept_labels, "data": dept_counts},
            "summary": {
                "total_appointments": sum(counts),
                "completed_appointments": sum(completed),
                "average_per_day": round(sum(counts) / max(len(counts), 1), 1),
            },
        }
    )

@reports_bp.route("/api/reports/analytics/treatments", methods=["GET"])

@jwt_required()

def analytics_treatments():
    if not is_admin():
        return error_response("Forbidden", 403)
    days = int(request.args.get("days", 30))
    start_date = date.today() - timedelta(days=days)
    doctor_stats = (
        db.session.query(
            Doctor.full_name,
            db.func.count(Treatment.id).label("count"),
            db.func.avg(db.case((Payment.status == "Completed", 1), else_=0)).label(
                "payment_rate"
            ),
        )
        .outerjoin(Appointment, Appointment.doctor_id == Doctor.id)
        .outerjoin(Treatment, Treatment.appointment_id == Appointment.id)
        .outerjoin(Payment, Payment.treatment_id == Treatment.id)
        .filter(Treatment.created_at >= start_date * 1 if start_date else True)
        .group_by(Doctor.id, Doctor.full_name)
        .order_by(db.func.count(Treatment.id).desc())
        .all()
    )
    doctor_names = [d[0] for d in doctor_stats]
    treatment_counts = [d[1] or 0 for d in doctor_stats]
    payment_rates = [round((d[2] or 0) * 100, 1) for d in doctor_stats]
    return success_response(
        {
            "doctors": {
                "names": doctor_names,
                "treatment_counts": treatment_counts,
                "payment_completion_rates": payment_rates,
            },
            "total_treatments": sum(treatment_counts),
            "average_treatments_per_doctor": round(
                sum(treatment_counts) / max(len(doctor_names), 1), 1
            ),
        }
    )

@reports_bp.route("/api/reports/monthly/<int:year>/<int:month>", methods=["GET"])

@jwt_required()

def monthly_report(year, month):
    if not is_admin():
        return error_response("Forbidden", 403)
    try:
        start_date = date(year, month, 1)
    except ValueError:
        return error_response("Invalid year or month", 400)
    _, end_date = get_month_range(start_date)
    appointments = Appointment.query.filter(
        Appointment.date >= start_date, Appointment.date <= end_date
    ).all()
    revenue_data = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(
            Payment.status == "Completed",
            extract("year", Payment.created_at) == year,
            extract("month", Payment.created_at) == month,
        )
        .scalar()
        or 0.0
    )
    pending_revenue = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(
            Payment.status == "Pending",
            extract("year", Payment.created_at) == year,
            extract("month", Payment.created_at) == month,
        )
        .scalar()
        or 0.0
    )
    payment_status = (
        db.session.query(
            Payment.status,
            db.func.count(Payment.id).label("count"),
            db.func.sum(Payment.amount).label("amount"),
        )
        .filter(
            extract("year", Payment.created_at) == year,
            extract("month", Payment.created_at) == month,
        )
        .group_by(Payment.status)
        .all()
    )
    doc_performance = (
        db.session.query(
            Doctor.full_name,
            Department.name,
            db.func.count(Appointment.id).label("appointments"),
        )
        .join(Department, Department.id == Doctor.department_id)
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.date >= start_date, Appointment.date <= end_date)
        .group_by(Doctor.id, Doctor.full_name, Department.name)
        .order_by(db.func.count(Appointment.id).desc())
        .all()
    )
    department_breakdown = (
        db.session.query(
            Department.name,
            db.func.count(Appointment.id).label("appointments"),
            db.func.sum(db.case((Appointment.status == "Completed", 1), else_=0)).label(
                "completed"
            ),
        )
        .join(Doctor, Doctor.department_id == Department.id)
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.date >= start_date, Appointment.date <= end_date)
        .group_by(Department.id, Department.name)
        .order_by(db.func.count(Appointment.id).desc())
        .all()
    )
    recent_billings = (
        db.session.query(Payment, Treatment, Appointment, Patient, Doctor)
        .join(Treatment, Payment.treatment_id == Treatment.id)
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .filter(
            extract("year", Payment.created_at) == year,
            extract("month", Payment.created_at) == month,
        )
        .order_by(Payment.created_at.desc())
        .limit(10)
        .all()
    )
    total_patients_seen = (
        db.session.query(Patient.id)
        .distinct()
        .join(Appointment, Appointment.patient_id == Patient.id)
        .filter(Appointment.date >= start_date, Appointment.date <= end_date)
        .count()
    )
    return success_response(
        {
            "month": start_date.strftime("%B %Y"),
            "metrics": {
                "total_appointments": len(appointments),
                "completed_appointments": sum(
                    1 for a in appointments if a.status == "Completed"
                ),
                "booked_appointments": sum(
                    1 for a in appointments if a.status == "Booked"
                ),
                "cancelled_appointments": sum(
                    1 for a in appointments if a.status == "Cancelled"
                ),
                "total_revenue": float(revenue_data),
                "pending_revenue": float(pending_revenue),
                "unique_patients": total_patients_seen,
            },
            "doctor_performance": [
                {
                    "name": name,
                    "department": department,
                    "appointments": appointments_count,
                }
                for name, department, appointments_count in doc_performance
            ],
            "payment_status": [
                {"status": status, "count": count, "amount": float(amount or 0.0)}
                for status, count, amount in payment_status
            ],
            "department_breakdown": [
                {
                    "name": name,
                    "appointments": appointments_count,
                    "completed": completed_count or 0,
                }
                for name, appointments_count, completed_count in department_breakdown
            ],
            "recent_billings": [
                {
                    "id": payment.id,
                    "patient": patient.full_name,
                    "doctor": doctor.full_name,
                    "amount": float(payment.amount),
                    "status": payment.status,
                    "created_at": (
                        payment.created_at.isoformat() if payment.created_at else None
                    ),
                    "diagnosis": treatment.diagnosis,
                    "appointment_date": appointment.date.isoformat(),
                }
                for payment, treatment, appointment, patient, doctor in recent_billings
            ],
        }
    )

@reports_bp.route("/api/reports/dashboard-summary", methods=["GET"])

@jwt_required()

def dashboard_summary():
    if not is_admin():
        return error_response("Forbidden", 403)
    today = date.today()
    this_month_start = date(today.year, today.month, 1)
    today_appointments = Appointment.query.filter(Appointment.date == today).count()
    today_revenue = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(
            Payment.status == "Completed", db.func.date(Payment.created_at) == today
        )
        .scalar()
        or 0.0
    )
    month_appointments = Appointment.query.filter(
        Appointment.date >= this_month_start, Appointment.date <= today
    ).count()
    month_revenue = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(
            Payment.status == "Completed",
            extract("year", Payment.created_at) == today.year,
            extract("month", Payment.created_at) == today.month,
        )
        .scalar()
        or 0.0
    )
    pending_revenue = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(Payment.status == "Pending")
        .scalar()
        or 0.0
    )
    pending_count = Payment.query.filter_by(status="Pending").count()
    top_doctors = (
        db.session.query(Doctor.full_name, db.func.count(Appointment.id).label("count"))
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.date >= this_month_start, Appointment.date <= today)
        .group_by(Doctor.id, Doctor.full_name)
        .order_by(db.func.count(Appointment.id).desc())
        .limit(5)
        .all()
    )
    return success_response(
        {
            "today": {
                "appointments": today_appointments,
                "revenue": float(today_revenue),
            },
            "this_month": {
                "appointments": month_appointments,
                "revenue": float(month_revenue),
            },
            "pending": {"revenue": float(pending_revenue), "count": pending_count},
            "top_doctors": [{"name": d[0], "appointments": d[1]} for d in top_doctors],
        }
    )

@reports_bp.route("/api/reports/overview", methods=["GET"])

@jwt_required()

def reports_overview():
    if not is_admin():
        return error_response("Forbidden", 403)
    today = date.today()
    month_start, month_end = get_month_range(today)
    trend_start = today - timedelta(days=5)
    appointments = Appointment.query.filter(
        Appointment.date >= month_start, Appointment.date <= month_end
    ).all()
    monthly_revenue = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(
            Payment.status == "Completed",
            extract("year", Payment.created_at) == today.year,
            extract("month", Payment.created_at) == today.month,
        )
        .scalar()
        or 0.0
    )
    pending_revenue = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(Payment.status == "Pending")
        .scalar()
        or 0.0
    )
    payment_status_rows = (
        db.session.query(
            Payment.status,
            db.func.count(Payment.id).label("count"),
            db.func.sum(Payment.amount).label("amount"),
        )
        .group_by(Payment.status)
        .all()
    )
    payment_status = [
        {
            "status": status,
            "count": count,
            "amount": float(amount or 0.0),
        }
        for status, count, amount in payment_status_rows
    ]
    department_rows = (
        db.session.query(
            Department.name,
            db.func.count(Appointment.id).label("appointments"),
            db.func.sum(db.case((Appointment.status == "Completed", 1), else_=0)).label(
                "completed"
            ),
        )
        .join(Doctor, Doctor.department_id == Department.id)
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.date >= month_start, Appointment.date <= month_end)
        .group_by(Department.id, Department.name)
        .order_by(db.func.count(Appointment.id).desc())
        .all()
    )
    doctor_rows = (
        db.session.query(
            Doctor.full_name,
            Department.name,
            db.func.count(Appointment.id).label("appointments"),
            db.func.sum(db.case((Appointment.status == "Completed", 1), else_=0)).label(
                "completed"
            ),
            db.func.sum(Payment.amount).label("revenue"),
        )
        .join(Department, Department.id == Doctor.department_id)
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .outerjoin(Treatment, Treatment.appointment_id == Appointment.id)
        .outerjoin(Payment, Payment.treatment_id == Treatment.id)
        .filter(Appointment.date >= month_start, Appointment.date <= month_end)
        .group_by(Doctor.id, Doctor.full_name, Department.name)
        .order_by(db.func.count(Appointment.id).desc())
        .limit(6)
        .all()
    )
    recent_payments_rows = (
        db.session.query(Payment, Treatment, Appointment, Patient, Doctor)
        .join(Treatment, Payment.treatment_id == Treatment.id)
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .order_by(Payment.created_at.desc())
        .limit(8)
        .all()
    )
    daily_rows = (
        db.session.query(
            Appointment.date,
            db.func.count(Appointment.id).label("appointments"),
            db.func.sum(db.case((Appointment.status == "Completed", 1), else_=0)).label(
                "completed"
            ),
        )
        .filter(Appointment.date >= trend_start, Appointment.date <= today)
        .group_by(Appointment.date)
        .order_by(Appointment.date)
        .all()
    )
    trend_dates = []
    trend_appointments = []
    trend_completed = []
    date_dict = {}
    for i in range(6):
        d = trend_start + timedelta(days=i)
        date_dict[d] = {"count": 0, "completed": 0}
    for row_date, count, completed in daily_rows:
        if type(row_date) == str:
            from datetime import datetime
            row_date = datetime.strptime(row_date, "%Y-%m-%d").date()
        if row_date in date_dict:
            date_dict[row_date]["count"] = count
            date_dict[row_date]["completed"] = completed
    for d in sorted(date_dict.keys()):
        trend_dates.append(d.strftime("%d %b"))
        trend_appointments.append(date_dict[d]["count"])
        trend_completed.append(date_dict[d]["completed"] or 0)
    report_generated = len(get_report_archives()) > 0
    return success_response(
        {
            "summary": {
                "month": today.strftime("%B %Y"),
                "appointments": len(appointments),
                "completed": sum(
                    1
                    for appointment in appointments
                    if appointment.status == "Completed"
                ),
                "cancelled": sum(
                    1
                    for appointment in appointments
                    if appointment.status == "Cancelled"
                ),
                "revenue": float(monthly_revenue),
                "pending_revenue": float(pending_revenue),
                "patients_seen": db.session.query(Patient.id)
                .join(Appointment, Appointment.patient_id == Patient.id)
                .filter(Appointment.date >= month_start, Appointment.date <= month_end)
                .distinct()
                .count(),
                "report_generated": report_generated,
            },
            "daily_trend": {
                "labels": trend_dates,
                "appointments": trend_appointments,
                "completed": trend_completed,
            },
            "payment_status": payment_status,
            "departments": [
                {
                    "name": name,
                    "appointments": appointments_count,
                    "completed": completed_count or 0,
                }
                for name, appointments_count, completed_count in department_rows
            ],
            "top_doctors": [
                {
                    "name": doctor_name,
                    "department": department_name,
                    "appointments": appointments_count,
                    "completed": completed_count or 0,
                    "revenue": float(revenue or 0.0),
                }
                for doctor_name, department_name, appointments_count, completed_count, revenue in doctor_rows
            ],
            "recent_payments": [
                {
                    "id": payment.id,
                    "patient": patient.full_name,
                    "doctor": doctor.full_name,
                    "amount": float(payment.amount),
                    "status": payment.status,
                    "created_at": (
                        payment.created_at.isoformat() if payment.created_at else None
                    ),
                    "appointment_date": appointment.date.isoformat(),
                    "diagnosis": treatment.diagnosis,
                }
                for payment, treatment, appointment, patient, doctor in recent_payments_rows
            ],
            "archives": get_report_archives(),
        }
    )
