import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.project import ProjectModel
from models.user import UserModel

class ProjectController:
    @staticmethod
    def get_all_posts(skill=None):
        posts = ProjectModel.get_all_posts(skill_filter=skill)
        return {"success": True, "count": len(posts), "posts": posts}

    @staticmethod
    def get_join_requests(user_id):
        if not user_id:
            return {"success": False, "message": "User ID is required."}
        data = ProjectModel.get_user_join_requests(user_id)
        return {"success": True, "incoming": data["incoming"], "outgoing": data["outgoing"], "pending_count": data["pending_count"]}

    @staticmethod
    def create_post(user_id, data):
        user = UserModel.get_by_id(user_id)
        if not user or user['role'] != 'Student':
            return {"success": False, "message": "Only students can post project ideas in Teammate Finder."}

        title = data.get('idea_title')
        desc = data.get('description')
        skills = data.get('required_skills')
        
        if not title or not desc or not skills:
            return {"success": False, "message": "Idea title, description, and required skills are mandatory."}
            
        post_id = ProjectModel.create_post(user_id, title, desc, skills)
        if not post_id:
            return {"success": False, "message": "Failed to create project post. Only students can create posts."}
        return {"success": True, "post_id": post_id, "message": "Project post created successfully."}

    @staticmethod
    def join_team(post_id, user_id):
        if not post_id or not user_id:
            return {"success": False, "message": "Post ID and User ID required."}
        user = UserModel.get_by_id(user_id)
        if not user or user['role'] != 'Student':
            return {"success": False, "message": "Only students can request to join project teams."}
        return ProjectModel.add_teammate(post_id, user_id)

    @staticmethod
    def respond_join(data):
        post_id = data.get('post_id')
        applicant_id = data.get('applicant_id')
        creator_id = data.get('creator_id') or data.get('user_id')
        action = data.get('action')
        
        if not post_id or not applicant_id or not creator_id or not action:
            return {"success": False, "message": "Post ID, Applicant ID, Creator ID, and Action are required."}
            
        return ProjectModel.respond_to_join_request(post_id, applicant_id, creator_id, action)

    @staticmethod
    def delete_post(user_id, post_id):
        if not user_id or not post_id:
            return {"success": False, "message": "User ID and Post ID required."}
            
        user = UserModel.get_by_id(user_id)
        is_admin = user and user['role'] == 'Admin'
        
        success = ProjectModel.delete_post(post_id, user_id, is_admin)
        return {"success": success, "message": "Project post deleted." if success else "Unauthorized or failed."}
