from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from model import db, User, Doctor, Patient, Appointment, Treatment, Department
from datetime import date, timedelta
from sqlalchemy import or_

doctor_bp = Blueprint('doctor', __name__)


def get_current_doctor():
    user = User.query.get(int(get_jwt_identity()))
    if not user or user.role != 'doctor' or not user.doctor_profile:
        return None
    return user.doctor_profile


# ── Dashboard Stats ──────────────────────────────────────────
@doctor_bp.route('/api/doctor/dashboard', methods=['GET'])
@jwt_required()
def doctor_dashboard():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    today = date.today()
    week_end = today + timedelta(days=7)

    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.status == 'Booked',
        Appointment.date >= today
    ).count()

    today_count = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.date == today,
        Appointment.status.in_(['Booked', 'Completed'])
    ).count()

    completed = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.status == 'Completed'
    ).count()

    cancelled = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.status == 'Cancelled'
    ).count()

    patient_count = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doc.id
    ).distinct().count()

    # Today's schedule
    today_appointments = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.date == today
    ).order_by(Appointment.time.asc()).all()

    today_list = []
    for a in today_appointments:
        today_list.append({
            'id': a.id,
            'patient': a.patient.full_name,
            'time': a.time.strftime('%H:%M'),
            'status': a.status
        })

    # Weekly chart data (appointments per day for next 7 days)
    chart_labels = []
    chart_data = []
    for i in range(7):
        d = today + timedelta(days=i)
        chart_labels.append(d.strftime('%a %d'))
        count = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.date == d
        ).count()
        chart_data.append(count)

    return jsonify(
        upcoming=upcoming,
        today=today_count,
        completed=completed,
        cancelled=cancelled,
        patients=patient_count,
        today_schedule=today_list,
        chart_labels=chart_labels,
        chart_data=chart_data,
        doctor_name=doc.full_name,
        department=doc.department.name
    ), 200


# ── Appointments List ────────────────────────────────────────
@doctor_bp.route('/api/doctor/appointments', methods=['GET'])
@jwt_required()
def doctor_appointments():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    filter_type = request.args.get('filter', 'all')
    today = date.today()
    week_end = today + timedelta(days=7)

    query = Appointment.query.filter(Appointment.doctor_id == doc.id)

    if filter_type == 'today':
        query = query.filter(Appointment.date == today)
    elif filter_type == 'week':
        query = query.filter(Appointment.date >= today, Appointment.date <= week_end)
    elif filter_type == 'upcoming':
        query = query.filter(Appointment.date >= today, Appointment.status == 'Booked')
    elif filter_type == 'past':
        query = query.filter(Appointment.date < today)

    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()

    result = []
    for a in appointments:
        item = {
            'id': a.id,
            'patient_name': a.patient.full_name,
            'patient_id': a.patient.id,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status,
            'has_treatment': a.treatment is not None
        }
        result.append(item)

    return jsonify(result), 200


# ── Update Appointment Status ────────────────────────────────
@doctor_bp.route('/api/doctor/appointments/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_appointment_status(id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    appointment = Appointment.query.get(id)
    if not appointment or appointment.doctor_id != doc.id:
        return jsonify(msg='Appointment not found'), 404

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['Completed', 'Cancelled']:
        return jsonify(msg='Invalid status. Use Completed or Cancelled'), 400

    if appointment.status != 'Booked':
        return jsonify(msg='Can only update Booked appointments'), 400

    appointment.status = new_status
    db.session.commit()

    return jsonify(msg=f'Appointment marked as {new_status}'), 200


# ── Add Treatment ────────────────────────────────────────────
@doctor_bp.route('/api/doctor/appointments/<int:id>/treatment', methods=['POST'])
@jwt_required()
def add_treatment(id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    appointment = Appointment.query.get(id)
    if not appointment or appointment.doctor_id != doc.id:
        return jsonify(msg='Appointment not found'), 404

    if appointment.status != 'Completed':
        return jsonify(msg='Can only add treatment to completed appointments'), 400

    if appointment.treatment:
        return jsonify(msg='Treatment already exists. Use PUT to update.'), 400

    data = request.get_json()

    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis=data.get('diagnosis', ''),
        prescription=data.get('prescription', ''),
        notes=data.get('notes', ''),
        next_visit=data.get('next_visit') or None
    )
    db.session.add(treatment)
    db.session.commit()

    return jsonify(msg='Treatment record added'), 201


# ── Update Treatment ─────────────────────────────────────────
@doctor_bp.route('/api/doctor/appointments/<int:id>/treatment', methods=['PUT'])
@jwt_required()
def update_treatment(id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    appointment = Appointment.query.get(id)
    if not appointment or appointment.doctor_id != doc.id:
        return jsonify(msg='Appointment not found'), 404

    if not appointment.treatment:
        return jsonify(msg='No treatment record found'), 404

    data = request.get_json()
    t = appointment.treatment
    t.diagnosis = data.get('diagnosis', t.diagnosis)
    t.prescription = data.get('prescription', t.prescription)
    t.notes = data.get('notes', t.notes)
    t.next_visit = data.get('next_visit') or t.next_visit

    db.session.commit()

    return jsonify(msg='Treatment record updated'), 200


# ── My Patients ──────────────────────────────────────────────
@doctor_bp.route('/api/doctor/patients', methods=['GET'])
@jwt_required()
def doctor_patients():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    search = request.args.get('search', '').strip()

    # Get distinct patients who have appointments with this doctor
    patient_ids = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doc.id
    ).distinct().all()
    patient_ids = [pid[0] for pid in patient_ids]

    if not patient_ids:
        return jsonify([]), 200

    query = Patient.query.filter(Patient.id.in_(patient_ids))

    if search:
        query = query.filter(
            or_(
                Patient.full_name.ilike(f'%{search}%'),
                Patient.contact.ilike(f'%{search}%')
            )
        )

    patients = query.all()
    result = []
    for p in patients:
        # Count appointments with this doctor
        apt_count = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.patient_id == p.id
        ).count()

        result.append({
            'id': p.id,
            'full_name': p.full_name,
            'contact': p.contact,
            'gender': p.gender,
            'blood_group': p.blood_group,
            'dob': p.dob.isoformat() if p.dob else None,
            'appointment_count': apt_count
        })

    return jsonify(result), 200


# ── Patient Medical History ──────────────────────────────────
@doctor_bp.route('/api/doctor/patients/<int:patient_id>/history', methods=['GET'])
@jwt_required()
def patient_history(patient_id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify(msg='Patient not found'), 404

    # Get all appointments between this doctor and this patient
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.patient_id == patient_id
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()

    result = {
        'patient': {
            'id': patient.id,
            'full_name': patient.full_name,
            'contact': patient.contact,
            'gender': patient.gender,
            'blood_group': patient.blood_group,
            'dob': patient.dob.isoformat() if patient.dob else None,
            'address': patient.address
        },
        'records': []
    }

    for a in appointments:
        record = {
            'appointment_id': a.id,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status,
            'treatment': None
        }
        if a.treatment:
            record['treatment'] = {
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes,
                'next_visit': a.treatment.next_visit.isoformat() if a.treatment.next_visit else None
            }
        result['records'].append(record)

    return jsonify(result), 200


# ── Get / Update Availability ────────────────────────────────
@doctor_bp.route('/api/doctor/availability', methods=['GET'])
@jwt_required()
def get_availability():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    return jsonify(
        availability=doc.availability or '',
        full_name=doc.full_name,
        department=doc.department.name
    ), 200


@doctor_bp.route('/api/doctor/availability', methods=['PUT'])
@jwt_required()
def update_availability():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    data = request.get_json()
    doc.availability = data.get('availability', doc.availability)
    db.session.commit()

    return jsonify(msg='Availability updated'), 200


# ── Doctor Profile ───────────────────────────────────────────
@doctor_bp.route('/api/doctor/profile', methods=['GET'])
@jwt_required()
def doctor_profile():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg='Forbidden'), 403

    return jsonify(
        id=doc.id,
        full_name=doc.full_name,
        email=doc.user.email,
        contact=doc.contact,
        department=doc.department.name,
        experience=doc.experience,
        qualification=doc.qualification,
        availability=doc.availability
    ), 200
