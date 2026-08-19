import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.internship import InternshipModel
from models.user import UserModel

class InternshipController:
    @staticmethod
    def get_opportunities(student_id=None):
        student_cgpa = None
        dept = None
        if student_id:
            profile = UserModel.get_user_profile(student_id)
            if profile and profile.get('role') == 'Student':
                student_cgpa = profile['student_profile']['cgpa']
                dept = profile['department']
                
        opps = InternshipModel.get_all_opportunities(student_cgpa=student_cgpa, department=dept)
        return {"success": True, "opportunities": opps}

    @staticmethod
    def apply(opportunity_id, student_id):
        res = InternshipModel.apply_for_internship(opportunity_id, student_id)
        return res

    @staticmethod
    def get_my_applications(student_id):
        apps = InternshipModel.get_student_applications(student_id)
        return {"success": True, "applications": apps}

    @staticmethod
    def create_posting(data):
        c_name = data.get('company_name')
        title = data.get('title')
        reqs = data.get('requirements')
        min_cgpa = data.get('min_cgpa', 3.0)
        dept = data.get('department', 'CSE')
        deadline = data.get('deadline')
        
        if not c_name or not title or not reqs or not deadline:
            return {"success": False, "message": "Company, Title, Requirements, and Deadline are required."}
            
        opp_id = InternshipModel.create_opportunity(c_name, title, reqs, min_cgpa, dept, deadline)
        return {"success": True, "opportunity_id": opp_id, "message": "Internship opportunity created."}
