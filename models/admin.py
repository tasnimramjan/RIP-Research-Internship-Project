import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class AdminModel:
    @staticmethod
    def get_all_users():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, email, department, role, status FROM users ORDER BY role, name")
        users = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return users

    @staticmethod
    def toggle_user_status(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"success": False, "message": "User not found."}
        
        current = row[0] if row[0] else 'Active'
        new_status = 'Suspended' if current == 'Active' else 'Active'
        cursor.execute("UPDATE users SET status = ? WHERE user_id = ?", (new_status, user_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": f"User status updated to {new_status}.", "status": new_status}

    @staticmethod
    def delete_user(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "User deleted successfully."}

    @staticmethod
    def edit_user(user_id, name, email, department, role):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = ?, email = ?, department = ?, role = ? WHERE user_id = ?",
            (name, email, department, role, user_id)
        )
        conn.commit()
        conn.close()
        return {"success": True, "message": "User information updated."}

    @staticmethod
    def delete_lab(lab_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ra_opportunities WHERE lab_id = ?", (lab_id,))
        cursor.execute("DELETE FROM lab_projects WHERE lab_id = ?", (lab_id,))
        cursor.execute("DELETE FROM research_labs WHERE lab_id = ?", (lab_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Research lab deleted successfully."}

    @staticmethod
    def delete_internship(opportunity_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM internship_applications WHERE opportunity_id = ?", (opportunity_id,))
        cursor.execute("DELETE FROM internship_opportunities WHERE opportunity_id = ?", (opportunity_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Internship opportunity deleted."}

    @staticmethod
    def delete_thesis_group(group_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE group_id = ?", (group_id,))
        cursor.execute("DELETE FROM thesis_group_members WHERE group_id = ?", (group_id,))
        cursor.execute("DELETE FROM thesis_groups WHERE group_id = ?", (group_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Thesis group deleted successfully."}

    @staticmethod
    def get_system_stats():
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Student'")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Faculty'")
        total_faculty = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_labs")
        total_labs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM internship_opportunities")
        total_internships = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM thesis_groups")
        total_groups = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_papers")
        total_papers = cursor.fetchone()[0]

        conn.close()
        return {
            "total_users": total_users,
            "total_students": total_students,
            "total_faculty": total_faculty,
            "total_labs": total_labs,
            "total_internships": total_internships,
            "total_groups": total_groups,
            "total_papers": total_papers
        }
