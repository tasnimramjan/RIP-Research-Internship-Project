import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.forum import DiscussionModel

class ForumController:
    @staticmethod
    def get_threads(user_id, category=None):
        allowed = DiscussionModel.get_user_allowed_categories(user_id)
        if category and category != "All" and category not in allowed:
            return {"success": False, "message": "You do not have access to this category."}
            
        threads = DiscussionModel.get_threads(category=category)
        # Further filter threads if category is 'All'
        if not category or category == "All":
            threads = [t for t in threads if t['category'] in allowed]
            
        return {"success": True, "threads": threads}

    @staticmethod
    def get_access_categories(user_id):
        allowed = DiscussionModel.get_user_allowed_categories(user_id)
        return {"success": True, "categories": allowed}

    @staticmethod
    def create_thread(user_id, data):
        title = data.get('title')
        category = data.get('category', 'General Academic Discussions')
        content = data.get('content')
        
        if not title or not content:
            return {"success": False, "message": "Title and content are required."}
            
        success, result = DiscussionModel.create_thread(user_id, title, category, content)
        if not success:
            return {"success": False, "message": result}
            
        return {"success": True, "thread_id": result, "message": "Discussion thread created."}

    @staticmethod
    def add_comment(user_id, data):
        thread_id = data.get('thread_id')
        content = data.get('content')
        
        if not thread_id or not content:
            return {"success": False, "message": "Thread ID and content are required."}
            
        success, result = DiscussionModel.add_comment(thread_id, user_id, content)
        if not success:
            return {"success": False, "message": result}
            
        return {"success": True, "comment_id": result, "message": "Comment posted."}

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
        if not thread_id:
            return {"success": False, "message": "Thread ID required."}
        success, message = DiscussionModel.delete_thread(thread_id, user_id)
        return {"success": success, "message": message}

    @staticmethod
    def delete_comment(user_id, data):
        comment_id = data.get('comment_id')
        if not comment_id:
            return {"success": False, "message": "Comment ID required."}
        success, message = DiscussionModel.delete_comment(comment_id, user_id)
        return {"success": success, "message": message}
