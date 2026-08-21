import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.dashboard import DashboardModel
from models.user import UserModel

class DashboardController:
    @staticmethod
    def get_dashboard_data(user_id):
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "User not found."}

        role = user.get('role', 'Student')
        if role == 'Student':
            data = DashboardModel.get_student_dashboard(user_id)
        else:
            data = DashboardModel.get_faculty_dashboard(user_id)

        data['user_profile'] = user
        return {"success": True, "dashboard": data}