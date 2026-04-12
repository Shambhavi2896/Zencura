from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from backend.models import User

def error_response(message, status_code=400):
    return jsonify(msg=message), status_code

def success_response(data=None, message="Success", status_code=200):
    response = {"msg": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def get_current_user_id():
    try:
        return get_jwt_identity()
    except:
        return None

def get_current_user():
    user_id = get_current_user_id()
    if user_id:
        return User.query.get(user_id)
    return None
