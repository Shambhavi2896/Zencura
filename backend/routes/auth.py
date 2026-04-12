from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, User, Patient
from datetime import datetime
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/login", methods=["POST"])

def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()
    if not user or not check_password_hash(user.password, data.get("password", "")):
        return jsonify(msg="Invalid username or password"), 401
    if not user.is_active:
        return jsonify(msg="Your account has been deactivated"), 403
    token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role}
    )
    response = {"token": token, "role": user.role, "username": user.username}
    if user.role == "doctor" and user.doctor_profile:
        response["full_name"] = user.doctor_profile.full_name
    elif user.role == "patient" and user.patient_profile:
        response["full_name"] = user.patient_profile.full_name
    return jsonify(response), 200

@auth_bp.route("/api/register", methods=["POST"])

def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    if not all([username, email, password, full_name]):
        return jsonify(msg="Username, email, password and full name are all required"), 400
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(msg="Invalid email format"), 400
    if len(password) < 6:
        return jsonify(msg="Password must be at least 6 characters"), 400
    if User.query.filter_by(username=username).first():
        return jsonify(msg="Username already taken"), 409
    if User.query.filter_by(email=email).first():
        return jsonify(msg="Email already registered"), 409
    user = User(
        username=username,
        password=generate_password_hash(password),
        email=email,
        role="patient",
    )
    db.session.add(user)
    db.session.flush()
    dob = None
    if data.get("dob"):
        try:
            for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                try:
                    dob = datetime.strptime(data.get("dob"), fmt).date()
                    break
                except ValueError:
                    continue
        except Exception as e:
            return jsonify(msg=f"Invalid date format. Use DD-MM-YYYY"), 400
    patient = Patient(
        user_id=user.id,
        full_name=data.get("full_name", ""),
        contact=data.get("contact", ""),
        dob=dob,
        gender=data.get("gender", ""),
        blood_group=data.get("blood_group", ""),
        address=data.get("address", ""),
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(msg="Registration successful! You can now login."), 201

@auth_bp.route("/api/me", methods=["GET"])

@jwt_required()

def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify(msg="User not found"), 404
    result = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }
    if user.role == "doctor" and user.doctor_profile:
        result["full_name"] = user.doctor_profile.full_name
        result["department"] = user.doctor_profile.department.name
    elif user.role == "patient" and user.patient_profile:
        result["full_name"] = user.patient_profile.full_name
    return jsonify(result), 200
