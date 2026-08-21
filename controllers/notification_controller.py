import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.notification import NotificationModel

class NotificationController:
    @staticmethod
    def fetch_notifications(user_id, unread_only=False):
        notifs = NotificationModel.get_user_notifications(user_id, unread_only=unread_only)
        return {"success": True, "count": len(notifs), "notifications": notifs}

    @staticmethod
    def send_notification(data):
        user_id = data.get('user_id')
        title = data.get('title')
        msg = data.get('message')
        cat = data.get('category', 'Announcement')
        
        if not user_id or not title or not msg:
            return {"success": False, "message": "User ID, title, and message text are required."}
            
        nid = NotificationModel.create_notification(user_id, title, msg, category=cat)
        return {"success": True, "notif_id": nid, "message": "Notification dispatched."}

    @staticmethod
    def mark_read(notif_id):
        return NotificationModel.mark_as_read(notif_id)

    @staticmethod
    def mark_all_read(user_id):
        return NotificationModel.mark_all_as_read(user_id)