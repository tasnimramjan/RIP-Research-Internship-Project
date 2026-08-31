import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.forum import DiscussionModel

class ForumController:
    @staticmethod
    def get_user_spaces(user_id):
        access = DiscussionModel.get_accessible_spaces(user_id)
        return {"success": True, **access}

    @staticmethod
    def get_threads(category=None, user_id=None):
        threads = DiscussionModel.get_threads(category=category, user_id=user_id)
        return {"success": True, "threads": threads}

    @staticmethod
    def create_thread(user_id, data):
        title = data.get('title')
        category = data.get('category', 'General Academic Discussions')
        content = data.get('content')
        
        if not title or not content:
            return {"success": False, "message": "Title and content are required."}
            
        return DiscussionModel.create_thread(user_id, title, category, content)

    @staticmethod
    def add_comment(user_id, data):
        thread_id = data.get('thread_id')
        content = data.get('content')
        
        if not thread_id or not content:
            return {"success": False, "message": "Thread ID and content are required."}
            
        return DiscussionModel.add_comment(thread_id, user_id, content)

    @staticmethod
    def delete_comment(user_id, data):
        comment_id = data.get('comment_id')
        if not comment_id or not user_id:
            return {"success": False, "message": "Comment ID and User ID required."}
        return DiscussionModel.delete_comment(comment_id, user_id)

    @staticmethod
    def add_reaction(user_id, data):
        thread_id = data.get('thread_id')
        comment_id = data.get('comment_id')
        r_type = data.get('reaction_type', 'like')
        
        return DiscussionModel.add_reaction(user_id, thread_id=thread_id, comment_id=comment_id, reaction_type=r_type)

    @staticmethod
    def moderate_reactions(user_id, data):
        thread_id = data.get('thread_id')
        comment_id = data.get('comment_id')
        return DiscussionModel.moderate_reactions(user_id, thread_id=thread_id, comment_id=comment_id)

    @staticmethod
    def set_reminder(user_id, data):
        thread_id = data.get('thread_id')
        remind_at = data.get('remind_at')
        note = data.get('note')
        
        if not thread_id or not remind_at:
            return {"success": False, "message": "Thread ID and reminder date/time are required."}
            
        return DiscussionModel.set_reminder(thread_id, user_id, remind_at, note=note)

    @staticmethod
    def check_reminders(user_id):
        reminders = DiscussionModel.get_due_reminders(user_id)
        return {"success": True, "reminders": reminders}

    @staticmethod
    def get_my_reminders(user_id):
        reminders = DiscussionModel.get_user_reminders(user_id)
        return {"success": True, "reminders": reminders}

    @staticmethod
    def delete_reminder(user_id, data):
        reminder_id = data.get('reminder_id')
        if not reminder_id or not user_id:
            return {"success": False, "message": "Reminder ID and User ID required."}
        return DiscussionModel.delete_reminder(reminder_id, user_id)

    @staticmethod
    def delete_thread(user_id, data):
        thread_id = data.get('thread_id')
        if not thread_id or not user_id:
            return {"success": False, "message": "Thread ID and User ID required."}
            
        success = DiscussionModel.delete_thread(thread_id, user_id)
        return {"success": success, "message": "Discussion thread deleted." if success else "Unauthorized or failed."}

    @staticmethod
    def get_admin_stats(user_id):
        return DiscussionModel.get_admin_analytics(user_id)

    @staticmethod
    def get_admin_reminders(user_id):
        return DiscussionModel.get_all_reminders_admin(user_id)
