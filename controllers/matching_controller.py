import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.user import UserModel
from models.supervisor import SupervisorModel
from models.message import ChatMessageModel
from models.matching import MatchingModel

class MatchingController:
    @staticmethod
    def search(params):
        keywords = params.get('keywords', '')
        results = MatchingModel.search_all(keywords)
        results["success"] = True
        return results

    @staticmethod
    def match_student_with_faculty(student_id):
        student = UserModel.get_user_profile(student_id)
        if not student or student.get('role') != 'Student':
            return {"success": False, "message": "Student profile not found."}
            
        s_profile = student['student_profile']
        interests = s_profile.get('research_interests', [])
        cgpa = s_profile.get('cgpa', 3.0)
        
        supervisors = SupervisorModel.search_supervisors()
        
        matched_results = []
        for fac in supervisors:
            score = SupervisorModel.calculate_match_score(
                interests,
                fac['research_domains'],
                cgpa,
                fac['min_cgpa_req']
            )
            fac_copy = dict(fac)
            fac_copy['match_score'] = score
            matched_results.append(fac_copy)
            
        matched_results.sort(key=lambda x: x['match_score'], reverse=True)
        return {"success": True, "student_interests": interests, "matches": matched_results}

    @staticmethod
    def get_chat_history(user1_id, user2_id):
        messages = ChatMessageModel.get_direct_messages(user1_id, user2_id)
        return {"success": True, "messages": messages}

    @staticmethod
    def send_chat_message(sender_id, receiver_id, text):
        if not text or not text.strip():
            return {"success": False, "message": "Message text cannot be empty."}
        msg_id = ChatMessageModel.send_message(sender_id, receiver_id=receiver_id, message_text=text.strip())
        return {"success": True, "message_id": msg_id}
