import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.user import UserModel
from models.lab import LabModel
from models.supervisor import SupervisorModel
from models.faculty import FacultyModel, parse_json_list

class FacultyController:
    @staticmethod
    def get_faculty_profile(faculty_id):
        profile = FacultyModel.get_faculty_details(faculty_id)
        if not profile:
            return {"success": False, "message": "Faculty profile not found."}
        return {"success": True, "faculty": profile}

    @staticmethod
    def get_my_profile(faculty_id):
        from db import get_db
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Faculty Details
        cursor.execute("""
            SELECT f.*, u.name, u.email, u.department 
            FROM faculty f
            JOIN users u ON f.faculty_id = u.user_id
            WHERE f.faculty_id = ?
        """, (faculty_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"success": False, "message": "Faculty not found."}
            
        faculty = dict(row)
        faculty['research_domains'] = parse_json_list(faculty.get('research_domains'))
        
        # 2. Labs
        cursor.execute("SELECT * FROM research_labs WHERE faculty_id = ?", (faculty_id,))
        labs = []
        for r in cursor.fetchall():
            lab = dict(r)
            lab['facilities'] = parse_json_list(lab.get('facilities'))
            labs.append(lab)
        
        # 3. Publications
        cursor.execute("SELECT * FROM research_papers WHERE faculty_id = ?", (faculty_id,))
        papers = []
        for p in cursor.fetchall():
            paper = dict(p)
            paper['authors'] = parse_json_list(paper.get('authors'))
            papers.append(paper)
            
        conn.close()
        
        return {
            "success": True,
            "faculty": faculty,
            "labs": labs,
            "papers": papers
        }

    @staticmethod
    def search_faculty(params):
        keywords = params.get('keywords')
        department = params.get('department')
        domain = params.get('domain')
        lab = params.get('lab')
        
        results = FacultyModel.search_faculty(keywords, department, domain, lab)
        return {"success": True, "faculties": results}

    @staticmethod
    def update_faculty_profile(faculty_id, data):
        name = data.get('name')
        department = data.get('department')
        designation = data.get('designation')
        h_index = data.get('h_index')
        domains = data.get('research_domains')
        slots = data.get('remaining_slots')
        max_capacity = data.get('max_capacity')
        min_cgpa = data.get('min_cgpa_req') if data.get('min_cgpa_req') is not None else data.get('min_cgpa')
        thesis_avail = data.get('thesis_available')

        ok = SupervisorModel.update_faculty_profile(
            faculty_id, designation=designation, h_index=h_index,
            research_domains=domains, remaining_slots=slots,
            min_cgpa_req=min_cgpa, thesis_available=thesis_avail,
            name=name, department=department, max_capacity=max_capacity
        )
        return {"success": ok, "message": "Faculty profile updated successfully." if ok else "No changes were made."}

    @staticmethod
    def verify_faculty(faculty_id, is_verified):
        if not faculty_id:
            return {"success": False, "message": "Faculty ID is required."}
        ok = FacultyModel.verify_faculty_profile(faculty_id, is_verified)
        status_str = "verified" if is_verified else "unverified"
        return {"success": ok, "message": f"Faculty profile marked as {status_str}."}

    @staticmethod
    def admin_edit_faculty(faculty_id, data):
        if not faculty_id:
            return {"success": False, "message": "Faculty ID is required."}
        
        desig = data.get('designation')
        domains = data.get('research_domains')
        h_index = data.get('h_index')
        max_cap = data.get('max_capacity')
        curr_stud = data.get('current_students')
        slots = data.get('remaining_slots')
        cgpa = data.get('min_cgpa_req') if data.get('min_cgpa_req') is not None else data.get('min_cgpa')
        verified = data.get('is_verified')
        thesis_avail = data.get('thesis_available')
        
        ok = FacultyModel.admin_update_faculty(
            faculty_id, designation=desig, research_domains=domains,
            h_index=h_index, max_capacity=max_cap, current_students=curr_stud,
            remaining_slots=slots, min_cgpa_req=cgpa,
            is_verified=verified, thesis_available=thesis_avail
        )
        return {"success": ok, "message": "Faculty profile details updated by Admin." if ok else "Failed to update profile."}

    @staticmethod
    def create_lab(faculty_id, data):
        name = data.get('lab_name')
        area = data.get('focus_area')
        facilities = data.get('facilities', [])

        if not name or not area:
            return {"success": False, "message": "Lab name and focus area are required."}

        lab = LabModel.create_lab(name, area, facilities, faculty_id)
        return {"success": True, "lab": lab, "message": "Research lab created successfully."}

    @staticmethod
    def add_lab_project(data):
        lab_id = data.get('lab_id')
        title = data.get('title')
        desc = data.get('description', '')

        if not lab_id or not title:
            return {"success": False, "message": "Lab ID and project title are required."}

        pid = LabModel.add_lab_project(lab_id, title, desc)
        return {"success": True, "project_id": pid, "message": "Ongoing research project added."}
