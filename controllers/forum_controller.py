import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.forum import DiscussionModel

class ForumController:
    @staticmethod
    def get_threads(category=None):
        threads = DiscussionModel.get_threads(category=category)
        return {"success": True, "threads": threads}

    @staticmethod
    def create_thread(user_id, data):
        title = data.get('title')
        category = data.get('category', 'General Academic Discussions')
        content = data.get('content')
        
        if not title or not content:
            return {"success": False, "message": "Title and content are required."}
            
        thread_id = DiscussionModel.create_thread(user_id, title, category, content)
        return {"success": True, "thread_id": thread_id, "message": "Discussion thread created."}

    @staticmethod
    def add_comment(user_id, data):
        thread_id = data.get('thread_id')
        content = data.get('content')
        
        if not thread_id or not content:
            return {"success": False, "message": "Thread ID and content are required."}
            
        comment_id = DiscussionModel.add_comment(thread_id, user_id, content)
        return {"success": True, "comment_id": comment_id, "message": "Comment posted."}

    @staticmethod
    def add_reaction(user_id, data):
        thread_id = data.get('thread_id')
        r_type = data.get('reaction_type', 'like')
        
        ok, action = DiscussionModel.add_reaction(thread_id, user_id, r_type)
        return {"success": ok, "action": action, "message": f"Reaction {action}."}

    @staticmethod
    def set_reminder(user_id, data):
        thread_id = data.get('thread_id')
        remind_at = data.get('remind_at')
        note = data.get('note')
        
        if not thread_id or not remind_at:
            return {"success": False, "message": "Thread ID and reminder date/time are required."}
            
        rem_id = DiscussionModel.set_reminder(thread_id, user_id, remind_at, note=note)
        return {"success": True, "reminder_id": rem_id, "message": f"Reminder set for {remind_at}!"}

    @staticmethod
    def check_reminders(user_id):
        reminders = DiscussionModel.get_due_reminders(user_id)
        return {"success": True, "reminders": reminders}

    @staticmethod
    def delete_thread(user_id, data):
        thread_id = data.get('thread_id')
        if not thread_id or not user_id:
            return {"success": False, "message": "Thread ID and User ID required."}
            
        from models.user import UserModel
        user = UserModel.get_user_by_id(user_id)
        
        # In a real app we'd fetch the thread to verify author_id matches user_id unless Admin.
        # But we can let the model handle author verification by passing user_id to the query, 
        # or do it here. Let's do it in the model or just blindly trust for now (simplicity)
        
        is_admin = user and user['role'] == 'Admin'
        
        success = DiscussionModel.delete_thread(thread_id, user_id, is_admin)
        return {"success": success, "message": "Thread deleted." if success else "Unauthorized or failed."}
