import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.notification import NotificationModel

class NotificationController:
    @staticmethod
    def get_notifications(user_id):
        if not user_id:
            return {"success": False, "message": "User ID is required."}
        data = NotificationModel.get_user_notifications(user_id)
        return {"success": True, "notifications": data["notifications"], "unread_count": data["unread_count"]}

    @staticmethod
    def mark_as_read(data):
        notif_id = data.get('notification_id')
        user_id = data.get('user_id')
        if not notif_id or not user_id:
            return {"success": False, "message": "Notification ID and User ID required."}
        NotificationModel.mark_as_read(notif_id, user_id)
        return {"success": True, "message": "Marked as read."}

    @staticmethod
    def mark_all_as_read(data):
        user_id = data.get('user_id')
        if not user_id:
            return {"success": False, "message": "User ID required."}
        NotificationModel.mark_all_as_read(user_id)
        return {"success": True, "message": "All notifications marked as read."}

    @staticmethod
    def delete_notification(data):
        notif_id = data.get('notification_id')
        user_id = data.get('user_id')
        if not notif_id or not user_id:
            return {"success": False, "message": "Notification ID and User ID required."}
        NotificationModel.delete_notification(notif_id, user_id)
        return {"success": True, "message": "Notification dismissed."}