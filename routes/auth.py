from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, User, Patient

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not check_password_hash(user.password, data.get('password', '')):
        return jsonify(msg='Invalid username or password'), 401

    if not user.is_active:
        return jsonify(msg='Your account has been deactivated'), 403

    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})

    response = {
        'token': token,
        'role': user.role,
        'username': user.username
    }

    if user.role == 'doctor' and user.doctor_profile:
        response['full_name'] = user.doctor_profile.full_name
    elif user.role == 'patient' and user.patient_profile:
        response['full_name'] = user.patient_profile.full_name

    return jsonify(response), 200

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify(msg='Username already taken'), 409

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify(msg='Email already registered'), 409

    user = User(
        username=data['username'],
        password=generate_password_hash(data['password']),
        email=data['email'],
        role='patient'
    )
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id,
        full_name=data.get('full_name', ''),
        contact=data.get('contact', ''),
        dob=data.get('dob') or None,
        gender=data.get('gender', ''),
        blood_group=data.get('blood_group', ''),
        address=data.get('address', '')
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify(msg='Registration successful! You can now login.'), 201

@auth_bp.route('/api/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify(msg='User not found'), 404

    result = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }

    if user.role == 'doctor' and user.doctor_profile:
        result['full_name'] = user.doctor_profile.full_name
        result['department'] = user.doctor_profile.department.name
    elif user.role == 'patient' and user.patient_profile:
        result['full_name'] = user.patient_profile.full_name

    return jsonify(result), 200
