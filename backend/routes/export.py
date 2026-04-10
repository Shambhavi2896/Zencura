"""CSV export endpoints for patient data."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from model import db, Patient
from backend.core.utils import error_response, success_response


export_bp = Blueprint('export', __name__)


def is_patient():
    """Check if current user is a patient."""
    claims = get_jwt()
    return claims.get('role') == 'patient'


def is_admin():
    """Check if current user is admin."""
    claims = get_jwt()
    return claims.get('role') == 'admin'


@export_bp.route('/api/export/treatments/<int:patient_id>', methods=['POST'])
@jwt_required()
def export_treatment_history(patient_id):
    """Trigger async CSV export of patient treatment history.
    
    Can be triggered by the patient themselves or by an admin.
    Sends email notification when export is ready.
    """
    from backend.tasks.export_csv import generate_patient_export
    
    claims = get_jwt()
    user_id = claims.get('sub')
    user_role = claims.get('role')
    if user_role == 'patient':
        patient = db.session.query(Patient).filter(Patient.user_id == user_id).first()
        if not patient or patient.id != patient_id:
            return error_response('Unauthorized: Can only export your own data', 403)
    elif user_role != 'admin':
        return error_response('Forbidden: Only patients and admins can export', 403)
    patient = db.session.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return error_response('Patient not found', 404)
    
    try:
        task = generate_patient_export.delay(patient_id)
        
        return success_response({
            'status': 'processing',
            'task_id': task.id,
            'message': f'Export started for patient {patient.full_name}. Email notification will be sent when ready.',
            'patient_id': patient_id,
            'patient_name': patient.full_name
        }, 202)
    
    except Exception as e:
        return error_response(f'Failed to start export: {str(e)}', 500)


@export_bp.route('/api/export/status/<task_id>', methods=['GET'])
@jwt_required()
def check_export_status(task_id):
    """Check the status of an ongoing CSV export task.
    
    Returns task status: PENDING, STARTED, SUCCESS, FAILURE, RETRY
    """
    try:
        from backend.core.celery_worker import celery_app
        task = celery_app.AsyncResult(task_id)
        
        response = {
            'task_id': task_id,
            'status': task.state,
            'current': 0,
            'total': 100
        }
        
        if task.state == 'PENDING':
            response['status'] = 'pending'
            response['message'] = 'Task is waiting to be processed'
        
        elif task.state == 'PROGRESS':
            response['current'] = task.info.get('current', 0)
            response['total'] = task.info.get('total', 100)
            response['message'] = task.info.get('status', 'Processing...')
        
        elif task.state == 'SUCCESS':
            response['result'] = task.result
            response['message'] = 'Export completed successfully'
            response['download_url'] = task.result  # The result is the file URL
        
        elif task.state == 'FAILURE':
            response['message'] = f'Export failed: {str(task.info)}'
            response['error'] = str(task.info)
        
        return success_response(response)
    
    except Exception as e:
        return error_response(f'Failed to check status: {str(e)}', 500)


@export_bp.route('/api/export/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_export(filename):
    """Download a generated CSV export file.
    
    File must be in static/exports directory.
    """
    import os
    from flask import send_file
    
    try:
        if '..' in filename or filename.startswith('/'):
            return error_response('Invalid filename', 400)
        
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'exports', filename)
        if not os.path.exists(file_path):
            return error_response('File not found', 404)
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return error_response(f'Failed to download file: {str(e)}', 500)

