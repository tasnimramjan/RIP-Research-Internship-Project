import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class AdminPanelModel:
    @staticmethod
    def get_all_users():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, email, department, role, is_active FROM users ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def toggle_user_status(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"success": False, "message": "User not found."}
        
        new_status = 0 if row['is_active'] == 1 else 1
        cursor.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (new_status, user_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": f"User status updated to {new_status}."}

    @staticmethod
    def verify_faculty(faculty_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE faculty SET verified = 1 WHERE faculty_id = ?", (faculty_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Faculty profile verified."}

    @staticmethod
    def delete_discussion(thread_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM discussion_threads WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM thread_comments WHERE thread_id = ?", (thread_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Discussion moderated and deleted."}

    @staticmethod
    def get_system_analytics():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as u_cnt FROM users")
        users = cursor.fetchone()['u_cnt']
        cursor.execute("SELECT COUNT(*) as e_cnt FROM events")
        events = cursor.fetchone()['e_cnt']
        conn.close()
        return {"total_users": users, "total_events": events}