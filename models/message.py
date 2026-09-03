import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class ChatMessageModel:
    @staticmethod
    def send_message(sender_id, receiver_id=None, group_id=None, message_text=""):
        conn = get_db()
        cursor = conn.cursor()
        msg_id = "msg_" + str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO chat_messages (message_id, sender_id, receiver_id, group_id, message_text, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (msg_id, sender_id, receiver_id, group_id, message_text, now)
        )
        conn.commit()
        conn.close()
        return msg_id

    @staticmethod
    def get_direct_messages(user1_id, user2_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT m.*, u.name as sender_name
        FROM chat_messages m
        LEFT JOIN users u ON m.sender_id = u.user_id
        WHERE (m.sender_id = ? AND m.receiver_id = ?)
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.timestamp ASC
        """, (user1_id, user2_id, user2_id, user1_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_group_messages(group_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT m.*, u.name as sender_name
        FROM chat_messages m
        LEFT JOIN users u ON m.sender_id = u.user_id
        WHERE m.group_id = ?
        ORDER BY m.timestamp ASC
        """, (group_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_user_conversations(user_id):
        import json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                CASE WHEN m.sender_id = ? THEN m.receiver_id ELSE m.sender_id END as partner_id,
                MAX(m.timestamp) as last_timestamp,
                m.message_text as last_message
            FROM chat_messages m
            WHERE (m.sender_id = ? OR m.receiver_id = ?) AND m.receiver_id IS NOT NULL
            GROUP BY partner_id
            ORDER BY last_timestamp DESC
        """, (user_id, user_id, user_id))
        summary_rows = [dict(r) for r in cursor.fetchall()]
        
        conversations = []
        for r in summary_rows:
            partner_id = r['partner_id']
            if not partner_id:
                continue
            cursor.execute("""
                SELECT u.user_id, u.name, u.email, u.department, u.role, s.cgpa, s.research_interests
                FROM users u
                LEFT JOIN students s ON u.user_id = s.student_id
                WHERE u.user_id = ?
            """, (partner_id,))
            u_row = cursor.fetchone()
            if u_row:
                item = dict(u_row)
                item['last_message'] = r['last_message']
                item['last_timestamp'] = r['last_timestamp']
                if item.get('research_interests'):
                    try:
                        item['research_interests'] = json.loads(item['research_interests'])
                    except Exception:
                        item['research_interests'] = []
                conversations.append(item)
                
        conn.close()
        return conversations

