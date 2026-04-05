from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from model import db, User, Doctor, Patient, Appointment, Department
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)

def is_admin():
    claims = get_jwt()
    return claims.get('role') == 'admin'

@admin_bp.route('/api/admin/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    if not is_admin():
        return jsonify(msg='Forbidden'), 403

    search_query = request.args.get('search', '').lower()

    query = Doctor.query.join(User).join(Department)
    if search_query:
        query = query.filter(
            or_(
                Doctor.full_name.ilike(f'%{search_query}%'),
                Department.name.ilike(f'%{search_query}%')
            )
        )

    doctors = query.all()
    result = []
    for d in doctors:
        result.append({
            'id': d.id,
            'user_id': d.user_id,
            'username': d.user.username,
            'email': d.user.email,
            'is_active': d.user.is_active,
            'full_name': d.full_name,
            'department_id': d.department_id,
            'department_name': d.department.name,
            'contact': d.contact,
            'experience': d.experience,
            'qualification': d.qualification,
            'availability': d.availability
        })

    return jsonify(result), 200

@admin_bp.route('/api/admin/doctors', methods=['POST'])
@jwt_required()
def add_doctor():
    if not is_admin():
        return jsonify(msg='Forbidden'), 403

    data = request.get_json()

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify(msg='Username already exists'), 400
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify(msg='Email already exists'), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role='doctor',
        is_active=True
    )
    db.session.add(new_user)
    db.session.flush()

    new_doc = Doctor(
        user_id=new_user.id,
        department_id=data['department_id'],
        full_name=data['full_name'],
        contact=data.get('contact'),
        experience=data.get('experience'),
        qualification=data.get('qualification'),
        availability=data.get('availability', 'Not specified')
    )
    db.session.add(new_doc)
    db.session.commit()

    return jsonify(msg='Doctor added successfully'), 201

@admin_bp.route('/api/admin/doctors/<int:id>', methods=['PUT'])
@jwt_required()
def update_doctor(id):
    if not is_admin():
        return jsonify(msg='Forbidden'), 403

    data = request.get_json()
    doctor = Doctor.query.get(id)
    if not doctor:
        return jsonify(msg='Doctor not found'), 404

    doctor.full_name = data.get('full_name', doctor.full_name)
    doctor.department_id = data.get('department_id', doctor.department_id)
    doctor.contact = data.get('contact', doctor.contact)
    doctor.experience = data.get('experience', doctor.experience)
    doctor.qualification = data.get('qualification', doctor.qualification)
    doctor.availability = data.get('availability', doctor.availability)

    if 'password' in data and data['password']:
         doctor.user.password = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify(msg='Doctor updated successfully'), 200


@admin_bp.route('/api/admin/patients', methods=['GET'])
@jwt_required()
def get_patients():
    if not is_admin():
        return jsonify(msg='Forbidden'), 403

    search_query = request.args.get('search', '').lower()

    query = Patient.query.join(User)
    if search_query:
        query = query.filter(
            or_(
                Patient.full_name.ilike(f'%{search_query}%'),
                Patient.contact.ilike(f'%{search_query}%'),
                db.text(f"patients.id LIKE '%{search_query}%'")
            )
        )

    patients = query.all()
    result = []
    for p in patients:
        result.append({
            'id': p.id,
            'user_id': p.user_id,
            'username': p.user.username,
            'email': p.user.email,
            'is_active': p.user.is_active,
            'full_name': p.full_name,
            'contact': p.contact,
            'dob': p.dob.isoformat() if p.dob else None,
            'gender': p.gender,
            'blood_group': p.blood_group
        })

    return jsonify(result), 200

@admin_bp.route('/api/admin/users/<int:id>/toggle_status', methods=['PUT'])
@jwt_required()
def toggle_user_status(id):
    if not is_admin():
        return jsonify(msg='Forbidden'), 403

    user = User.query.get(id)
    if not user:
        return jsonify(msg='User not found'), 404

    if user.role == 'admin':
        return jsonify(msg='Cannot modify admin account status'), 400

    user.is_active = not user.is_active
    db.session.commit()

    status_str = "activated" if user.is_active else "deactivated"
    return jsonify(msg=f'User account has been {status_str}'), 200

@admin_bp.route('/api/admin/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    if not is_admin():
        return jsonify(msg='Forbidden'), 403

    appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    result = []
    for a in appointments:
        result.append({
            'id': a.id,
            'doctor_name': a.doctor.full_name,
            'department_name': a.doctor.department.name,
            'patient_name': a.patient.full_name,
            'date': a.date.isoformat(),
            'time': a.time.isoformat(),
            'status': a.status
        })

    return jsonify(result), 200

@admin_bp.route('/api/departments', methods=['GET'])
@jwt_required()
def get_departments():
    # Publicly accessible (if authenticated) so admin can see for dropdowns
    departments = Department.query.all()
    return jsonify([{'id': d.id, 'name': d.name} for d in departments]), 200
