import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.admin import AdminModel
from models.user import UserModel
from models.internship import InternshipModel

class AdminController:
    @staticmethod
    def get_users():
        users = AdminModel.get_all_users()
        return {"success": True, "users": users}

    @staticmethod
    def toggle_user_status(user_id):
        return AdminModel.toggle_user_status(user_id)

    @staticmethod
    def delete_user(user_id):
        return AdminModel.delete_user(user_id)

    @staticmethod
    def add_user(data):
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        department = data.get('department', 'CSE')
        role = data.get('role', 'Student')

        if not name or not email or not password:
            return {"success": False, "message": "Name, email, and password are required."}

        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters long."}

        try:
            user = UserModel.create_user(name, email, password, department, role, extra_data=data)
            return {"success": True, "user": user, "message": f"User {name} created successfully."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def create_internship(data):
        company = data.get('company_name')
        title = data.get('title')
        reqs = data.get('requirements')
        cgpa = data.get('min_cgpa', 3.0)
        dept = data.get('department', 'CSE')
        deadline = data.get('deadline')
        email = data.get('contact_email')
        phone = data.get('contact_phone')

        if not company or not title or not reqs or not deadline:
            return {"success": False, "message": "Company name, title, requirements, and deadline are required."}

        opp_id = InternshipModel.create_opportunity(
            company_name=company, title=title, requirements=reqs,
            min_cgpa=cgpa, department=dept, deadline=deadline,
            contact_email=email, contact_phone=phone
        )
        return {"success": True, "opportunity_id": opp_id, "message": "Internship opportunity created."}

    @staticmethod
    def delete_internship(opp_id):
        return AdminModel.delete_internship(opp_id)

    @staticmethod
    def delete_lab(lab_id):
        return AdminModel.delete_lab(lab_id)

    @staticmethod
    def delete_thesis_group(group_id):
        return AdminModel.delete_thesis_group(group_id)

    @staticmethod
    def get_system_analytics():
        stats = AdminModel.get_system_stats()
        return {"success": True, "stats": stats}
    
    #part4

    @staticmethod
    def toggle_status(user_id):
        return AdminModel.toggle_user_status(user_id)

    @staticmethod
    def verify_faculty(faculty_id):
        return AdminModel.verify_faculty(faculty_id)

    @staticmethod
    def get_analytics():
        return {"success": True, "analytics": AdminModel.get_system_analytics()}
