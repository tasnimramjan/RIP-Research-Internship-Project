import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.project import ProjectModel

class ProjectController:
    @staticmethod
    def get_all_posts(skill=None):
        posts = ProjectModel.get_all_posts(skill_filter=skill)
        return {"success": True, "count": len(posts), "posts": posts}

    @staticmethod
    def create_post(student_id, data):
        title = data.get('idea_title')
        desc = data.get('description')
        skills = data.get('required_skills')
        
        if not title or not desc or not skills:
            return {"success": False, "message": "Idea title, description, and required skills are mandatory."}
            
        post_id = ProjectModel.create_post(student_id, title, desc, skills)
        return {"success": True, "post_id": post_id, "message": "Project post created successfully."}

    @staticmethod
    def join_team(post_id, student_id):
        res = ProjectModel.add_teammate(post_id, student_id)
        return res

    @staticmethod
    def delete_post(user_id, post_id):
        if not user_id or not post_id:
            return {"success": False, "message": "User ID and Post ID required."}
            
        from models.user import UserModel
        user = UserModel.get_user_by_id(user_id)
        is_admin = user and user['role'] == 'Admin'
        
        success = ProjectModel.delete_post(post_id, user_id, is_admin)
        return {"success": success, "message": "Project post deleted." if success else "Unauthorized or failed."}
