import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class InternshipModel:
    @staticmethod
    def get_all_opportunities(student_cgpa=None, department=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM internship_opportunities ORDER BY deadline ASC")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            item = dict(r)
            if student_cgpa is not None:
                item['eligible'] = bool(student_cgpa >= item['min_cgpa'])
            else:
                item['eligible'] = True
            results.append(item)
        return results

    @staticmethod
    def create_opportunity(company_name, title, requirements, min_cgpa, department, deadline, contact_email=None, contact_phone=None, external_url=None):
        conn = get_db()
        cursor = conn.cursor()
        opp_id = "int_" + str(uuid.uuid4())[:6]
        cursor.execute(
            "INSERT INTO internship_opportunities (opportunity_id, company_name, title, requirements, min_cgpa, department, deadline, contact_email, contact_phone, external_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (opp_id, company_name, title, requirements, float(min_cgpa), department, deadline, contact_email, contact_phone, external_url)
        )
        conn.commit()
        conn.close()
        return opp_id

    @staticmethod
    def apply_for_internship(opportunity_id, student_id):
        conn = get_db()
        cursor = conn.cursor()
        
        # Check existing application
        cursor.execute("SELECT * FROM internship_applications WHERE opportunity_id = ? AND student_id = ?", (opportunity_id, student_id))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "message": "You have already applied for this internship opportunity."}
            
        app_id = "app_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO internship_applications (application_id, opportunity_id, student_id, status, applied_at) VALUES (?, ?, ?, ?, ?)",
            (app_id, opportunity_id, student_id, "Pending", now)
        )
        conn.commit()
        conn.close()
        return {"success": True, "application_id": app_id}

    @staticmethod
    def get_student_applications(student_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT a.*, o.company_name, o.title, o.deadline, o.min_cgpa
        FROM internship_applications a
        JOIN internship_opportunities o ON a.opportunity_id = o.opportunity_id
        WHERE a.student_id = ?
        ORDER BY a.applied_at DESC
        """, (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
