from app import app, db
from model import User, Department, Doctor, Patient, Appointment, Treatment
from datetime import datetime, timedelta, date, time
from werkzeug.security import generate_password_hash
import random

def seed_data():
    with app.app_context():
        # 1. Clear and Create Tables
        db.drop_all()
        db.create_all()

        # 2. Create Admin (Predefined - No registration allowed)
        admin = User(
            username='admin',
            password=generate_password_hash('adminpassword'),
            email='admin@hospital.com',
            role='admin',
            is_active=True
        )
        db.session.add(admin)

        # 3. Create Departments
        departments_data = [
            {'name': 'Cardiology', 'desc': 'Diagnosis and treatment of heart and blood vessel conditions.'},
            {'name': 'Neurology', 'desc': 'Treatment of disorders of the nervous system.'},
            {'name': 'Orthopedics', 'desc': 'Care for musculoskeletal injuries and conditions.'},
            {'name': 'Pediatrics', 'desc': 'Medical care for infants, children, and adolescents.'},
            {'name': 'General Surgery', 'desc': 'Surgical procedures for a wide range of conditions.'},
            {'name': 'Dermatology', 'desc': 'Treatment of skin, hair, and nail conditions.'},
            {'name': 'ENT', 'desc': 'Ear, nose, and throat specialist care.'},
            {'name': 'Ophthalmology', 'desc': 'Eye care and vision-related treatments.'},
        ]
        for d in departments_data:
            db.session.add(Department(name=d['name'], description=d['desc']))

        db.session.flush()

        all_departments = Department.query.all()

        # 4. Create 20 Doctors
        doctor_names = [
            'Dr. Aarav Sharma', 'Dr. Priya Patel', 'Dr. Rohan Mehta', 'Dr. Sneha Reddy',
            'Dr. Vikram Singh', 'Dr. Anjali Gupta', 'Dr. Karan Joshi', 'Dr. Meera Nair',
            'Dr. Arjun Rao', 'Dr. Divya Iyer', 'Dr. Siddharth Kapoor', 'Dr. Pooja Verma',
            'Dr. Nikhil Das', 'Dr. Riya Choudhary', 'Dr. Aditya Pillai', 'Dr. Kavya Menon',
            'Dr. Harsh Agarwal', 'Dr. Tanvi Bhat', 'Dr. Rahul Saxena', 'Dr. Neha Kulkarni'
        ]
        qualifications = [
            'MBBS, MD Cardiology', 'MBBS, MS Neurology', 'MBBS, MS Orthopedics',
            'MBBS, MD Pediatrics', 'MBBS, MS General Surgery', 'MBBS, MD Dermatology',
            'MBBS, MS ENT', 'MBBS, MS Ophthalmology'
        ]
        availabilities = [
            'Mon-Fri 09:00-17:00', 'Mon-Sat 10:00-16:00', 'Tue-Sat 08:00-14:00',
            'Mon-Fri 11:00-19:00', 'Wed-Sun 09:00-15:00'
        ]

        for i in range(20):
            d_user = User(
                username=f'doctor{i+1}',
                password=generate_password_hash('doctor123'),
                email=f'doctor{i+1}@hospital.com',
                role='doctor',
                is_active=True
            )
            db.session.add(d_user)
            db.session.flush()

            dept = all_departments[i % len(all_departments)]
            doctor = Doctor(
                user_id=d_user.id,
                department_id=dept.id,
                full_name=doctor_names[i],
                contact=f'+91-98765-{10000+i}',
                experience=f'{random.randint(2, 25)} years',
                qualification=qualifications[i % len(qualifications)],
                availability=availabilities[i % len(availabilities)],
                is_blacklisted=False
            )
            db.session.add(doctor)

        db.session.flush()

        # 5. Create 50 Patients
        first_names = [
            'Amit', 'Sunita', 'Raj', 'Lakshmi', 'Deepak', 'Anita', 'Suresh', 'Geeta',
            'Manish', 'Rekha', 'Vijay', 'Suman', 'Prakash', 'Kamla', 'Ajay', 'Usha',
            'Ramesh', 'Savita', 'Manoj', 'Nandini', 'Sanjay', 'Parvati', 'Ashok', 'Lata',
            'Ravi', 'Kiran', 'Mohan', 'Padma', 'Gaurav', 'Shanti', 'Pankaj', 'Mala',
            'Naveen', 'Pushpa', 'Tarun', 'Jaya', 'Yogesh', 'Seema', 'Dinesh', 'Radha',
            'Sachin', 'Swati', 'Nitin', 'Asha', 'Vishal', 'Bhavna', 'Arun', 'Hema',
            'Kunal', 'Reena'
        ]
        last_names = ['Kumar', 'Sharma', 'Verma', 'Gupta', 'Singh', 'Patel', 'Jain', 'Mishra', 'Yadav', 'Chauhan']
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        genders = ['Male', 'Female']

        for i in range(50):
            p_user = User(
                username=f'patient{i+1}',
                password=generate_password_hash('patient123'),
                email=f'patient{i+1}@email.com',
                role='patient',
                is_active=(i % 25 != 0)
            )
            db.session.add(p_user)
            db.session.flush()

            patient = Patient(
                user_id=p_user.id,
                full_name=f'{first_names[i]} {last_names[i % len(last_names)]}',
                contact=f'+91-90000-{10000+i}',
                dob=date(1960 + (i % 40), (i % 12) + 1, (i % 28) + 1),
                gender=genders[i % 2],
                blood_group=blood_groups[i % len(blood_groups)],
                address=f'{100+i}, Sector {i+1}, New Delhi',
                is_blacklisted=False
            )
            db.session.add(patient)

        db.session.flush()

        all_doctors = Doctor.query.all()
        all_patients = Patient.query.all()

        # 6. Create Appointments (mix of Booked, Completed, Cancelled)
        today = date.today()
        appointment_times = [
            time(9, 0), time(9, 30), time(10, 0), time(10, 30),
            time(11, 0), time(11, 30), time(14, 0), time(14, 30),
            time(15, 0), time(15, 30), time(16, 0), time(16, 30)
        ]

        # Past appointments (completed/cancelled) - for history
        for i in range(40):
            doc = all_doctors[i % len(all_doctors)]
            pat = all_patients[i % len(all_patients)]
            apt_date = today - timedelta(days=random.randint(5, 60))
            apt_time = appointment_times[i % len(appointment_times)]

            status = 'Completed' if i % 5 != 0 else 'Cancelled'
            appointment = Appointment(
                patient_id=pat.id,
                doctor_id=doc.id,
                date=apt_date,
                time=apt_time,
                status=status
            )
            db.session.add(appointment)
            db.session.flush()

            # Add treatment records for completed appointments
            if status == 'Completed':
                diagnoses = [
                    'Mild hypertension', 'Seasonal allergies', 'Lower back strain',
                    'Common cold', 'Vitamin D deficiency', 'Migraine',
                    'Skin rash - eczema', 'Conjunctivitis', 'Ankle sprain',
                    'Gastric reflux', 'Mild anemia', 'Sinus infection'
                ]
                prescriptions = [
                    'Amlodipine 5mg daily', 'Cetirizine 10mg as needed',
                    'Ibuprofen 400mg twice daily', 'Paracetamol 500mg thrice daily',
                    'Vitamin D3 60000 IU weekly', 'Sumatriptan 50mg as needed',
                    'Hydrocortisone cream apply twice daily', 'Moxifloxacin eye drops',
                    'Crepe bandage and rest', 'Pantoprazole 40mg before breakfast',
                    'Iron supplement daily', 'Amoxicillin 500mg thrice daily'
                ]
                treatment = Treatment(
                    appointment_id=appointment.id,
                    diagnosis=diagnoses[i % len(diagnoses)],
                    prescription=prescriptions[i % len(prescriptions)],
                    notes=f'Patient responding well. Follow-up in {random.choice([7, 14, 30])} days.',
                    next_visit=today + timedelta(days=random.randint(7, 30))
                )
                db.session.add(treatment)

        # Future/upcoming appointments (booked) - for dashboards
        for i in range(20):
            doc = all_doctors[i % len(all_doctors)]
            pat = all_patients[(i + 10) % len(all_patients)]
            apt_date = today + timedelta(days=random.randint(1, 14))
            apt_time = appointment_times[i % len(appointment_times)]

            appointment = Appointment(
                patient_id=pat.id,
                doctor_id=doc.id,
                date=apt_date,
                time=apt_time,
                status='Booked'
            )
            db.session.add(appointment)

        db.session.commit()
        print("Success! Database created and seeded with hospital management data.")
        print(f"  - 1 Admin (admin / adminpassword)")
        print(f"  - {len(all_departments)} Departments")
        print(f"  - 20 Doctors (doctor1..doctor20 / doctor123)")
        print(f"  - 50 Patients (patient1..patient50 / patient123)")
        print(f"  - 60 Appointments (40 past + 20 upcoming)")
        print(f"  - ~32 Treatment records for completed appointments")

if __name__ == '__main__':
    seed_data()
