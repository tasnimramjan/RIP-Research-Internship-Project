import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class AvailabilityModel:
    @staticmethod
    def search_availability(keywords_str, dept=None, domain=None, status=None):
        conn = get_db()
        cursor = conn.cursor()
        
        # Base query joining faculty, users, and research_labs
        query = """
            SELECT f.faculty_id, f.designation, f.research_domains, 
                   f.max_capacity, f.current_students, f.thesis_available,
                   u.name, u.department,
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
            
        # We will fetch all and filter keywords, domain, and status in Python 
        # since JSON array searching in SQLite is tricky without JSON1 extension.
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        
        keywords = [k.strip().lower() for k in (keywords_str or "").split() if k.strip()]
        domain = domain.lower() if domain else None
        
        for r in rows:
            item = dict(r)
            domains = json.loads(item['research_domains']) if item['research_domains'] else []
            
            # Calculate remaining slots & status
            max_cap = item['max_capacity']
            curr_students = item['current_students']
            remaining = max(0, max_cap - curr_students)
            
            item['remaining_slots'] = remaining
            item['research_domains'] = domains
            
            if remaining == 0:
                item['status'] = 'Full'
            elif remaining <= 2:
                item['status'] = 'Limited'
            else:
                item['status'] = 'Available'
                
            # Filter by Status
            if status and item['status'].lower() != status.lower():
                continue
                
            # Filter by Domain
            if domain:
                if not any(domain in d.lower() for d in domains):
                    continue
            
            # Filter by Keywords
            if keywords:
                # Need to match ALL keywords (AND logic)
                matches_all = True
                search_text = (
                    item['name'] + " " + 
                    item['designation'] + " " +
                    " ".join(domains) + " " +
                    (item['lab_name'] or "") + " " +
                    (item['focus_area'] or "")
                ).lower()
                
                for kw in keywords:
                    if kw not in search_text:
                        matches_all = False
                        break
                
                if not matches_all:
                    continue
                    
            results.append(item)
            
        return results
