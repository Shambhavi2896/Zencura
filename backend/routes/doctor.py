from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models import db, User, Doctor, Patient, Appointment, Treatment, Department, Payment
from datetime import date, timedelta
from sqlalchemy import or_
from backend.core.cache_utils import cached_route, invalidate_cache
from backend.core.cache import cache
doctor_bp = Blueprint("doctor", __name__)

def get_current_doctor():
    user = User.query.get(int(get_jwt_identity()))
    if not user or user.role != "doctor" or not user.doctor_profile:
        return None
    return user.doctor_profile

@doctor_bp.route("/api/doctor/dashboard", methods=["GET"])

@jwt_required()

def doctor_dashboard():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    today = date.today()
    week_end = today + timedelta(days=7)
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.status == "Booked",
        Appointment.date >= today,
    ).count()
    today_count = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.date == today,
        Appointment.status.in_(["Booked", "Completed"]),
    ).count()
    completed = Appointment.query.filter(
        Appointment.doctor_id == doc.id, Appointment.status == "Completed"
    ).count()
    cancelled = Appointment.query.filter(
        Appointment.doctor_id == doc.id, Appointment.status == "Cancelled"
    ).count()
    patient_count = (
        db.session.query(Appointment.patient_id)
        .filter(Appointment.doctor_id == doc.id)
        .distinct()
        .count()
    )
    today_appointments = (
        Appointment.query.filter(
            Appointment.doctor_id == doc.id, Appointment.date == today
        )
        .order_by(Appointment.time.asc())
        .all()
    )
    today_list = []
    for a in today_appointments:
        today_list.append(
            {
                "id": a.id,
                "patient": a.patient.full_name,
                "time": a.time.strftime("%H:%M"),
                "status": a.status,
            }
        )
    chart_labels = []
    chart_data = []
    for i in range(7):
        d = today + timedelta(days=i)
        chart_labels.append(d.strftime("%a %d"))
        count = Appointment.query.filter(
            Appointment.doctor_id == doc.id, Appointment.date == d
        ).count()
        chart_data.append(count)
    return (
        jsonify(
            upcoming=upcoming,
            today=today_count,
            completed=completed,
            cancelled=cancelled,
            patients=patient_count,
            today_schedule=today_list,
            chart_labels=chart_labels,
            chart_data=chart_data,
            doctor_name=doc.full_name,
            department=doc.department.name,
        ),
        200,
    )

@doctor_bp.route("/api/doctor/appointments", methods=["GET"])

@jwt_required()

def doctor_appointments():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    filter_type = request.args.get("filter", "all")
    today = date.today()
    week_end = today + timedelta(days=7)
    query = Appointment.query.filter(Appointment.doctor_id == doc.id)
    if filter_type == "today":
        query = query.filter(Appointment.date == today)
    elif filter_type == "week":
        query = query.filter(Appointment.date >= today, Appointment.date <= week_end)
    elif filter_type == "upcoming":
        query = query.filter(Appointment.date >= today, Appointment.status == "Booked")
    elif filter_type == "past":
        query = query.filter(Appointment.date < today)
    appointments = query.order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()
    result = []
    for a in appointments:
        item = {
            "id": a.id,
            "patient_name": a.patient.full_name,
            "patient_id": a.patient.id,
            "date": a.date.isoformat(),
            "time": a.time.strftime("%H:%M"),
            "status": a.status,
            "has_treatment": a.treatment is not None,
        }
        result.append(item)
    return jsonify(result), 200

@doctor_bp.route("/api/doctor/appointments/<int:id>/status", methods=["PUT"])

@jwt_required()

def update_appointment_status(id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    appointment = Appointment.query.get(id)
    if not appointment or appointment.doctor_id != doc.id:
        return jsonify(msg="Appointment not found"), 404
    data = request.get_json()
    new_status = data.get("status")
    if new_status not in ["Completed", "Cancelled"]:
        return jsonify(msg="Invalid status. Use Completed or Cancelled"), 400
    if appointment.status != "Booked":
        return jsonify(msg="Can only update Booked appointments"), 400
    appointment.status = new_status
    db.session.commit()
    return jsonify(msg=f"Appointment marked as {new_status}"), 200

@doctor_bp.route("/api/doctor/appointments/<int:id>/treatment", methods=["POST"])

@jwt_required()

def add_treatment(id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    appointment = Appointment.query.get(id)
    if not appointment or appointment.doctor_id != doc.id:
        return jsonify(msg="Appointment not found"), 404
    if appointment.status != "Completed":
        return jsonify(msg="Can only add treatment to completed appointments"), 400
    if appointment.treatment:
        return jsonify(msg="Treatment already exists. Use PUT to update."), 400
    data = request.get_json()
    diagnosis = data.get("diagnosis", "").strip()
    prescription = data.get("prescription", "").strip()
    amount = data.get("amount")
    if not all([diagnosis, prescription, amount]):
        return jsonify(msg="Diagnosis, prescription and amount are required"), 400
    try:
        amount = float(amount)
        if amount < 0:
            return jsonify(msg="Amount cannot be negative"), 400
    except (ValueError, TypeError):
        return jsonify(msg="Invalid amount format"), 400
    next_visit_date = None
    if data.get("next_visit"):
        from datetime import date
        try:
            next_visit_date = date.fromisoformat(data["next_visit"])
        except ValueError:
            pass
    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=data.get("notes", ""),
        next_visit=next_visit_date,
    )
    db.session.add(treatment)
    db.session.flush()
    payment = Payment(
        treatment_id=treatment.id, amount=amount
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify(msg="Treatment record added"), 201

@doctor_bp.route("/api/doctor/appointments/<int:id>/treatment", methods=["PUT"])

@jwt_required()

def update_treatment(id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    appointment = Appointment.query.get(id)
    if not appointment or appointment.doctor_id != doc.id:
        return jsonify(msg="Appointment not found"), 404
    if not appointment.treatment:
        return jsonify(msg="No treatment record found"), 404
    data = request.get_json()
    t = appointment.treatment
    t.diagnosis = data.get("diagnosis", t.diagnosis)
    t.prescription = data.get("prescription", t.prescription)
    t.notes = data.get("notes", t.notes)
    if "next_visit" in data:
        next_visit_str = data["next_visit"]
        if next_visit_str:
            from datetime import date
            try:
                t.next_visit = date.fromisoformat(next_visit_str)
            except ValueError:
                pass
        else:
            t.next_visit = None
    db.session.commit()
    return jsonify(msg="Treatment record updated"), 200

@doctor_bp.route("/api/doctor/patients", methods=["GET"])

@jwt_required()

def doctor_patients():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    search = request.args.get("search", "").strip()
    patient_ids = (
        db.session.query(Appointment.patient_id)
        .filter(Appointment.doctor_id == doc.id)
        .distinct()
        .all()
    )
    patient_ids = [pid[0] for pid in patient_ids]
    if not patient_ids:
        return jsonify([]), 200
    query = Patient.query.filter(Patient.id.in_(patient_ids))
    if search:
        query = query.filter(
            or_(
                Patient.full_name.ilike(f"%{search}%"),
                Patient.contact.ilike(f"%{search}%"),
            )
        )
    patients = query.all()
    result = []
    for p in patients:
        apt_count = Appointment.query.filter(
            Appointment.doctor_id == doc.id, Appointment.patient_id == p.id
        ).count()
        result.append(
            {
                "id": p.id,
                "full_name": p.full_name,
                "contact": p.contact,
                "gender": p.gender,
                "blood_group": p.blood_group,
                "dob": p.dob.isoformat() if p.dob else None,
                "appointment_count": apt_count,
            }
        )
    return jsonify(result), 200

@doctor_bp.route("/api/doctor/patients/<int:patient_id>/history", methods=["GET"])

@jwt_required()

def patient_history(patient_id):
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify(msg="Patient not found"), 404
    appointments = (
        Appointment.query.filter(
            Appointment.doctor_id == doc.id, Appointment.patient_id == patient_id
        )
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )
    result = {
        "patient": {
            "id": patient.id,
            "full_name": patient.full_name,
            "contact": patient.contact,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "dob": patient.dob.isoformat() if patient.dob else None,
            "address": patient.address,
        },
        "records": [],
    }
    for a in appointments:
        record = {
            "appointment_id": a.id,
            "date": a.date.isoformat(),
            "time": a.time.strftime("%H:%M"),
            "status": a.status,
            "treatment": None,
        }
        if a.treatment:
            record["treatment"] = {
                "diagnosis": a.treatment.diagnosis,
                "prescription": a.treatment.prescription,
                "notes": a.treatment.notes,
                "next_visit": (
                    a.treatment.next_visit.isoformat()
                    if a.treatment.next_visit
                    else None
                ),
                "payment": None,
            }
            if a.treatment.payment:
                record["treatment"]["payment"] = {
                    "amount": a.treatment.payment.amount,
                    "status": a.treatment.payment.status,
                    "transaction_id": a.treatment.payment.transaction_id,
                }
        result["records"].append(record)
    return jsonify(result), 200

@doctor_bp.route("/api/doctor/availability", methods=["GET"])

@jwt_required()

@cache.cached(timeout=600, key_prefix="doctor_availability")

def get_availability():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    return (
        jsonify(
            availability=doc.availability or "",
            full_name=doc.full_name,
            department=doc.department.name,
        ),
        200,
    )

@doctor_bp.route("/api/doctor/availability", methods=["PUT"])

@jwt_required()

@invalidate_cache("api_cache:*availability*", "api_cache:*doctor*")

def update_availability():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    data = request.get_json()
    doc.availability = data.get("availability", doc.availability)
    db.session.commit()
    from backend.core.cache import cache
    cache.delete("doctor_availability")
    return jsonify(msg="Availability updated"), 200

@doctor_bp.route("/api/doctor/profile", methods=["GET"])

@jwt_required()

@cache.cached(timeout=600, key_prefix="doctor_profile")

def doctor_profile():
    doc = get_current_doctor()
    if not doc:
        return jsonify(msg="Forbidden"), 403
    return (
        jsonify(
            id=doc.id,
            full_name=doc.full_name,
            email=doc.user.email,
            contact=doc.contact,
            department=doc.department.name,
            experience=doc.experience,
            qualification=doc.qualification,
            availability=doc.availability,
        ),
        200,
    )
