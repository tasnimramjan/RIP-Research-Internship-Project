import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class SupervisorModel:
    @staticmethod
    def search_supervisors(department=None, keyword=None, cgpa=None, availability_only=False):
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
        SELECT u.user_id, u.name, u.email, u.department, f.designation, f.h_index, 
               f.research_domains, f.remaining_slots, f.min_cgpa_req, f.thesis_available,
               COALESCE(f.max_capacity, 5) as max_capacity, COALESCE(f.current_students, 0) as current_students
        FROM faculty f
        JOIN users u ON f.faculty_id = u.user_id
        WHERE 1=1
        """
        params = []
        
        if department:
            query += " AND u.department = ?"
            params.append(department)
            
        if availability_only:
            query += " AND f.thesis_available = 1 AND f.remaining_slots > 0"
            
        if cgpa is not None:
            query += " AND f.min_cgpa_req <= ?"
            params.append(float(cgpa))
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            item = dict(r)
            domains_raw = item.get('research_domains')
            domains = []
            if domains_raw:
                if isinstance(domains_raw, list):
                    domains = domains_raw
                else:
                    try:
                        res = json.loads(domains_raw)
                        domains = res if isinstance(res, list) else []
                    except Exception:
                        if isinstance(domains_raw, str):
                            domains = [d.strip() for d in domains_raw.split(',') if d.strip()]
            item['research_domains'] = domains
            
            max_cap = item.get('max_capacity') if item.get('max_capacity') is not None else 5
            curr_students = item.get('current_students') if item.get('current_students') is not None else 0
            rem_slots = max(0, max_cap - curr_students)
            item['max_capacity'] = max_cap
            item['current_students'] = curr_students
            item['remaining_slots'] = rem_slots
            
            # Keyword filter (in domains, name, designation)
            if keyword:
                kw = keyword.lower()
                matches = (
                    kw in item['name'].lower() or
                    kw in item['designation'].lower() or
                    any(kw in d.lower() for d in domains)
                )
                if not matches:
                    continue
                    
            results.append(item)
            
        return results

    @staticmethod
    def update_availability(faculty_id, slots=None, thesis_available=None, min_cgpa_req=None):
        conn = get_db()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if slots is not None:
            updates.append("remaining_slots = ?")
            params.append(int(slots))
        if thesis_available is not None:
            updates.append("thesis_available = ?")
            params.append(1 if thesis_available else 0)
        if min_cgpa_req is not None:
            updates.append("min_cgpa_req = ?")
            params.append(float(min_cgpa_req))
            
        if not updates:
            conn.close()
            return False
            
        params.append(faculty_id)
        sql = f"UPDATE faculty SET {', '.join(updates)} WHERE faculty_id = ?"
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def update_faculty_profile(faculty_id, designation=None, h_index=None, research_domains=None, remaining_slots=None, min_cgpa_req=None, thesis_available=None, name=None, department=None, max_capacity=None):
        conn = get_db()
        cursor = conn.cursor()

        # Fetch existing record for remaining_slots calculation
        cursor.execute("SELECT max_capacity, current_students, thesis_available FROM faculty WHERE faculty_id = ?", (faculty_id,))
        row = cursor.fetchone()
        ex_max = row['max_capacity'] if row and row['max_capacity'] is not None else 5
        ex_curr = row['current_students'] if row and row['current_students'] is not None else 0
        ex_t = row['thesis_available'] if row and row['thesis_available'] is not None else 1

        new_max = int(max_capacity) if max_capacity is not None else ex_max
        new_t = (1 if thesis_available else 0) if thesis_available is not None else ex_t
        calc_rem = max(0, new_max - ex_curr)

        # Update users table if name or department are provided
        if name is not None or department is not None:
            user_updates = []
            user_params = []
            if name is not None and name.strip():
                user_updates.append("name = ?")
                user_params.append(name.strip())
            if department is not None and department.strip():
                user_updates.append("department = ?")
                user_params.append(department.strip())
            if user_updates:
                user_params.append(faculty_id)
                cursor.execute(f"UPDATE users SET {', '.join(user_updates)} WHERE user_id = ?", user_params)

        updates = []
        params = []
        if designation is not None:
            updates.append("designation = ?")
            params.append(designation)
        if h_index is not None:
            updates.append("h_index = ?")
            params.append(int(h_index))
        if research_domains is not None:
            if isinstance(research_domains, str):
                research_domains = [d.strip() for d in research_domains.split(',') if d.strip()]
            updates.append("research_domains = ?")
            params.append(json.dumps(research_domains))
        
        updates.append("remaining_slots = ?")
        params.append(calc_rem)

        if max_capacity is not None:
            updates.append("max_capacity = ?")
            params.append(new_max)
        if min_cgpa_req is not None:
            updates.append("min_cgpa_req = ?")
            params.append(float(min_cgpa_req))
        if thesis_available is not None:
            updates.append("thesis_available = ?")
            params.append(new_t)

        if updates:
            params.append(faculty_id)
            sql = f"UPDATE faculty SET {', '.join(updates)} WHERE faculty_id = ?"
            cursor.execute(sql, params)

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def calculate_match_score(student_interests, faculty_domains, student_cgpa, min_cgpa_req):
        if student_cgpa < min_cgpa_req:
            return 0
            
        s_set = set(i.lower().strip() for i in student_interests)
        f_set = set(d.lower().strip() for d in faculty_domains)
        
        if not s_set or not f_set:
            return 20
            
        intersection = s_set.intersection(f_set)
        # Jaccard + domain overlap ratio
        overlap_score = len(intersection) / max(len(s_set), 1)
        
        # CGPA bonus
        cgpa_bonus = min(15, (student_cgpa - min_cgpa_req) * 20)
        
        total_score = int(min(100, (overlap_score * 80) + 15 + cgpa_bonus))
        return total_score
