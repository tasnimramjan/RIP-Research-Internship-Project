import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class MatchingModel:
    @staticmethod
    def search_all(keywords_str):
        keywords = []
        if keywords_str:
            keywords = [k.strip() for k in keywords_str.split() if k.strip()]

        conn = get_db()
        
        # Build conditions for ANDing keywords
        def build_like_clause(fields, kw_list):
            if not kw_list:
                return "1=1", []
            # For each keyword, it must appear in AT LEAST ONE of the fields
            # Returns a clause string and parameters
            clauses = []
            params = []
            for kw in kw_list:
                kw_pattern = f"%{kw}%"
                field_clauses = [f"LOWER({f}) LIKE LOWER(?)" for f in fields]
                clauses.append("(" + " OR ".join(field_clauses) + ")")
                params.extend([kw_pattern] * len(fields))
            return " AND ".join(clauses), params

        # 1. Faculty
        fac_fields = ["u.name", "f.designation", "f.research_domains"]
        fac_clause, fac_params = build_like_clause(fac_fields, keywords)
        fac_query = f"""
            SELECT f.*, u.name, u.email, u.department 
            FROM faculty f 
            JOIN users u ON f.faculty_id = u.user_id 
            WHERE {fac_clause}
        """
        
        # 2. Labs
        lab_fields = ["rl.lab_name", "rl.focus_area", "rl.facilities", "u.name"]
        lab_clause, lab_params = build_like_clause(lab_fields, keywords)
        lab_query = f"""
            SELECT rl.*, u.name as faculty_name
            FROM research_labs rl
            JOIN faculty f ON rl.faculty_id = f.faculty_id
            JOIN users u ON f.faculty_id = u.user_id
            WHERE {lab_clause}
        """
        
        # 3. Thesis Groups
        thesis_fields = ["tg.group_name", "tg.topic", "tg.description"]
        thesis_clause, thesis_params = build_like_clause(thesis_fields, keywords)
        thesis_query = f"""
            SELECT tg.*
            FROM thesis_groups tg
            WHERE {thesis_clause}
        """
        
        # 4. Projects (Lab Projects + Project Posts)
        # Lab Projects
        lp_fields = ["lp.title", "lp.description", "rl.lab_name"]
        lp_clause, lp_params = build_like_clause(lp_fields, keywords)
        lp_query = f"""
            SELECT lp.project_id as id, lp.title, lp.description, 'Lab Project' as type, rl.lab_name as context
            FROM lab_projects lp
            JOIN research_labs rl ON lp.lab_id = rl.lab_id
            WHERE {lp_clause}
        """
        
        # Project Posts
        pp_fields = ["pp.idea_title", "pp.description", "pp.required_skills"]
        pp_clause, pp_params = build_like_clause(pp_fields, keywords)
        pp_query = f"""
            SELECT pp.post_id as id, pp.idea_title as title, pp.description, 'Student Project' as type, pp.required_skills as context
            FROM project_posts pp
            WHERE {pp_clause}
        """
        
        cursor = conn.cursor()
        
        from models.faculty import parse_json_list
        cursor.execute(fac_query, fac_params)
        faculty = [dict(row) for row in cursor.fetchall()]
        for f in faculty:
            f['research_domains'] = parse_json_list(f.get('research_domains'))
            
        cursor.execute(lab_query, lab_params)
        labs = [dict(row) for row in cursor.fetchall()]
        for l in labs:
            l['facilities'] = parse_json_list(l.get('facilities'))
            
        cursor.execute(thesis_query, thesis_params)
        thesis = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute(lp_query, lp_params)
        lab_projs = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute(pp_query, pp_params)
        student_projs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "faculty": faculty,
            "labs": labs,
            "thesis": thesis,
            "projects": lab_projs + student_projs
        }
