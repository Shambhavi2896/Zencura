from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


def get_utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    doctors = db.relationship('Doctor', backref='department', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    experience = db.Column(db.String(50))
    qualification = db.Column(db.String(200))
    availability = db.Column(db.String(255))
    is_blacklisted = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    address = db.Column(db.Text)
    is_blacklisted = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('patient_profile', uselist=False))
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked')
    created_at = db.Column(db.DateTime, default=get_utc_now)
    treatment = db.relationship('Treatment', backref='appointment', uselist=False,
                                cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', 'time', name='uq_doctor_date_time'),
    )

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False, unique=True)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    next_visit = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    payment = db.relationship('Payment', backref='treatment', uselist=False, cascade='all, delete-orphan')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatment.id'), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False, default=150.00)
    status = db.Column(db.String(20), default='Pending')
    transaction_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=get_utc_now)

