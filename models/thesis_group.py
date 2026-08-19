import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class ThesisGroupModel:
    @staticmethod
    def get_all_groups(topic_filter=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT g.*, u.name as creator_name, u.email as creator_email, u.department
        FROM thesis_groups g
        JOIN users u ON g.creator_id = u.user_id
        ORDER BY g.created_at DESC
        """)
        rows = cursor.fetchall()
        
        groups = []
        for r in rows:
            g = dict(r)
            if topic_filter:
                tf = topic_filter.lower().strip()
                if not (tf in g['topic'].lower() or tf in g['group_name'].lower()):
                    continue
                    
            cursor.execute("""
            SELECT m.*, u.name as student_name, u.email, s.cgpa
            FROM thesis_group_members m
            JOIN users u ON m.student_id = u.user_id
            JOIN students s ON m.student_id = s.student_id
            WHERE m.group_id = ?
            """, (g['group_id'],))
            g['members'] = [dict(m) for m in cursor.fetchall()]
            
            groups.append(g)
            
        conn.close()
        return groups

    @staticmethod
    def create_group(creator_id, group_name, topic, description):
        conn = get_db()
        cursor = conn.cursor()
        group_id = "grp_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO thesis_groups (group_id, group_name, topic, description, creator_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (group_id, group_name, topic, description, creator_id, now)
        )
        cursor.execute(
            "INSERT INTO thesis_group_members (group_id, student_id, joined_at) VALUES (?, ?, ?)",
            (group_id, creator_id, now)
        )
        conn.commit()
        conn.close()
        return group_id

    @staticmethod
    def join_group(group_id, student_id):
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute(
                "INSERT INTO thesis_group_members (group_id, student_id, joined_at) VALUES (?, ?, ?)",
                (group_id, student_id, now)
            )
            conn.commit()
            success = True
            msg = "Joined thesis group successfully."
        except Exception:
            success = False
            msg = "You are already a member of this thesis group."
        finally:
            conn.close()
        return {"success": success, "message": msg}

    @staticmethod
    def leave_group(group_id, student_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM thesis_group_members WHERE group_id = ? AND student_id = ?", (group_id, student_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": "You have left the thesis study circle."}
