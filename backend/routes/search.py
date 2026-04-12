from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from backend.models import db, Doctor, Patient, User, Appointment
from backend.core.utils import success_response
from backend.core.cache_utils import cached_route
search_bp = Blueprint("search", __name__)

@search_bp.route("/api/search/doctors", methods=["GET"])

@jwt_required()

@cached_route(timeout=300)

def search_doctors():
    query = request.args.get("q", "").strip().lower()
    department = request.args.get("department", None)
    if not query or len(query) < 2:
        return success_response([])
    search_filter = or_(
        Doctor.full_name.ilike(f"%{query}%"),
        Doctor.qualification.ilike(f"%{query}%"),
        Doctor.experience.ilike(f"%{query}%"),
    )
    doctors_query = Doctor.query.join(User).filter(search_filter)
    if department:
        doctors_query = doctors_query.filter(Doctor.department_id == department)
    doctors = doctors_query.all()
    return success_response(
        [
            {
                "id": d.id,
                "full_name": d.full_name,
                "department": d.department.name if d.department else None,
                "qualification": d.qualification,
                "experience": d.experience,
                "contact": d.contact,
                "availability": d.availability,
            }
            for d in doctors
        ]
    )

@search_bp.route("/api/search/patients", methods=["GET"])

@jwt_required()

@cached_route(timeout=300)

def search_patients():
    query = request.args.get("q", "").strip().lower()
    if not query or len(query) < 2:
        return success_response([])
    search_filter = or_(
        Patient.full_name.ilike(f"%{query}%"),
        Patient.contact.ilike(f"%{query}%"),
    )
    patients = Patient.query.join(User).filter(search_filter).all()
    return success_response(
        [
            {
                "id": p.id,
                "full_name": p.full_name,
                "contact": p.contact,
                "email": p.user.email,
                "dob": p.dob.isoformat() if p.dob else None,
                "gender": p.gender,
                "blood_group": p.blood_group,
            }
            for p in patients
        ]
    )

@search_bp.route("/api/search/appointments", methods=["GET"])

@jwt_required()

def search_appointments():
    status = request.args.get("status", None)
    doctor_id = request.args.get("doctor_id", None)
    patient_id = request.args.get("patient_id", None)
    date_query = request.args.get("date", None)
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    if date_query:
        query = query.filter(Appointment.date == date_query)
    appointments = query.all()
    return success_response(
        [
            {
                "id": a.id,
                "patient_id": a.patient_id,
                "doctor_id": a.doctor_id,
                "date": a.date.isoformat(),
                "time": a.time.isoformat(),
                "status": a.status,
            }
            for a in appointments
        ]
    )
