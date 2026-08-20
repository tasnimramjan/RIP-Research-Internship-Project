import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.lab import LabModel

class LabController:
    @staticmethod
    def get_all_labs(search_name=None):
        labs = LabModel.get_all_labs(search_name=search_name)
        return {"success": True, "count": len(labs), "labs": labs}

    @staticmethod
    def get_lab_detail(lab_id):
        lab = LabModel.get_lab_by_id(lab_id)
        if not lab:
            return {"success": False, "message": "Research Lab not found."}
        return {"success": True, "lab": lab}

    @staticmethod
    def post_ra(lab_id, data):
        title = data.get('title')
        desc = data.get('description')
        stipend = data.get('stipend')
        deadline = data.get('deadline')
        
        if not title or not desc:
            return {"success": False, "message": "Title and description are required."}
            
        ra_id = LabModel.post_ra_opportunity(lab_id, title, desc, stipend, deadline)
        return {"success": True, "ra_id": ra_id, "message": "RA Opportunity posted successfully."}

    @staticmethod
    def delete_lab(lab_id, user_id):
        if not lab_id or not user_id:
            return {"success": False, "message": "Lab ID and User ID required."}
        
        lab = LabModel.get_lab_by_id(lab_id)
        if not lab:
            return {"success": False, "message": "Lab not found."}
            
        # Check permissions: user must be the faculty who owns it or an Admin
        # We will do a simple check: if user_id matches faculty_id, let them delete.
        # Admin deletion can bypass this if we pass a flag or check roles, but for now we trust the controller logic.
        # Actually, let's look up user role:
        from models.user import UserModel
        user = UserModel.get_user_by_id(user_id)
        
        if not user or (user['role'] != 'Admin' and lab['faculty_id'] != user_id):
            return {"success": False, "message": "Unauthorized to delete this lab."}
            
        from models.admin import AdminModel
        success = AdminModel.delete_lab(lab_id)
        return {"success": success, "message": "Lab deleted successfully." if success else "Failed to delete lab."}
