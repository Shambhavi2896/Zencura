from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User, Doctor, Patient, Appointment, Treatment, Department, Payment
from datetime import date, time, timedelta
import time as time_mod
from sqlalchemy import or_
from celery.result import AsyncResult
from backend.core.cache import cache

patient_bp = Blueprint('patient', __name__)


def get_current_patient():
    user = User.query.get(int(get_jwt_identity()))
    if not user or user.role != 'patient' or not user.patient_profile:
        return None
    return user.patient_profile
@patient_bp.route('/api/patient/dashboard', methods=['GET'])
@jwt_required()
def patient_dashboard():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    today = date.today()

    upcoming = Appointment.query.filter(
        Appointment.patient_id == pat.id,
        Appointment.status == 'Booked',
        Appointment.date >= today
    ).count()

    completed = Appointment.query.filter(
        Appointment.patient_id == pat.id,
        Appointment.status == 'Completed'
    ).count()

    cancelled = Appointment.query.filter(
        Appointment.patient_id == pat.id,
        Appointment.status == 'Cancelled'
    ).count()

    total = Appointment.query.filter(
        Appointment.patient_id == pat.id
    ).count()
    upcoming_list = Appointment.query.filter(
        Appointment.patient_id == pat.id,
        Appointment.status == 'Booked',
        Appointment.date >= today
    ).order_by(Appointment.date.asc(), Appointment.time.asc()).limit(5).all()

    upcoming_apts = []
    for a in upcoming_list:
        upcoming_apts.append({
            'id': a.id,
            'doctor': a.doctor.full_name,
            'department': a.doctor.department.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status
        })

    return jsonify(
        upcoming=upcoming,
        completed=completed,
        cancelled=cancelled,
        total=total,
        patient_name=pat.full_name,
        upcoming_appointments=upcoming_apts
    ), 200
@patient_bp.route('/api/patient/doctors', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def search_doctors():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    search = request.args.get('search', '').strip()
    dept_id = request.args.get('department', '')

    query = Doctor.query.join(User).join(Department).filter(User.is_active == True)

    if search:
        if len(search) < 2:
            return jsonify(msg='Search query must be at least 2 characters'), 400
        query = query.filter(
            or_(
                Doctor.full_name.ilike(f'%{search}%'),
                Department.name.ilike(f'%{search}%')
            )
        )

    if dept_id:
        try:
            dept_id = int(dept_id)
            query = query.filter(Doctor.department_id == dept_id)
        except (ValueError, TypeError):
            return jsonify(msg='Invalid department ID'), 400

    doctors = query.all()
    result = []
    for d in doctors:
        result.append({
            'id': d.id,
            'full_name': d.full_name,
            'department': d.department.name,
            'department_id': d.department_id,
            'qualification': d.qualification,
            'experience': d.experience,
            'availability': d.availability,
            'contact': d.contact
        })

    return jsonify(result), 200
@patient_bp.route('/api/patient/departments', methods=['GET'])
@jwt_required()
@cache.cached(timeout=3600)
def get_departments():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    departments = Department.query.order_by(Department.name).all()
    return jsonify([{'id': d.id, 'name': d.name} for d in departments]), 200
@patient_bp.route('/api/patient/doctors/<int:doctor_id>/slots', methods=['GET'])
@jwt_required()
@cache.cached(timeout=30, query_string=True)
def get_doctor_slots(doctor_id):
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify(msg='Doctor not found'), 404

    req_date = request.args.get('date', '')
    if not req_date:
        return jsonify(msg='Date parameter required'), 400

    try:
        apt_date = date.fromisoformat(req_date)
    except ValueError:
        return jsonify(msg='Invalid date format'), 400

    if apt_date < date.today():
        return jsonify(msg='Cannot book past dates'), 400
    all_slots = []
    for hour in range(9, 17):
        for minute in [0, 30]:
            all_slots.append(time(hour, minute))
    booked = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == apt_date,
        Appointment.status.in_(['Booked', 'Completed'])
    ).all()

    booked_times = {a.time for a in booked}

    available = []
    for slot in all_slots:
        available.append({
            'time': slot.strftime('%H:%M'),
            'available': slot not in booked_times
        })

    return jsonify(
        doctor_name=doctor.full_name,
        department=doctor.department.name,
        date=req_date,
        slots=available
    ), 200
@patient_bp.route('/api/patient/appointments', methods=['POST'])
@jwt_required()
def book_appointment():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    data = request.get_json()
    doctor_id = data.get('doctor_id')
    apt_date_str = data.get('date')
    apt_time_str = data.get('time')

    if not all([doctor_id, apt_date_str, apt_time_str]):
        return jsonify(msg='Doctor, date, and time are required'), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor or not doctor.user.is_active:
        return jsonify(msg='Doctor not available'), 400

    try:
        apt_date = date.fromisoformat(apt_date_str)
        apt_time = time.fromisoformat(apt_time_str)
    except ValueError:
        return jsonify(msg='Invalid date or time format'), 400

    if apt_date < date.today():
        return jsonify(msg='Cannot book past dates'), 400
    existing = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == apt_date,
        Appointment.time == apt_time,
        Appointment.status.in_(['Booked', 'Completed'])
    ).first()

    if existing:
        return jsonify(msg='This time slot is already booked'), 409

    appointment = Appointment(
        patient_id=pat.id,
        doctor_id=doctor_id,
        date=apt_date,
        time=apt_time,
        status='Booked'
    )
    db.session.add(appointment)
    db.session.commit()

    # Trigger confirmation email
    try:
        from backend.tasks.send_appointment_confirmation import send_confirmation_email
        send_confirmation_email.delay(appointment.id)
    except Exception as e:
        pass  # Log error but don't fail the booking

    return jsonify(msg='Appointment booked successfully', id=appointment.id), 201
@patient_bp.route('/api/patient/appointments', methods=['GET'])
@jwt_required()
def get_my_appointments():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    filter_type = request.args.get('filter', 'all')
    today = date.today()

    query = Appointment.query.filter(Appointment.patient_id == pat.id)

    if filter_type == 'upcoming':
        query = query.filter(Appointment.date >= today, Appointment.status == 'Booked')
    elif filter_type == 'past':
        query = query.filter(
            or_(
                Appointment.date < today,
                Appointment.status.in_(['Completed', 'Cancelled'])
            )
        )
    elif filter_type == 'completed':
        query = query.filter(Appointment.status == 'Completed')
    elif filter_type == 'cancelled':
        query = query.filter(Appointment.status == 'Cancelled')

    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()

    result = []
    for a in appointments:
        item = {
            'id': a.id,
            'doctor_name': a.doctor.full_name,
            'doctor_id': a.doctor_id,
            'department': a.doctor.department.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status,
            'treatment': None
        }
        if a.treatment:
            item['treatment'] = {
                'id': a.treatment.id,
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes,
                'next_visit': a.treatment.next_visit.isoformat() if a.treatment.next_visit else None,
                'payment': None
            }
            if a.treatment.payment:
                item['treatment']['payment'] = {
                    'amount': a.treatment.payment.amount,
                    'status': a.treatment.payment.status,
                    'transaction_id': a.treatment.payment.transaction_id
                }
        result.append(item)

    return jsonify(result), 200
@patient_bp.route('/api/patient/appointments/<int:id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(id):
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    appointment = Appointment.query.get(id)
    if not appointment or appointment.patient_id != pat.id:
        return jsonify(msg='Appointment not found'), 404

    if appointment.status != 'Booked':
        return jsonify(msg='Can only cancel booked appointments'), 400

    appointment.status = 'Cancelled'
    db.session.commit()

    return jsonify(msg='Appointment cancelled'), 200
@patient_bp.route('/api/patient/appointments/<int:id>/reschedule', methods=['PUT'])
@jwt_required()
def reschedule_appointment(id):
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    appointment = Appointment.query.get(id)
    if not appointment or appointment.patient_id != pat.id:
        return jsonify(msg='Appointment not found'), 404

    if appointment.status != 'Booked':
        return jsonify(msg='Can only reschedule booked appointments'), 400

    data = request.get_json()
    new_date_str = data.get('date')
    new_time_str = data.get('time')

    if not all([new_date_str, new_time_str]):
        return jsonify(msg='New date and time are required'), 400

    try:
        new_date = date.fromisoformat(new_date_str)
        new_time = time.fromisoformat(new_time_str)
    except ValueError:
        return jsonify(msg='Invalid date or time format'), 400

    if new_date < date.today():
        return jsonify(msg='Cannot reschedule to a past date'), 400
    existing = Appointment.query.filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.date == new_date,
        Appointment.time == new_time,
        Appointment.status.in_(['Booked', 'Completed']),
        Appointment.id != id
    ).first()

    if existing:
        return jsonify(msg='This time slot is already booked'), 409

    appointment.date = new_date
    appointment.time = new_time
    db.session.commit()

    return jsonify(msg='Appointment rescheduled successfully'), 200
@patient_bp.route('/api/patient/profile', methods=['GET'])
@jwt_required()
def get_profile():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    return jsonify(
        id=pat.id,
        full_name=pat.full_name,
        email=pat.user.email,
        contact=pat.contact,
        gender=pat.gender,
        dob=pat.dob.isoformat() if pat.dob else '',
        blood_group=pat.blood_group,
        address=pat.address
    ), 200
@patient_bp.route('/api/patient/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    data = request.get_json()
    pat.full_name = data.get('full_name', pat.full_name)
    pat.contact = data.get('contact', pat.contact)
    pat.gender = data.get('gender', pat.gender)
    pat.blood_group = data.get('blood_group', pat.blood_group)
    pat.address = data.get('address', pat.address)

    if data.get('dob'):
        pat.dob = data['dob']

    db.session.commit()
    return jsonify(msg='Profile updated successfully', full_name=pat.full_name), 200
@patient_bp.route('/api/patient/export', methods=['POST'])
@jwt_required()
def request_export():
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403
        
    from backend.tasks.export_csv import generate_patient_export
    task = generate_patient_export.delay(pat.id)
    return jsonify(msg="Export task started", task_id=task.id), 202

@patient_bp.route('/api/patient/export/<task_id>', methods=['GET'])
@jwt_required()
def get_export_status(task_id):
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403
        
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result if task_result.status == 'SUCCESS' else str(task_result.info)
    }
    return jsonify(result), 200
@patient_bp.route('/api/patient/treatments/<int:id>/pay', methods=['POST'])
@jwt_required()
def pay_treatment(id):
    pat = get_current_patient()
    if not pat:
        return jsonify(msg='Forbidden'), 403

    treatment = Treatment.query.get(id)
    if not treatment or treatment.appointment.patient_id != pat.id:
        return jsonify(msg='Treatment not found'), 404

    if not treatment.payment:
        return jsonify(msg='No invoice associated with this treatment'), 404

    if treatment.payment.status == 'Paid':
        return jsonify(msg='Treatment is already paid.'), 400
    treatment.payment.status = 'Paid'
    treatment.payment.transaction_id = f"tx_mock_{treatment.id}_{int(time_mod.time())}"
    db.session.commit()

    return jsonify(msg='Payment successful via Mock Gateway', transaction_id=treatment.payment.transaction_id), 200

