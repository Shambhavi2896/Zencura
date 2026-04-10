"""Appointment management routes.

This module handles appointment-related API endpoints for creating,
updating, and managing medical appointments.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from model import db, Appointment, Patient, Doctor
from backend.core.utils import error_response, success_response

appointment_bp = Blueprint('appointment', __name__)


@appointment_bp.route('/api/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get all appointments with optional filtering."""
    status = request.args.get('status', None)
    doctor_id = request.args.get('doctor_id', None)
    patient_id = request.args.get('patient_id', None)
    
    query = Appointment.query
    
    if status:
        query = query.filter_by(status=status)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    appointments = query.all()
    return success_response([
        {
            'id': a.id,
            'patient_id': a.patient_id,
            'doctor_id': a.doctor_id,
            'date': a.date.isoformat(),
            'time': a.time.isoformat(),
            'status': a.status,
            'created_at': a.created_at.isoformat() if a.created_at else None
        }
        for a in appointments
    ])


@appointment_bp.route('/api/appointments/<int:id>', methods=['GET'])
@jwt_required()
def get_appointment(id):
    """Get appointment details by ID."""
    appointment = Appointment.query.get(id)
    
    if not appointment:
        return error_response('Appointment not found', 404)
    
    return success_response({
        'id': appointment.id,
        'patient_id': appointment.patient_id,
        'doctor_id': appointment.doctor_id,
        'date': appointment.date.isoformat(),
        'time': appointment.time.isoformat(),
        'status': appointment.status,
        'created_at': appointment.created_at.isoformat() if appointment.created_at else None
    })


@appointment_bp.route('/api/appointments/<int:id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(id):
    """Cancel an appointment."""
    appointment = Appointment.query.get(id)
    
    if not appointment:
        return error_response('Appointment not found', 404)
    
    if appointment.status == 'Cancelled':
        return error_response('Appointment is already cancelled', 400)
    
    appointment.status = 'Cancelled'
    db.session.commit()
    
    return success_response(message='Appointment cancelled successfully')
