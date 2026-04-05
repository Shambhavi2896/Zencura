from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from model import db, Doctor, Patient, Appointment, Department

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify(msg='Forbidden'), 403

    return jsonify(
        doctors=Doctor.query.count(),
        patients=Patient.query.count(),
        appointments=Appointment.query.count()
    ), 200

@stats_bp.route('/api/doctor/stats', methods=['GET'])
@jwt_required()
def doctor_stats():
    from flask_jwt_extended import get_jwt_identity
    from model import User
    from datetime import date

    user = User.query.get(int(get_jwt_identity()))
    if not user or not user.doctor_profile:
        return jsonify(msg='Forbidden'), 403

    doc = user.doctor_profile
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.status == 'Booked',
        Appointment.date >= date.today()
    ).count()

    patient_ids = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doc.id
    ).distinct().count()

    return jsonify(upcoming=upcoming, patients=patient_ids), 200

@stats_bp.route('/api/patient/stats', methods=['GET'])
@jwt_required()
def patient_stats():
    from flask_jwt_extended import get_jwt_identity
    from model import User
    from datetime import date

    user = User.query.get(int(get_jwt_identity()))
    if not user or not user.patient_profile:
        return jsonify(msg='Forbidden'), 403

    pat = user.patient_profile
    upcoming = Appointment.query.filter(
        Appointment.patient_id == pat.id,
        Appointment.status == 'Booked',
        Appointment.date >= date.today()
    ).count()

    completed = Appointment.query.filter(
        Appointment.patient_id == pat.id,
        Appointment.status == 'Completed'
    ).count()

    departments = Department.query.count()

    return jsonify(upcoming=upcoming, completed=completed, departments=departments), 200
