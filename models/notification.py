import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class NotificationModel:
    @staticmethod
    def create_notification(user_id, title, message, category="General"):
        conn = get_db()
        cursor = conn.cursor()
        notif_id = "notif_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO notifications (notif_id, user_id, title, message, category, is_read, created_at) VALUES (?, ?, ?, ?, ?, 0, ?)",
            (notif_id, user_id, title, message, category, now)
        )
        conn.commit()
        conn.close()
        return notif_id

    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT * FROM notifications WHERE user_id = ?"
        params = [user_id]
        if unread_only:
            query += " AND is_read = 0"
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_as_read(notif_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE notif_id = ?", (notif_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Notification marked as read."}

    @staticmethod
    def mark_all_as_read(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "All notifications marked as read."}