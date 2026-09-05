import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

def safe_parse_domains(val):
    if not val:
        return []
    if isinstance(val, list):
        return val
    try:
        res = json.loads(val)
        return res if isinstance(res, list) else []
    except Exception:
        if isinstance(val, str):
            return [d.strip() for d in val.split(',') if d.strip()]
        return []

class AvailabilityModel:
    @staticmethod
    def search_availability(keywords_str="", dept=None, domain=None, status=None):
        conn = get_db()
        cursor = conn.cursor()
        
        # Query joining faculty, users, and research_labs
        query = """
            SELECT f.faculty_id, f.designation, f.research_domains, 
                   f.max_capacity, f.current_students, f.thesis_available,
                   f.remaining_slots, f.min_cgpa_req, f.h_index,
                   u.name, u.email, u.department,
                   rl.lab_name, rl.focus_area
            FROM faculty f
            JOIN users u ON f.faculty_id = u.user_id
            LEFT JOIN research_labs rl ON f.faculty_id = rl.faculty_id
            WHERE 1=1
        """
        params = []
        
        if dept:
            query += " AND LOWER(u.department) = LOWER(?)"
            params.append(dept)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        keywords = [k.strip().lower() for k in (keywords_str or "").split() if k.strip()]
        domain = domain.lower() if domain else None
        
        for r in rows:
            item = dict(r)
            domains = safe_parse_domains(item.get('research_domains'))
            
            max_cap = item.get('max_capacity') if item.get('max_capacity') is not None else 5
            curr_students = item.get('current_students') if item.get('current_students') is not None else 0
            
            rem_slots = max(0, max_cap - curr_students)
            if rem_slots == 0:
                item['status'] = 'Full'
            elif rem_slots <= 2:
                item['status'] = 'Limited'
            else:
                item['status'] = 'Available'

            item['max_capacity'] = max_cap
            item['current_students'] = curr_students
            item['remaining_slots'] = rem_slots
            item['research_domains'] = domains
            
            # Filter by Status
            if status and item['status'].lower() != status.lower():
                continue
                
            # Filter by Domain
            if domain:
                if not any(domain in d.lower() for d in domains):
                    continue
            
            # Filter by Keywords
            if keywords:
                search_text = (
                    (item.get('name') or "") + " " + 
                    (item.get('designation') or "") + " " +
                    (item.get('department') or "") + " " +
                    " ".join(domains) + " " +
                    (item.get('lab_name') or "") + " " +
                    (item.get('focus_area') or "")
                ).lower()
                
                matches_all = True
                for kw in keywords:
                    if kw not in search_text:
                        matches_all = False
                        break
                
                if not matches_all:
                    continue
                    
            results.append(item)
            
        return results

    @staticmethod
    def update_availability_record(faculty_id, max_capacity=None, current_students=None, remaining_slots=None, thesis_available=None, designation=None, research_domains=None, min_cgpa_req=None):
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT max_capacity, current_students, thesis_available FROM faculty WHERE faculty_id = ?", (faculty_id,))
        ex = cursor.fetchone()
        ex_max = ex['max_capacity'] if ex and ex['max_capacity'] is not None else 5
        ex_curr = ex['current_students'] if ex and ex['current_students'] is not None else 0
        ex_t = ex['thesis_available'] if ex and ex['thesis_available'] is not None else 1

        new_max = int(max_capacity) if max_capacity is not None else ex_max
        new_curr = int(current_students) if current_students is not None else ex_curr
        new_t = (1 if thesis_available else 0) if thesis_available is not None else ex_t

        calc_rem = max(0, new_max - new_curr)

        updates = []
        params = []
        
        if max_capacity is not None:
            updates.append("max_capacity = ?")
            params.append(new_max)
        if current_students is not None:
            updates.append("current_students = ?")
            params.append(new_curr)
            
        updates.append("remaining_slots = ?")
        params.append(calc_rem)
            
        if thesis_available is not None:
            updates.append("thesis_available = ?")
            params.append(new_t)
        if designation is not None:
            updates.append("designation = ?")
            params.append(designation)
        if research_domains is not None:
            if isinstance(research_domains, str):
                research_domains = [d.strip() for d in research_domains.split(',') if d.strip()]
            updates.append("research_domains = ?")
            params.append(json.dumps(research_domains))
        if min_cgpa_req is not None:
            updates.append("min_cgpa_req = ?")
            params.append(float(min_cgpa_req))

        if updates:
            params.append(faculty_id)
            sql = f"UPDATE faculty SET {', '.join(updates)} WHERE faculty_id = ?"
            cursor.execute(sql, params)
            conn.commit()

        conn.close()
        return True
