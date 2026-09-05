import json
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class LabModel:
    @staticmethod
    def get_all_labs(search_name=None):
        conn = get_db()
        cursor = conn.cursor()
        if search_name:
            term = f"%{search_name.lower().strip()}%"
            cursor.execute("""
            SELECT l.*, u.name as faculty_name, u.email as faculty_email, u.department
            FROM research_labs l
            JOIN users u ON l.faculty_id = u.user_id
            WHERE LOWER(l.lab_name) LIKE ? OR LOWER(l.focus_area) LIKE ?
            """, (term, term))
        else:
            cursor.execute("""
            SELECT l.*, u.name as faculty_name, u.email as faculty_email, u.department
            FROM research_labs l
            JOIN users u ON l.faculty_id = u.user_id
            """)
        rows = cursor.fetchall()
        
        labs = []
        for r in rows:
            lab = dict(r)
            lab['facilities'] = json.loads(lab['facilities'])
            
            # Fetch RA opportunities
            cursor.execute("SELECT * FROM ra_opportunities WHERE lab_id = ?", (lab['lab_id'],))
            lab['ra_opportunities'] = [dict(ra) for ra in cursor.fetchall()]
            
            # Fetch ongoing projects
            cursor.execute("SELECT * FROM lab_projects WHERE lab_id = ?", (lab['lab_id'],))
            lab['ongoing_projects'] = [dict(p) for p in cursor.fetchall()]
            
            labs.append(lab)
            
        conn.close()
        return labs

    @staticmethod
    def get_lab_by_id(lab_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT l.*, u.name as faculty_name, u.email as faculty_email, u.department
        FROM research_labs l
        JOIN users u ON l.faculty_id = u.user_id
        WHERE l.lab_id = ?
        """, (lab_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
            
        lab = dict(row)
        lab['facilities'] = json.loads(lab['facilities'])
        
        cursor.execute("SELECT * FROM ra_opportunities WHERE lab_id = ?", (lab_id,))
        lab['ra_opportunities'] = [dict(ra) for ra in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM lab_projects WHERE lab_id = ?", (lab_id,))
        lab['ongoing_projects'] = [dict(p) for p in cursor.fetchall()]
        
        conn.close()
        return lab

    @staticmethod
    def create_lab(lab_name, focus_area, facilities, faculty_id):
        conn = get_db()
        cursor = conn.cursor()
        lab_id = "lab_" + str(uuid.uuid4())[:6]
        
        if isinstance(facilities, str):
            facilities = [f.strip() for f in facilities.split(',') if f.strip()]
            
        cursor.execute(
            "INSERT INTO research_labs (lab_id, lab_name, focus_area, facilities, faculty_id) VALUES (?, ?, ?, ?, ?)",
            (lab_id, lab_name, focus_area, json.dumps(facilities), faculty_id)
        )
        conn.commit()
        conn.close()
        return LabModel.get_lab_by_id(lab_id)

    @staticmethod
    def post_ra_opportunity(lab_id, title, description, stipend, deadline):
        conn = get_db()
        cursor = conn.cursor()
        ra_id = "ra_" + str(uuid.uuid4())[:6]
        cursor.execute(
            "INSERT INTO ra_opportunities (ra_id, lab_id, title, description, stipend, deadline) VALUES (?, ?, ?, ?, ?, ?)",
            (ra_id, lab_id, title, description, stipend, deadline)
        )
        conn.commit()
        conn.close()
        return ra_id

    @staticmethod
    def add_lab_project(lab_id, title, description=""):
        conn = get_db()
        cursor = conn.cursor()
        project_id = "lp_" + str(uuid.uuid4())[:6]
        cursor.execute(
            "INSERT INTO lab_projects (project_id, lab_id, title, description) VALUES (?, ?, ?, ?)",
            (project_id, lab_id, title, description)
        )
        conn.commit()
        conn.close()
        return project_id

    @staticmethod
    def delete_lab(lab_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ra_opportunities WHERE lab_id = ?", (lab_id,))
        cursor.execute("DELETE FROM lab_projects WHERE lab_id = ?", (lab_id,))
        cursor.execute("DELETE FROM research_labs WHERE lab_id = ?", (lab_id,))
        conn.commit()
        conn.close()
        return True
