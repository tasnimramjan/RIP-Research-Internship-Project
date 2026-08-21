import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class DashboardModel:
    @staticmethod
    def get_student_dashboard(student_id):
        conn = get_db()
        cursor = conn.cursor()
        
        # Deadlines & upcoming events
        cursor.execute("SELECT title, deadline, company_name FROM internship_opportunities ORDER BY deadline ASC LIMIT 3")
        internships = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute("SELECT title, event_date, location FROM events ORDER BY event_date ASC LIMIT 3")
        events = [dict(r) for r in cursor.fetchall()]
        
        # Recent group activities
        cursor.execute("""
            SELECT g.group_name, g.topic 
            FROM thesis_group_members m 
            JOIN thesis_groups g ON m.group_id = g.group_id 
            WHERE m.student_id = ?
        """, (student_id,))
        groups = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {
            "upcoming_internships": internships,
            "upcoming_events": events,
            "my_thesis_groups": groups,
            "quick_links": ["/supervisors", "/internships", "/papers", "/forums"]
        }

    @staticmethod
    def get_faculty_dashboard(faculty_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT remaining_slots, min_cgpa_req, thesis_available FROM faculty WHERE faculty_id = ?", (faculty_id,))
        fac_info = cursor.fetchone()
        conn.close()
        return {
            "status": dict(fac_info) if fac_info else {},
            "quick_links": ["/availability", "/labs", "/students"]
        }