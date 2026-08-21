import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class FAQChatbotModel:
    KNOWLEDGE_BASE = [
        {
            "keywords": ["thesis", "supervisor", "find", "select"],
            "answer": "You can find supervisors via the Supervisor Finder. Filter faculty by department, domain keywords, and minimum CGPA."
        },
        {
            "keywords": ["internship", "apply", "job", "career"],
            "answer": "Browse open postings in the Internship Portal. Check minimum CGPA requirements and click 'Apply Now' before the deadline."
        },
        {
            "keywords": ["paper", "research", "semantic", "citation"],
            "answer": "Use Paper Discovery to search research documents by keywords or semantic queries. You can export citations in IEEE, APA, or MLA."
        },
        {
            "keywords": ["teammate", "project", "group", "post"],
            "answer": "Post your project idea or required skills in the Teammate Finder, or join existing project circles."
        },
        {
            "keywords": ["faq", "help", "contact", "support"],
            "answer": "This portal helps you navigate thesis management, faculty matching, internships, and research collaborations."
        }
    ]

    @staticmethod
    def query_bot(user_message):
        msg = user_message.lower().strip()
        best_match = None
        max_score = 0

        for item in FAQChatbotModel.KNOWLEDGE_BASE:
            score = sum(1 for kw in item["keywords"] if kw in msg)
            if score > max_score:
                max_score = score
                best_match = item["answer"]

        if not best_match:
            best_match = "I'm sorry, I couldn't find specific instructions for that query. Please check the resource library or consult academic admin."

        return {"query": user_message, "response": best_match}