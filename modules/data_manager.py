"""
Interactive Data Manager Module with SQLite
Handles real-time data changes and persistence using SQLite database
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import streamlit as st
import sqlite3
import os

class HospitalDataManager:
    """Manage hospital data with SQLite persistence."""
    
    def __init__(self, db_path='hospital.db'):
        self.db_path = db_path
        self.init_database()
        self.sync_from_database()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                condition TEXT,
                ward TEXT,
                status TEXT DEFAULT 'Active',
                admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                discharge_date TIMESTAMP,
                bed_number TEXT,
                doctor TEXT,
                insurance TEXT,
                contact TEXT,
                emergency_contact TEXT
            )
        """)
        
        # Create beds table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS beds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bed_id TEXT UNIQUE NOT NULL,
                ward TEXT,
                room_number TEXT,
                status TEXT DEFAULT 'Available',
                patient_id TEXT,
                last_cleaned TIMESTAMP,
                equipment TEXT
            )
        """)
        
        # Create staff table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id TEXT UNIQUE NOT NULL,
                name TEXT,
                role TEXT,
                department TEXT,
                status TEXT DEFAULT 'On Duty',
                shift TEXT,
                join_date DATE,
                phone TEXT,
                email TEXT,
                patients_assigned INTEGER DEFAULT 0
            )
        """)
        
        # Create equipment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id TEXT UNIQUE NOT NULL,
                name TEXT,
                type TEXT,
                status TEXT DEFAULT 'Available',
                location TEXT,
                last_service DATE,
                next_service DATE,
                usage_hours INTEGER DEFAULT 0,
                condition TEXT
            )
        """)
        
        # Create hospital_metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospital_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                daily_patients INTEGER DEFAULT 0,
                emergency_cases INTEGER DEFAULT 0,
                icu_admissions INTEGER DEFAULT 0,
                discharge_count INTEGER DEFAULT 0,
                doctors_on_duty INTEGER DEFAULT 0,
                nurses_on_duty INTEGER DEFAULT 0,
                icu_nurses INTEGER DEFAULT 0,
                beds_available INTEGER DEFAULT 0,
                icu_beds_available INTEGER DEFAULT 0,
                ventilators_available INTEGER DEFAULT 0,
                equipment_utilization REAL DEFAULT 0,
                staff_satisfaction REAL DEFAULT 0,
                patient_satisfaction REAL DEFAULT 0,
                avg_wait_time REAL DEFAULT 0,
                surgery_count INTEGER DEFAULT 0,
                lab_tests INTEGER DEFAULT 0,
                pharmacy_orders INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Initialize with sample data if empty
        self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Initialize database with sample data if tables are empty."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if patients table is empty
        cursor.execute("SELECT COUNT(*) FROM patients")
        if cursor.fetchone()[0] == 0:
            # Insert sample patients
            sample_patients = self.generate_sample_patients()
            for patient in sample_patients:
                cursor.execute("""
                    INSERT INTO patients (patient_id, name, age, gender, condition, ward, status, 
                                        admission_date, bed_number, doctor, insurance, contact, emergency_contact)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (patient['Patient_ID'], patient['Name'], patient['Age'], patient['Gender'],
                      patient['Condition'], patient['Ward'], patient['Status'], patient['Admission_Date'],
                      patient['Bed_Number'], patient['Doctor'], patient['Insurance'], 
                      patient['Contact'], patient['Emergency_Contact']))
        
        # Check if beds table is empty
        cursor.execute("SELECT COUNT(*) FROM beds")
        if cursor.fetchone()[0] == 0:
            # Insert sample beds
            sample_beds = self.generate_sample_beds()
            for bed in sample_beds:
                cursor.execute("""
                    INSERT INTO beds (bed_id, ward, room_number, status, patient_id, last_cleaned, equipment)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (bed['Bed_ID'], bed['Ward'], bed['Room_Number'], bed['Status'],
                      bed['Patient_ID'], bed['Last_Cleaned'], bed['Equipment']))
        
        # Check if staff table is empty
        cursor.execute("SELECT COUNT(*) FROM staff")
        if cursor.fetchone()[0] == 0:
            # Insert sample staff
            sample_staff = self.generate_sample_staff()
            for member in sample_staff:
                cursor.execute("""
                    INSERT INTO staff (staff_id, name, role, department, status, shift, join_date, phone, email, patients_assigned)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (member['Staff_ID'], member['Name'], member['Role'], member['Department'],
                      member['Status'], member['Shift'], member['Join_Date'], member['Phone'],
                      member['Email'], member['Patients_Assigned']))
        
        # Check if equipment table is empty
        cursor.execute("SELECT COUNT(*) FROM equipment")
        if cursor.fetchone()[0] == 0:
            # Insert sample equipment
            sample_equipment = self.generate_sample_equipment()
            for eq in sample_equipment:
                cursor.execute("""
                    INSERT INTO equipment (equipment_id, name, type, status, location, last_service, next_service, usage_hours, condition)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (eq['Equipment_ID'], eq['Name'], eq['Type'], eq['Status'], eq['Location'],
                      eq['Last_Service'], eq['Next_Service'], eq['Usage_Hours'], eq['Condition']))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def generate_sample_patients(self, count=50):
        """Generate sample patients."""
        patients = []
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa', 'Robert', 'Emily']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        conditions = ['Flu', 'Pneumonia', 'Heart Disease', 'Diabetes', 'Hypertension', 'COVID-19', 'Fracture']
        wards = ['General', 'ICU', 'Emergency', 'Surgery', 'Cardiology']
        statuses = ['Active', 'Critical', 'Stable', 'Recovering']
        
        for i in range(count):
            patients.append({
                'Patient_ID': f'P{10000 + i}',
                'Name': f"{random.choice(first_names)} {random.choice(last_names)}",
                'Age': random.randint(18, 85),
                'Gender': random.choice(['Male', 'Female']),
                'Condition': random.choice(conditions),
                'Ward': random.choice(wards),
                'Status': random.choice(statuses),
                'Admission_Date': datetime.now() - timedelta(days=random.randint(0, 10)),
                'Bed_Number': f'B-{random.randint(101, 999)}',
                'Doctor': f"Dr. {random.choice(last_names)}",
                'Insurance': random.choice(['Private', 'Medicare', 'Medicaid']),
                'Contact': f'+1-555-{random.randint(1000, 9999)}',
                'Emergency_Contact': f'+1-555-{random.randint(1000, 9999)}'
            })
        return patients
    
    def generate_sample_beds(self):
        """Generate sample beds."""
        beds = []
        ward_types = {'General': 40, 'ICU': 20, 'Emergency': 16, 'Surgery': 12, 'Cardiology': 12}
        bed_id = 100
        
        for ward, count in ward_types.items():
            for i in range(count):
                beds.append({
                    'Bed_ID': f'B{bed_id}',
                    'Ward': ward,
                    'Room_Number': f'{ward[:3].upper()}-{i+1}',
                    'Status': random.choice(['Available', 'Occupied', 'Maintenance']),
                    'Patient_ID': None,
                    'Last_Cleaned': datetime.now() - timedelta(hours=random.randint(1, 48)),
                    'Equipment': random.choice(['Standard', 'Ventilator', 'Monitor'])
                })
                bed_id += 1
        return beds
    
    def generate_sample_staff(self):
        """Generate sample staff."""
        staff = []
        roles = {'Doctor': 15, 'Nurse': 25, 'Technician': 8, 'Administrator': 5}
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        
        staff_id = 1000
        for role, count in roles.items():
            for i in range(count):
                staff.append({
                    'Staff_ID': f'S{staff_id}',
                    'Name': f"{random.choice(first_names)} {random.choice(last_names)}",
                    'Role': role,
                    'Department': random.choice(['Emergency', 'ICU', 'General', 'Surgery']),
                    'Status': random.choice(['On Duty', 'Off Duty', 'On Leave']),
                    'Shift': random.choice(['Morning', 'Evening', 'Night']),
                    'Join_Date': datetime.now() - timedelta(days=random.randint(365, 3650)),
                    'Phone': f'+1-555-{random.randint(1000, 9999)}',
                    'Email': f'staff{staff_id}@hospital.com',
                    'Patients_Assigned': random.randint(0, 5) if role in ['Doctor', 'Nurse'] else 0
                })
                staff_id += 1
        return staff
    
    def generate_sample_equipment(self):
        """Generate sample equipment."""
        equipment = []
        eq_types = {'Ventilator': 8, 'ECG': 10, 'Defibrillator': 5, 'Ultrasound': 4, 'X-Ray': 3, 'Monitor': 15}
        eq_id = 1000
        
        for eq_type, count in eq_types.items():
            for i in range(count):
                equipment.append({
                    'Equipment_ID': f'EQ{eq_id}',
                    'Name': f'{eq_type} #{i+1}',
                    'Type': eq_type,
                    'Status': random.choice(['Available', 'In Use', 'Maintenance']),
                    'Location': random.choice(['ICU', 'Emergency', 'OR', 'General']),
                    'Last_Service': datetime.now() - timedelta(days=random.randint(0, 90)),
                    'Next_Service': datetime.now() + timedelta(days=random.randint(30, 180)),
                    'Usage_Hours': random.randint(0, 8760),
                    'Condition': random.choice(['Excellent', 'Good', 'Fair'])
                })
                eq_id += 1
        return equipment
    
    def sync_from_database(self):
        """Sync data from database to session state."""
        conn = self.get_connection()
        
        # Load patients
        patients_df = pd.read_sql("SELECT * FROM patients", conn)
        if not patients_df.empty:
            st.session_state.patients = patients_df
        
        # Load beds
        beds_df = pd.read_sql("SELECT * FROM beds", conn)
        if not beds_df.empty:
            st.session_state.beds = beds_df
        
        # Load staff
        staff_df = pd.read_sql("SELECT * FROM staff", conn)
        if not staff_df.empty:
            st.session_state.staff = staff_df
        
        # Load equipment
        equipment_df = pd.read_sql("SELECT * FROM equipment", conn)
        if not equipment_df.empty:
            st.session_state.equipment = equipment_df
        
        conn.close()
    
    # Patient Management with DB persistence
    def admit_patient(self, patient_data):
        """Admit a new patient and save to database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO patients (patient_id, name, age, gender, condition, ward, status, 
                                    admission_date, bed_number, doctor, insurance, contact, emergency_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_data['patient_id'], patient_data['name'], patient_data['age'], 
                  patient_data['gender'], patient_data['condition'], patient_data['ward'], 
                  patient_data['status'], patient_data['admission_date'], patient_data['bed_number'],
                  patient_data['doctor'], patient_data['insurance'], patient_data['contact'], 
                  patient_data['emergency_contact']))
            
            conn.commit()
            
            # Update session state
            new_patient = pd.DataFrame([patient_data])
            st.session_state.patients = pd.concat([st.session_state.patients, new_patient], ignore_index=True)
            
            # Update counter
            st.session_state.admissions_today += 1
            
            return patient_data['patient_id']
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def discharge_patient(self, patient_id):
        """Discharge a patient and update database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE patients 
                SET status = 'Discharged', discharge_date = CURRENT_TIMESTAMP 
                WHERE patient_id = ?
            """, (patient_id,))
            
            conn.commit()
            
            # Update session state
            patients = st.session_state.patients
            patients.loc[patients['patient_id'] == patient_id, 'status'] = 'Discharged'
            patients.loc[patients['patient_id'] == patient_id, 'discharge_date'] = datetime.now()
            st.session_state.patients = patients
            
            # Update counter
            st.session_state.discharges_today += 1
            
            # Free up bed
            self.release_bed_by_patient(patient_id)
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def transfer_patient(self, patient_id, new_ward, new_bed):
        """Transfer patient to different ward/bed."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get current bed
            cursor.execute("SELECT bed_number FROM patients WHERE patient_id = ?", (patient_id,))
            old_bed = cursor.fetchone()
            
            # Update patient
            cursor.execute("""
                UPDATE patients SET ward = ?, bed_number = ? WHERE patient_id = ?
            """, (new_ward, new_bed, patient_id))
            
            conn.commit()
            
            # Update session state
            patients = st.session_state.patients
            patients.loc[patients['patient_id'] == patient_id, 'ward'] = new_ward
            patients.loc[patients['patient_id'] == patient_id, 'bed_number'] = new_bed
            st.session_state.patients = patients
            
            # Update beds
            if old_bed:
                self.release_bed(old_bed[0])
            self.assign_bed(new_bed, patient_id)
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    # Bed Management
    def assign_bed(self, bed_id, patient_id):
        """Assign bed to patient."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE beds SET status = 'Occupied', patient_id = ? WHERE bed_id = ?
            """, (patient_id, bed_id))
            conn.commit()
            
            # Update session state
            beds = st.session_state.beds
            beds.loc[beds['bed_id'] == bed_id, 'status'] = 'Occupied'
            beds.loc[beds['bed_id'] == bed_id, 'patient_id'] = patient_id
            st.session_state.beds = beds
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def release_bed(self, bed_id):
        """Release a bed."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE beds SET status = 'Available', patient_id = NULL, last_cleaned = CURRENT_TIMESTAMP 
                WHERE bed_id = ?
            """, (bed_id,))
            conn.commit()
            
            # Update session state
            beds = st.session_state.beds
            beds.loc[beds['bed_id'] == bed_id, 'status'] = 'Available'
            beds.loc[beds['bed_id'] == bed_id, 'patient_id'] = None
            st.session_state.beds = beds
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def release_bed_by_patient(self, patient_id):
        """Release bed by patient ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE beds SET status = 'Available', patient_id = NULL 
                WHERE patient_id = ?
            """, (patient_id,))
            conn.commit()
            
            # Update session state
            beds = st.session_state.beds
            beds.loc[beds['patient_id'] == patient_id, 'status'] = 'Available'
            beds.loc[beds['patient_id'] == patient_id, 'patient_id'] = None
            st.session_state.beds = beds
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    # Staff Management
    def update_staff_status(self, staff_id, new_status):
        """Update staff member status."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE staff SET status = ? WHERE staff_id = ?
            """, (new_status, staff_id))
            conn.commit()
            
            # Update session state
            staff = st.session_state.staff
            staff.loc[staff['staff_id'] == staff_id, 'status'] = new_status
            st.session_state.staff = staff
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    # Equipment Management
    def update_equipment_status(self, equipment_id, new_status):
        """Update equipment status."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE equipment SET status = ? WHERE equipment_id = ?
            """, (new_status, equipment_id))
            conn.commit()
            
            # Update session state
            equipment = st.session_state.equipment
            equipment.loc[equipment['equipment_id'] == equipment_id, 'status'] = new_status
            st.session_state.equipment = equipment
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def use_equipment(self, equipment_id, patient_id=None):
        """Mark equipment as in use."""
        self.update_equipment_status(equipment_id, 'In Use')
    
    # Getters
    def get_current_stats(self):
        """Get real-time hospital statistics."""
        beds = st.session_state.beds
        patients = st.session_state.patients
        staff = st.session_state.staff
        equipment = st.session_state.equipment
        
        return {
            'total_beds': len(beds),
            'occupied_beds': len(beds[beds['status'] == 'Occupied']),
            'available_beds': len(beds[beds['status'] == 'Available']),
            'total_patients': len(patients[patients['status'] == 'Active']),
            'critical_patients': len(patients[patients['status'] == 'Critical']),
            'staff_on_duty': len(staff[staff['status'] == 'On Duty']),
            'total_staff': len(staff),
            'equipment_available': len(equipment[equipment['status'] == 'Available']),
            'equipment_in_use': len(equipment[equipment['status'] == 'In Use']),
            'admissions_today': len(patients[pd.to_datetime(patients['admission_date']).dt.date == datetime.now().date()]),
            'discharges_today': len(patients[patients['status'] == 'Discharged'])
        }
    
    def get_available_beds(self, ward=None):
        """Get list of available beds."""
        beds = st.session_state.beds
        available = beds[beds['status'] == 'Available']
        if ward:
            available = available[available['ward'] == ward]
        return available
    
    def get_available_staff(self, role=None):
        """Get list of available staff."""
        staff = st.session_state.staff
        available = staff[staff['status'].isin(['On Duty', 'Available'])]
        if role:
            available = available[available['role'] == role]
        return available
    
    def get_available_equipment(self, eq_type=None):
        """Get list of available equipment."""
        equipment = st.session_state.equipment
        available = equipment[equipment['status'] == 'Available']
        if eq_type:
            available = available[available['type'] == eq_type]
        return available
