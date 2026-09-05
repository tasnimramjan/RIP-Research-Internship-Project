import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class FAQChatbotModel:
    KNOWLEDGE_BASE = [
        {"keywords": ["find", "select", "choose", "supervisor"],
         "answer": "You can find supervisors via the Smart Supervisor Finder. Filter faculty by department, domain keywords, and minimum CGPA."},
        {"keywords": ["available", "slots", "capacity", "supervisor"],
         "answer": "Check the Availability Tracker to see each faculty member's remaining thesis supervision slots before applying."},
        {"keywords": ["how", "long", "take", "duration", "thesis"],
         "answer": "Thesis duration varies by department, but generally spans proposal, literature review, implementation, writing, and defense — check the Thesis Progress Tracker for a milestone breakdown."},
        {"keywords": ["thesis", "process", "steps", "stages"],
         "answer": "The thesis process is tracked in stages: Proposal, Literature Review, Implementation, Writing, Submission, and Defense Preparation — see the Thesis Progress Tracker tab."},
        {"keywords": ["internship", "apply", "job", "career"],
         "answer": "Browse open postings in the Internship Portal. Check minimum CGPA requirements and click 'Apply Now' before the deadline."},
        {"keywords": ["internship", "requirement", "eligibility", "cgpa"],
         "answer": "Each internship posting lists its own minimum CGPA and requirements — check the listing details in the Internship Portal before applying."},
        {"keywords": ["paper", "research", "semantic", "search"],
         "answer": "Use Paper Discovery to search research documents by keywords or semantic queries."},
        {"keywords": ["citation", "reference", "export", "cite"],
         "answer": "You can export citations in IEEE, APA, or MLA format from the Citation & Reference Manager."},
        {"keywords": ["teammate", "project", "group", "post"],
         "answer": "Post your project idea or required skills in the Teammate Finder, or join existing project circles."},
        {"keywords": ["thesis", "group", "study", "circle"],
         "answer": "Use the Thesis Group Finder to connect with students working on similar topics and form a group or study circle."},
        {"keywords": ["event", "conference", "workshop", "register"],
         "answer": "Check the Research Event & Conference Hub for upcoming seminars, workshops, and conferences, and register directly there."},
        {"keywords": ["notification", "alert", "update"],
         "answer": "The Notification Center shows updates on messages, deadlines, and event registrations in real time."},
        {"keywords": ["faq", "help", "contact", "support"],
         "answer": "This portal helps you navigate thesis management, faculty matching, internships, and research collaborations."},
    ]

    @staticmethod
    def query_bot(user_message):
        msg = user_message.lower().strip()
        best_match = None
        best_score = 0.0

        def score_entry(keywords):
            hits = sum(1 for kw in keywords if kw in msg)
            if hits == 0:
                return 0.0
            return hits / len(keywords)

        for item in FAQChatbotModel.KNOWLEDGE_BASE:
            s = score_entry(item["keywords"])
            if s > best_score:
                best_score = s
                best_match = item["answer"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT keywords, answer FROM faq_chatbot")
        for row in cursor.fetchall():
            kws = [k.strip() for k in row["keywords"].split(",")]
            s = score_entry(kws)
            if s > best_score:
                best_score = s
                best_match = row["answer"]
        conn.close()

        if not best_match or best_score < 0.2:
            best_match = "I'm sorry, I couldn't find specific instructions for that query. Please check the resource library or consult academic admin."

        return {"query": user_message, "response": best_match}