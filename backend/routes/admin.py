from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from model import db, User, Doctor, Patient, Appointment, Department
from sqlalchemy import or_
from backend.core.cache import cache

admin_bp = Blueprint('admin', __name__)

def is_admin():
    claims = get_jwt()
    return claims.get('role') == 'admin'

@admin_bp.route('/api/admin/doctors', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
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
    cache.clear()

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
    cache.clear()
    
    return jsonify(msg='Doctor updated successfully'), 200


@admin_bp.route('/api/admin/patients', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
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
                Patient.id.astext.ilike(f'%{search_query}%')  # Safe: Use SQLAlchemy filter
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
    cache.clear()

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
        item = {
            'id': a.id,
            'doctor_name': a.doctor.full_name,
            'department_name': a.doctor.department.name,
            'patient_name': a.patient.full_name,
            'date': a.date.isoformat(),
            'time': a.time.isoformat(),
            'status': a.status,
            'treatment': None
        }
        if a.treatment:
            item['treatment'] = {
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
@admin_bp.route('/api/admin/reports', methods=['GET'])
@jwt_required()
def get_reports():
    if not is_admin():
        return jsonify(msg='Forbidden'), 403

    import os
    reports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'reports')
    
    if not os.path.exists(reports_dir):
        return jsonify([]), 200

    reports = []
    for file in os.listdir(reports_dir):
        if file.endswith('.html'):
            reports.append({
                'name': file,
                'url': f"/static/reports/{file}"
            })
    reports.sort(key=lambda x: x['name'], reverse=True)
    return jsonify(reports), 200
@admin_bp.route('/api/departments', methods=['GET'])
@jwt_required()
def get_departments():
    departments = Department.query.all()
    return jsonify([{'id': d.id, 'name': d.name} for d in departments]), 200
@admin_bp.route('/api/admin/test/daily-reminder', methods=['POST'])
@jwt_required()
def test_daily_reminder():
    """Manually trigger daily reminder task for testing."""
    if not is_admin():
        return jsonify(msg='Forbidden'), 403
    
    try:
        from backend.tasks.daily_reminder import send_daily_reminders
        task = send_daily_reminders.delay()
        return jsonify(msg='Daily reminder job triggered', task_id=task.id), 200
    except Exception as e:
        return jsonify(msg=f'Error triggering job: {str(e)}'), 500

@admin_bp.route('/api/admin/test/monthly-report', methods=['POST'])
@jwt_required()
def test_monthly_report():
    """Manually trigger monthly report task for testing."""
    if not is_admin():
        return jsonify(msg='Forbidden'), 403
    
    try:
        from backend.tasks.monthly_report import generate_monthly_report
        task = generate_monthly_report.delay()
        return jsonify(msg='Monthly report job triggered', task_id=task.id), 200
    except Exception as e:
        return jsonify(msg=f'Error triggering job: {str(e)}'), 500

@admin_bp.route('/api/admin/test/csv-export', methods=['POST'])
@jwt_required()
def test_csv_export():
    """Test CSV export with sample patient patient."""
    if not is_admin():
        return jsonify(msg='Forbidden'), 403
    
    try:
        from backend.tasks.export_csv import generate_patient_export
        first_patient = Patient.query.first()
        if not first_patient:
            return jsonify(msg='No patients found to test with'), 400
        
        task = generate_patient_export.delay(first_patient.id)
        return jsonify(msg='CSV export job triggered', task_id=task.id, patient_id=first_patient.id), 200
    except Exception as e:
        return jsonify(msg=f'Error triggering job: {str(e)}'), 500

@admin_bp.route('/api/admin/test/email-config', methods=['GET'])
@jwt_required()
def test_email_config():
    """Check email configuration."""
    if not is_admin():
        return jsonify(msg='Forbidden'), 403
    
    from flask import current_app
    config = current_app.config
    
    return jsonify({
        'mail_server': config.get('MAIL_SERVER'),
        'mail_port': config.get('MAIL_PORT'),
        'mail_use_tls': config.get('MAIL_USE_TLS'),
        'mail_username': config.get('MAIL_USERNAME'),
        'mail_default_sender': config.get('MAIL_DEFAULT_SENDER'),
        'status': 'Email is configured' if config.get('MAIL_USERNAME') else 'Email NOT configured'
    }), 200

@admin_bp.route('/api/admin/test/send-test-email', methods=['POST'])
@jwt_required()
def send_test_email():
    """Send a test email to verify email configuration."""
    if not is_admin():
        return jsonify(msg='Forbidden'), 403
    
    data = request.get_json()
    recipient = data.get('email')
    
    if not recipient:
        return jsonify(msg='Email recipient required'), 400
    
    try:
        from flask_mail import Mail, Message
        from flask import current_app
        
        mail = Mail(current_app)
        msg = Message(
            subject='Zencura Hospital - Test Email',
            recipients=[recipient],
            body=f'This is a test email from Zencura Hospital Management System.\n\nIf you received this, your email configuration is working correctly!\n\nEmail configuration:\n- Server: {current_app.config.get("MAIL_SERVER")}\n- Sender: {current_app.config.get("MAIL_DEFAULT_SENDER")}'
        )
        mail.send(msg)
        return jsonify(msg=f'Test email sent to {recipient}'), 200
    except Exception as e:
        return jsonify(msg=f'Error sending email: {str(e)}'), 500

