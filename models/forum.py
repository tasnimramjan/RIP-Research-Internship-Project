import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class DiscussionModel:
    @staticmethod
    def get_threads(category=None):
        conn = get_db()
        cursor = conn.cursor()
        query = """
        SELECT t.*, u.name as author_name, u.role as author_role, u.department
        FROM discussion_threads t
        JOIN users u ON t.user_id = u.user_id
        """
        params = []
        if category and category != "All":
            query += " WHERE t.category = ?"
            params.append(category)
            
        query += " ORDER BY t.created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        threads = []
        for r in rows:
            t = dict(r)
            
            # Fetch comments
            cursor.execute("""
            SELECT c.*, u.name as author_name, u.role as author_role
            FROM forum_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.thread_id = ?
            ORDER BY c.created_at ASC
            """, (t['thread_id'],))
            t['comments'] = [dict(c) for c in cursor.fetchall()]
            
            # Fetch reaction counts
            cursor.execute("""
            SELECT reaction_type, COUNT(*) as count
            FROM forum_reactions
            WHERE thread_id = ?
            GROUP BY reaction_type
            """, (t['thread_id'],))
            t['reactions'] = {r_row['reaction_type']: r_row['count'] for r_row in cursor.fetchall()}
            
            threads.append(t)
            
        conn.close()
        return threads

    @staticmethod
    def create_thread(user_id, title, category, content):
        conn = get_db()
        cursor = conn.cursor()
        thread_id = "th_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO discussion_threads (thread_id, user_id, title, category, content, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (thread_id, user_id, title, category, content, now)
        )
        conn.commit()
        conn.close()
        return thread_id

    @staticmethod
    def add_comment(thread_id, user_id, content):
        conn = get_db()
        cursor = conn.cursor()
        comment_id = "c_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO forum_comments (comment_id, thread_id, user_id, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (comment_id, thread_id, user_id, content, now)
        )
        conn.commit()
        conn.close()
        return comment_id

    @staticmethod
    def add_reaction(thread_id, user_id, reaction_type):
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute("SELECT * FROM forum_reactions WHERE thread_id=? AND user_id=? AND reaction_type=?", (thread_id, user_id, reaction_type))
        row = cursor.fetchone()
        
        if row:
            # Unlike
            cursor.execute("DELETE FROM forum_reactions WHERE thread_id=? AND user_id=? AND reaction_type=?", (thread_id, user_id, reaction_type))
            action = "removed"
        else:
            # Like
            cursor.execute(
                "INSERT INTO forum_reactions (thread_id, user_id, reaction_type) VALUES (?, ?, ?)",
                (thread_id, user_id, reaction_type)
            )
            action = "added"
            
        conn.commit()
        conn.close()
        return True, action

    @staticmethod
    def set_reminder(thread_id, user_id, remind_at, note=None):
        conn = get_db()
        cursor = conn.cursor()
        reminder_id = "rem_" + str(uuid.uuid4())[:6]
        cursor.execute(
            "INSERT INTO thread_reminders (reminder_id, thread_id, user_id, remind_at, note) VALUES (?, ?, ?, ?, ?)",
            (reminder_id, thread_id, user_id, remind_at, note or "Forum Thread Reminder")
        )
        conn.commit()
        conn.close()
        return reminder_id

    @staticmethod
    def get_due_reminders(user_id):
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            SELECT r.*, t.title as thread_title 
            FROM thread_reminders r
            JOIN discussion_threads t ON r.thread_id = t.thread_id
            WHERE r.user_id = ? AND r.is_triggered = 0 AND r.remind_at <= ?
        """, (user_id, now))
        reminders = [dict(r) for r in cursor.fetchall()]
        
        # Mark as triggered
        if reminders:
            ids = [r['reminder_id'] for r in reminders]
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"UPDATE thread_reminders SET is_triggered = 1 WHERE reminder_id IN ({placeholders})", ids)
            conn.commit()
            
        conn.close()
        return reminders
