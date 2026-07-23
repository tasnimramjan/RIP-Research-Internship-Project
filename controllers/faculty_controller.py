import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.user import UserModel
from models.lab import LabModel
from models.supervisor import SupervisorModel

class FacultyController:
    @staticmethod
    def get_faculty_profile(faculty_id):
        profile = UserModel.get_user_profile(faculty_id)
        if not profile or profile.get('role') != 'Faculty':
            return {"success": False, "message": "Faculty profile not found."}
            
        all_labs = LabModel.get_all_labs()
        directed_labs = [l for l in all_labs if l['faculty_id'] == faculty_id]
        profile['directed_labs'] = directed_labs
        
        return {"success": True, "faculty": profile}

    @staticmethod
    def update_faculty_profile(faculty_id, data):
        designation = data.get('designation')
        h_index = data.get('h_index')
        domains = data.get('research_domains')
        slots = data.get('remaining_slots')
        min_cgpa = data.get('min_cgpa_req')
        thesis_avail = data.get('thesis_available')

        ok = SupervisorModel.update_faculty_profile(
            faculty_id, designation=designation, h_index=h_index,
            research_domains=domains, remaining_slots=slots,
            min_cgpa_req=min_cgpa, thesis_available=thesis_avail
        )
        return {"success": ok, "message": "Faculty profile updated successfully." if ok else "No changes were made."}

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
