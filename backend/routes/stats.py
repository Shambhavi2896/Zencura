from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from backend.models import db, Doctor, Patient, Appointment, Department
from backend.core.cache import cache
stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/api/admin/stats", methods=["GET"])

@jwt_required()

def admin_stats():
    from backend.models import User
    from datetime import date
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify(msg="Forbidden"), 403
    
    print("DEBUG: Fetching admin stats from DB...")
    doctors_count = Doctor.query.count()
    patients_count = Patient.query.count()
    appointments_count = Appointment.query.count()
    print(f"DEBUG: Found {doctors_count} docs, {patients_count} pats, {appointments_count} apts")
    departments_count = Department.query.count()
    booked = Appointment.query.filter_by(status="Booked").count()
    completed = Appointment.query.filter_by(status="Completed").count()
    cancelled = Appointment.query.filter_by(status="Cancelled").count()
    blacklisted_docs = (
        db.session.query(Doctor).join(User).filter(User.is_active == False).count()
    )
    blacklisted_pats = (
        db.session.query(Patient).join(User).filter(User.is_active == False).count()
    )
    dept_stats = (
        db.session.query(Department.name, db.func.count(Appointment.id))
        .select_from(Department)
        .outerjoin(Doctor, Doctor.department_id == Department.id)
        .outerjoin(Appointment, Appointment.doctor_id == Doctor.id)
        .group_by(Department.name)
        .all()
    )
    chart_labels = [d[0] for d in dept_stats]
    chart_data = [d[1] for d in dept_stats]
    recent = (
        Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc())
        .limit(5)
        .all()
    )
    recent_list = []
    for a in recent:
        recent_list.append(
            {
                "id": a.id,
                "patient": a.patient.full_name,
                "doctor": a.doctor.full_name,
                "dept": a.doctor.department.name,
                "date": a.date.isoformat(),
                "time": a.time.isoformat(),
                "status": a.status,
            }
        )
    return (
        jsonify(
            doctors=doctors_count,
            patients=patients_count,
            appointments=appointments_count,
            departments=departments_count,
            booked=booked,
            completed=completed,
            cancelled=cancelled,
            blacklisted_docs=blacklisted_docs,
            blacklisted_pats=blacklisted_pats,
            chart_labels=chart_labels,
            chart_data=chart_data,
            recent=recent_list,
        ),
        200,
    )

@stats_bp.route("/api/doctor/stats", methods=["GET"])

@jwt_required()

def doctor_stats():
    from flask_jwt_extended import get_jwt_identity
    from backend.models import User
    from datetime import date
    user = User.query.get(int(get_jwt_identity()))
    if not user or not user.doctor_profile:
        return jsonify(msg="Forbidden"), 403
    doc = user.doctor_profile
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.status == "Booked",
        Appointment.date >= date.today(),
    ).count()
    patient_ids = (
        db.session.query(Appointment.patient_id)
        .filter(Appointment.doctor_id == doc.id)
        .distinct()
        .count()
    )
    return jsonify(upcoming=upcoming, patients=patient_ids), 200

@stats_bp.route("/api/patient/stats", methods=["GET"])

@jwt_required()

def patient_stats():
    from flask_jwt_extended import get_jwt_identity
    from backend.models import User
    from datetime import date
    user = User.query.get(int(get_jwt_identity()))
    if not user or not user.patient_profile:
        return jsonify(msg="Forbidden"), 403
    pat = user.patient_profile
    upcoming = Appointment.query.filter(
        Appointment.patient_id == pat.id,
        Appointment.status == "Booked",
        Appointment.date >= date.today(),
    ).count()
    completed = Appointment.query.filter(
        Appointment.patient_id == pat.id, Appointment.status == "Completed"
    ).count()
    departments = Department.query.count()
    return jsonify(upcoming=upcoming, completed=completed, departments=departments), 200
