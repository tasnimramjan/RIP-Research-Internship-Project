import hashlib
import json
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class UserModel:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        user = dict(row)
        user.pop('password_hash', None)
        return user

    get_user_by_id = get_by_id

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def authenticate(email, password):
        user = UserModel.get_by_email(email)
        if not user:
            return None
        hashed = UserModel.hash_password(password)
        if user['password_hash'] == hashed:
            user.pop('password_hash', None)
            return user
        return None

    @staticmethod
    def create_user(name, email, password, department, role, extra_data=None):
        conn = get_db()
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())[:8]
        hashed_pw = UserModel.hash_password(password)
        
        try:
            cursor.execute(
                "INSERT INTO users (user_id, name, email, password_hash, department, role) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, name, email, hashed_pw, department, role)
            )
            
            extra = extra_data or {}
            if role == 'Student':
                cgpa = float(extra.get('cgpa', 3.0))
                interests = extra.get('research_interests', [])
                if isinstance(interests, str):
                    interests = [i.strip() for i in interests.split(',') if i.strip()]
                cursor.execute(
                    "INSERT INTO students (student_id, cgpa, research_interests) VALUES (?, ?, ?)",
                    (user_id, cgpa, json.dumps(interests))
                )
            elif role == 'Faculty':
                designation = extra.get('designation', 'Lecturer')
                h_index = int(extra.get('h_index', 0))
                domains = extra.get('research_domains', [])
                if isinstance(domains, str):
                    domains = [d.strip() for d in domains.split(',') if d.strip()]
                slots = int(extra.get('remaining_slots', 5))
                min_cgpa = float(extra.get('min_cgpa_req', 3.0))
                cursor.execute(
                    "INSERT INTO faculty (faculty_id, designation, h_index, research_domains, remaining_slots, min_cgpa_req, thesis_available) VALUES (?, ?, ?, ?, ?, ?, 1)",
                    (user_id, designation, h_index, json.dumps(domains), slots, min_cgpa)
                )
            elif role == 'Admin':
                cursor.execute(
                    "INSERT INTO admins (admin_id, admin_level) VALUES (?, ?)",
                    (user_id, extra.get('admin_level', 'Moderator'))
                )
                
            conn.commit()
            return UserModel.get_by_id(user_id)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_user_profile(user_id):
        user = UserModel.get_by_id(user_id)
        if not user:
            return None
        
        conn = get_db()
        cursor = conn.cursor()
        
        if user['role'] == 'Student':
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (user_id,))
            s_row = cursor.fetchone()
            if s_row:
                s_dict = dict(s_row)
                s_dict['research_interests'] = json.loads(s_dict['research_interests'])
                user['student_profile'] = s_dict
        elif user['role'] == 'Faculty':
            cursor.execute("SELECT * FROM faculty WHERE faculty_id = ?", (user_id,))
            f_row = cursor.fetchone()
            if f_row:
                f_dict = dict(f_row)
                f_dict['research_domains'] = json.loads(f_dict['research_domains'])
                user['faculty_profile'] = f_dict
        elif user['role'] == 'Admin':
            cursor.execute("SELECT * FROM admins WHERE admin_id = ?", (user_id,))
            a_row = cursor.fetchone()
            if a_row:
                user['admin_profile'] = dict(a_row)
                
        conn.close()
        return user
