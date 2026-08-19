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
