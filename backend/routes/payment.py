"""Payment management module for treatment billing and tracking."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, date
from model import db, Payment, Treatment, Appointment, User, Doctor, Patient
from backend.core.utils import error_response, success_response

payment_bp = Blueprint('payment', __name__)


def is_admin():
    """Check if current user is admin."""
    claims = get_jwt()
    return claims.get('role') == 'admin'


@payment_bp.route('/api/payments', methods=['GET'])
@jwt_required()
def get_payments():
    """Get all payments with optional filtering."""
    status_filter = request.args.get('status', None)
    doctor_id = request.args.get('doctor_id', None)
    patient_id = request.args.get('patient_id', None)
    
    query = db.session.query(Payment, Treatment, Appointment, Patient, Doctor)\
        .join(Treatment, Payment.treatment_id == Treatment.id)\
        .join(Appointment, Treatment.appointment_id == Appointment.id)\
        .join(Patient, Appointment.patient_id == Patient.id)\
        .join(Doctor, Appointment.doctor_id == Doctor.id)
    
    if status_filter:
        query = query.filter(Payment.status == status_filter)
    if doctor_id:
        query = query.filter(Doctor.id == doctor_id)
    if patient_id:
        query = query.filter(Patient.id == patient_id)
    
    results = query.all()
    payments = []
    
    for payment, treatment, appointment, patient, doctor in results:
        payments.append({
            'id': payment.id,
            'amount': payment.amount,
            'status': payment.status,
            'transaction_id': payment.transaction_id,
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
            'patient_name': patient.full_name,
            'doctor_name': doctor.full_name,
            'appointment_date': appointment.date.isoformat(),
            'treatment_id': treatment.id,
            'diagnosis': treatment.diagnosis
        })
    
    return success_response(payments)


@payment_bp.route('/api/payments/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get specific payment details."""
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return error_response('Payment not found', 404)
    
    treatment = payment.treatment
    appointment = treatment.appointment
    
    return success_response({
        'id': payment.id,
        'amount': payment.amount,
        'status': payment.status,
        'transaction_id': payment.transaction_id,
        'created_at': payment.created_at.isoformat() if payment.created_at else None,
        'patient_name': appointment.patient.full_name,
        'doctor_name': appointment.doctor.full_name,
        'appointment_date': appointment.date.isoformat(),
        'treatment': {
            'id': treatment.id,
            'diagnosis': treatment.diagnosis,
            'prescription': treatment.prescription,
            'notes': treatment.notes
        }
    })


@payment_bp.route('/api/payments/<int:payment_id>/update-status', methods=['PUT'])
@jwt_required()
def update_payment_status(payment_id):
    """Update payment status."""
    if not is_admin():
        return error_response('Forbidden', 403)
    
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return error_response('Payment not found', 404)
    
    data = request.get_json()
    new_status = data.get('status')
    transaction_id = data.get('transaction_id', '')
    
    if new_status not in ['Pending', 'Completed', 'Failed', 'Refunded']:
        return error_response('Invalid status', 400)
    
    payment.status = new_status
    if transaction_id:
        payment.transaction_id = transaction_id
    
    db.session.commit()
    
    return success_response({'id': payment.id, 'status': payment.status}, 'Payment status updated')


@payment_bp.route('/api/payments/summary', methods=['GET'])
@jwt_required()
def payment_summary():
    """Get payment summary statistics."""
    if not is_admin():
        return error_response('Forbidden', 403)
    
    total_payments = db.session.query(db.func.sum(Payment.amount)).scalar() or 0.0
    completed_payments = db.session.query(db.func.sum(Payment.amount))\
        .filter(Payment.status == 'Completed').scalar() or 0.0
    pending_payments = db.session.query(db.func.sum(Payment.amount))\
        .filter(Payment.status == 'Pending').scalar() or 0.0
    
    payment_count = Payment.query.count()
    completed_count = Payment.query.filter_by(status='Completed').count()
    pending_count = Payment.query.filter_by(status='Pending').count()
    failed_count = Payment.query.filter_by(status='Failed').count()
    from sqlalchemy import extract
    monthly_revenue = db.session.query(
        extract('year', Payment.created_at).label('year'),
        extract('month', Payment.created_at).label('month'),
        db.func.sum(Payment.amount).label('total')
    ).filter(Payment.status == 'Completed')\
    .group_by('year', 'month')\
    .order_by('year', 'month').all()
    
    months = []
    revenues = []
    for year, month, total in monthly_revenue:
        months.append(f"{int(month)}/{int(year)}")
        revenues.append(float(total) if total else 0.0)
    
    return success_response({
        'total_amount': float(total_payments),
        'completed_amount': float(completed_payments),
        'pending_amount': float(pending_payments),
        'total_transactions': payment_count,
        'completed_transactions': completed_count,
        'pending_transactions': pending_count,
        'failed_transactions': failed_count,
        'monthly_revenue': {
            'labels': months,
            'data': revenues
        }
    })


@payment_bp.route('/api/payments/by-doctor', methods=['GET'])
@jwt_required()
def payments_by_doctor():
    """Get payment breakdown by doctor."""
    if not is_admin():
        return error_response('Forbidden', 403)
    
    results = db.session.query(
        Doctor.full_name,
        db.func.count(Payment.id).label('count'),
        db.func.sum(Payment.amount).label('total')
    ).join(Treatment, Payment.treatment_id == Treatment.id)\
    .join(Appointment, Treatment.appointment_id == Appointment.id)\
    .join(Doctor, Appointment.doctor_id == Doctor.id)\
    .filter(Payment.status == 'Completed')\
    .group_by(Doctor.id, Doctor.full_name)\
    .order_by(db.func.sum(Payment.amount).desc())\
    .all()
    
    data = []
    for doctor_name, count, total in results:
        data.append({
            'doctor': doctor_name,
            'transactions': count,
            'total_revenue': float(total) if total else 0.0
        })
    
    return success_response(data)

