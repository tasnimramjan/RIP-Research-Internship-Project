import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class MatchingModel:
    @staticmethod
    def calculate_match_score(student_interests, faculty_domains):
        if not student_interests or not faculty_domains:
            return 70
        s_set = set(i.lower().strip() for i in student_interests)
        f_set = set(d.lower().strip() for d in faculty_domains)
        if not s_set or not f_set:
            return 70
        overlap = s_set.intersection(f_set)
        if overlap:
            ratio = len(overlap) / max(len(s_set), 1)
            score = int(min(100, 60 + (ratio * 40)))
            return score
        partial_matches = 0
        for s in s_set:
            for f in f_set:
                if s in f or f in s:
                    partial_matches += 1
                    break
        if partial_matches > 0:
            return int(min(90, 50 + (partial_matches * 20)))
        return 65

    @staticmethod
    def search_all(keywords_str="", student_id=None):
        conn = get_db()
        cursor = conn.cursor()
        
        keywords = [k.strip() for k in keywords_str.split() if k.strip()] if keywords_str else []

        def build_like_clause(fields, kw_list):
            clauses = []
            params = []
            for kw in kw_list:
                kw_pattern = f"%{kw}%"
                field_clauses = [f"LOWER({f}) LIKE LOWER(?)" for f in fields]
                clauses.append("(" + " OR ".join(field_clauses) + ")")
                params.extend([kw_pattern] * len(fields))
            return " AND ".join(clauses), params

        if keywords:
            fac_fields = ["u.name", "f.designation", "f.research_domains"]
            fac_clause, fac_params = build_like_clause(fac_fields, keywords)
            fac_query = f"SELECT f.*, u.name, u.email, u.department FROM faculty f JOIN users u ON f.faculty_id = u.user_id WHERE {fac_clause}"
            
            lab_fields = ["rl.lab_name", "rl.focus_area", "rl.facilities", "u.name"]
            lab_clause, lab_params = build_like_clause(lab_fields, keywords)
            lab_query = f"SELECT rl.*, u.name as faculty_name FROM research_labs rl JOIN faculty f ON rl.faculty_id = f.faculty_id JOIN users u ON f.faculty_id = u.user_id WHERE {lab_clause}"
            
            thesis_fields = ["tg.group_name", "tg.topic", "tg.description"]
            thesis_clause, thesis_params = build_like_clause(thesis_fields, keywords)
            thesis_query = f"SELECT tg.* FROM thesis_groups tg WHERE {thesis_clause}"
            
            lp_fields = ["lp.title", "lp.description", "rl.lab_name"]
            lp_clause, lp_params = build_like_clause(lp_fields, keywords)
            lp_query = f"SELECT lp.project_id as id, lp.title, lp.description, 'Lab Project' as type, rl.lab_name as context FROM lab_projects lp JOIN research_labs rl ON lp.lab_id = rl.lab_id WHERE {lp_clause}"
            
            pp_fields = ["pp.idea_title", "pp.description", "pp.required_skills"]
            pp_clause, pp_params = build_like_clause(pp_fields, keywords)
            pp_query = f"SELECT pp.post_id as id, pp.idea_title as title, pp.description, 'Student Project' as type, pp.required_skills as context FROM project_posts pp WHERE {pp_clause}"
        else:
            fac_query = "SELECT f.*, u.name, u.email, u.department FROM faculty f JOIN users u ON f.faculty_id = u.user_id"
            fac_params = []
            lab_query = "SELECT rl.*, u.name as faculty_name FROM research_labs rl JOIN faculty f ON rl.faculty_id = f.faculty_id JOIN users u ON f.faculty_id = u.user_id"
            lab_params = []
            thesis_query = "SELECT tg.* FROM thesis_groups tg"
            thesis_params = []
            lp_query = "SELECT lp.project_id as id, lp.title, lp.description, 'Lab Project' as type, rl.lab_name as context FROM lab_projects lp JOIN research_labs rl ON lp.lab_id = rl.lab_id"
            lp_params = []
            pp_query = "SELECT pp.post_id as id, pp.idea_title as title, pp.description, 'Student Project' as type, pp.required_skills as context FROM project_posts pp"
            pp_params = []

        cursor.execute(fac_query, fac_params)
        faculty = [dict(row) for row in cursor.fetchall()]
        
        student_interests = []
        if student_id:
            cursor.execute("SELECT research_interests FROM students WHERE student_id = ?", (student_id,))
            s_row = cursor.fetchone()
            if s_row and s_row['research_interests']:
                try:
                    student_interests = json.loads(s_row['research_interests'])
                except Exception:
                    student_interests = []

        for f in faculty:
            f_domains = json.loads(f['research_domains']) if f.get('research_domains') else []
            f['research_domains'] = f_domains
            f['match_score'] = MatchingModel.calculate_match_score(student_interests, f_domains)

        cursor.execute(lab_query, lab_params)
        labs = [dict(row) for row in cursor.fetchall()]
        for l in labs:
            l['facilities'] = json.loads(l['facilities']) if l.get('facilities') else []

        cursor.execute(thesis_query, thesis_params)
        theses = [dict(row) for row in cursor.fetchall()]

        cursor.execute(lp_query, lp_params)
        lab_projs = [dict(row) for row in cursor.fetchall()]

        cursor.execute(pp_query, pp_params)
        student_projs = [dict(row) for row in cursor.fetchall()]

        conn.close()

        faculty.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        return {
            "faculty": faculty,
            "labs": labs,
            "theses": theses,
            "projects": lab_projs + student_projs
        }

    @staticmethod
    def update_student_interests(student_id, interests):
        conn = get_db()
        cursor = conn.cursor()
        if isinstance(interests, str):
            interests_list = [i.strip() for i in interests.split(',') if i.strip()]
        else:
            interests_list = interests or []
        json_str = json.dumps(interests_list)
        cursor.execute(
            "UPDATE students SET research_interests = ? WHERE student_id = ?",
            (json_str, student_id)
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_matched_students_for_faculty(faculty_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT research_domains FROM faculty WHERE faculty_id = ?", (faculty_id,))
        fac_row = cursor.fetchone()
        fac_domains = json.loads(fac_row['research_domains']) if fac_row and fac_row['research_domains'] else []

        cursor.execute("""
            SELECT s.student_id, s.cgpa, s.research_interests, u.name, u.email, u.department
            FROM students s
            JOIN users u ON s.student_id = u.user_id
            WHERE u.role = 'Student'
        """)
        student_rows = cursor.fetchall()
        conn.close()

        students = []
        for r in student_rows:
            item = dict(r)
            s_interests = json.loads(item['research_interests']) if item.get('research_interests') else []
            item['research_interests'] = s_interests
            item['match_score'] = MatchingModel.calculate_match_score(s_interests, fac_domains)
            students.append(item)

        students.sort(key=lambda x: x['match_score'], reverse=True)
        return students

    @staticmethod
    def get_admin_conversations():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, u1.name as sender_name, u2.name as receiver_name
            FROM chat_messages m
            LEFT JOIN users u1 ON m.sender_id = u1.user_id
            LEFT JOIN users u2 ON m.receiver_id = u2.user_id
            WHERE m.receiver_id IS NOT NULL
            ORDER BY m.timestamp DESC
            LIMIT 100
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

