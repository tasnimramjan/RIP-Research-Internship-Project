import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.thesis_group import ThesisGroupModel
from models.message import ChatMessageModel

class ThesisGroupController:
    @staticmethod
    def get_groups(topic=None):
        groups = ThesisGroupModel.get_all_groups(topic_filter=topic)
        return {"success": True, "count": len(groups), "groups": groups}

    @staticmethod
    def create_group(student_id, data):
        g_name = data.get('group_name')
        topic = data.get('topic')
        desc = data.get('description')
        
        if not g_name or not topic or not desc:
            return {"success": False, "message": "Group name, topic, and description are required."}
            
        group_id = ThesisGroupModel.create_group(student_id, g_name, topic, desc)
        return {"success": True, "group_id": group_id, "message": "Thesis group created successfully."}

    @staticmethod
    def join_group(group_id, student_id):
        res = ThesisGroupModel.join_group(group_id, student_id)
        return res

    @staticmethod
    def leave_group(group_id, student_id):
        res = ThesisGroupModel.leave_group(group_id, student_id)
        return res

    @staticmethod
    def get_group_messages(group_id):
        messages = ChatMessageModel.get_group_messages(group_id)
        return {"success": True, "messages": messages}

    @staticmethod
    def send_group_message(sender_id, group_id, text):
        if not text or not text.strip():
            return {"success": False, "message": "Message text cannot be empty."}
        msg_id = ChatMessageModel.send_message(sender_id, group_id=group_id, message_text=text.strip())
        return {"success": True, "message_id": msg_id}
