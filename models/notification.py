import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class NotificationModel:
    @staticmethod
    def create_notification(user_id, notif_type, title, message, reference_id=None, sender_id=None):
        conn = get_db()
        cursor = conn.cursor()
        notif_id = "notif_" + str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO notifications (notification_id, user_id, type, title, message, reference_id, sender_id, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (notif_id, user_id, notif_type, title, message, reference_id, sender_id, now))
        conn.commit()
        conn.close()
        return notif_id

    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
            SELECT n.*, u.name as sender_name, u.role as sender_role
            FROM notifications n
            LEFT JOIN users u ON n.sender_id = u.user_id
            WHERE n.user_id = ?
        """
        params = [user_id]
        if unread_only:
            query += " AND n.is_read = 0"
        query += " ORDER BY n.created_at DESC LIMIT 50"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        notifs = [dict(r) for r in rows]

        cursor.execute("SELECT COUNT(*) as unread_count FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
        unread_row = cursor.fetchone()
        unread_count = unread_row['unread_count'] if unread_row else 0

        conn.close()
        return {"notifications": notifs, "unread_count": unread_count}

    @staticmethod
    def mark_as_read(notification_id, user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE notification_id = ? AND user_id = ?", (notification_id, user_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def mark_all_as_read(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete_notification(notification_id, user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notifications WHERE notification_id = ? AND user_id = ?", (notification_id, user_id))
        conn.commit()
        conn.close()
        return True
