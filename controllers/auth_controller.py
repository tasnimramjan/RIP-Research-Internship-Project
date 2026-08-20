import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.user import UserModel

class AuthController:
    @staticmethod
    def handle_login(data):
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {"success": False, "message": "Email and password are required."}
            
        user = UserModel.authenticate(email, password)
        if not user:
            return {"success": False, "message": "Invalid email or password."}
            
        profile = UserModel.get_user_profile(user['user_id'])
        return {"success": True, "user": profile, "message": f"Welcome back, {user['name']}!"}

    @staticmethod
    def handle_signup(data):
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        department = data.get('department', 'CSE')
        role = data.get('role', 'Student')
        
        if role == 'Admin':
            return {"success": False, "message": "Admin registration is not allowed here."}
            
        
        if not name or not email or not password:
            return {"success": False, "message": "Name, email, and password are required."}

        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters long."}
            
        existing = UserModel.get_by_email(email)
        if existing:
            return {"success": False, "message": "User with this email already exists."}
            
        try:
            user = UserModel.create_user(name, email, password, department, role, extra_data=data)
            profile = UserModel.get_user_profile(user['user_id'])
            return {"success": True, "user": profile, "message": "Registration successful!"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def handle_get_profile(user_id):
        profile = UserModel.get_user_profile(user_id)
        if not profile:
            return {"success": False, "message": "User profile not found."}
        return {"success": True, "user": profile}
