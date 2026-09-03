import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.message import ChatMessageModel
from db import get_db

class MessageController:
    @staticmethod
    def send_message(data):
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        message_text = data.get('message_text')
        
        if not sender_id or not receiver_id or not message_text:
            return {"success": False, "message": "Sender, receiver, and message text are required."}
            
        from models.user import UserModel
        sender = UserModel.get_by_id(sender_id)
        receiver = UserModel.get_by_id(receiver_id)
        if not sender or not receiver:
            return {"success": False, "message": "Invalid sender or receiver."}

        s_role = sender.get('role')
        r_role = receiver.get('role')

        if (s_role == 'Student' and r_role == 'Faculty') or (s_role == 'Faculty' and r_role == 'Student'):
            msg_id = ChatMessageModel.send_message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                message_text=message_text
            )
            return {"success": True, "message_id": msg_id, "message": "Message sent."}
        else:
            return {"success": False, "message": "Direct messaging is strictly permitted only between students and faculty members."}


    @staticmethod
    def get_direct_messages(user1_id, user2_id):
        if not user1_id or not user2_id:
            return {"success": False, "message": "Both user IDs are required."}
            
        messages = ChatMessageModel.get_direct_messages(user1_id, user2_id)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE user_id = ?", (user2_id,))
        row = cursor.fetchone()
        receiver_name = row['name'] if row else "Unknown User"
        conn.close()
        
        return {"success": True, "messages": messages, "chat_with": receiver_name}

    @staticmethod
    def get_user_conversations(user_id):
        if not user_id:
            return {"success": False, "message": "User ID is required."}
        conversations = ChatMessageModel.get_user_conversations(user_id)
        return {"success": True, "conversations": conversations}

