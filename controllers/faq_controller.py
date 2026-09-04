import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.faq import FAQChatbotModel

class FAQController:
    @staticmethod
    def ask_question(data):
        query = data.get('question')
        if not query or not query.strip():
            return {"success": False, "message": "Question context cannot be empty."}

        result = FAQChatbotModel.query_bot(query)
        return {"success": True, "data": result}