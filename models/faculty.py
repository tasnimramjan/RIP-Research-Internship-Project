import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

def parse_json_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, str):
                return [s.strip() for s in parsed.split(',') if s.strip()]
        except Exception:
            return [s.strip() for s in value.split(',') if s.strip()]
    return []

class FacultyModel:
    @staticmethod
    def search_faculty(keywords=None, department=None, domain=None, lab_name=None):
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
        SELECT u.user_id, u.name, u.email, u.department, 
               f.designation, f.h_index, f.research_domains, 
               f.remaining_slots, f.min_cgpa_req, f.thesis_available,
               COALESCE(f.is_verified, 1) as is_verified
        FROM faculty f
        JOIN users u ON f.faculty_id = u.user_id
        WHERE u.role = 'Faculty'
        """
        
        cursor.execute(query)
        faculty_rows = cursor.fetchall()
        
        # Fetch labs
        cursor.execute("SELECT lab_id, lab_name, focus_area, facilities, faculty_id FROM research_labs")
        labs = cursor.fetchall()
        lab_dict = {}
        for lab in labs:
            fac_id = lab['faculty_id']
            if fac_id not in lab_dict:
                lab_dict[fac_id] = []
            
            lab_copy = dict(lab)
            lab_copy['facilities'] = parse_json_list(lab_copy['facilities'])
            lab_dict[fac_id].append(lab_copy)
            
        # Fetch papers
        cursor.execute("SELECT paper_id, title, authors, domain, publication_year, faculty_id FROM research_papers")
        papers = cursor.fetchall()
        
        conn.close()
        
        results = []
        for f in faculty_rows:
            item = dict(f)
            domains = parse_json_list(item['research_domains'])
            item['research_domains'] = domains
            
            # Associate labs
            item['directed_labs'] = lab_dict.get(item['user_id'], [])
            
            # Associate papers
            faculty_papers = []
            for p in papers:
                p_dict = dict(p)
                p_authors = parse_json_list(p_dict['authors'])
                p_dict['authors'] = p_authors
                
                is_author = any(item['name'].lower() in author.lower() for author in p_authors)
                is_fac_paper = (p_dict.get('faculty_id') == item['user_id'])
                
                if is_author or is_fac_paper:
                    faculty_papers.append(p_dict)
            
            item['publications'] = faculty_papers
            
            # Filter by department
            if department and item['department'].lower() != department.lower():
                continue
                
            # Filter by domain
            if domain and not any(domain.lower() in d.lower() for d in domains):
                continue
                
            # Filter by lab name/focus
            if lab_name:
                has_lab_match = False
                for l in item['directed_labs']:
                    if lab_name.lower() in l['lab_name'].lower() or lab_name.lower() in l['focus_area'].lower():
                        has_lab_match = True
                        break
                if not has_lab_match:
                    continue
            
            # Filter by keywords
            if keywords:
                kw_list = [k.strip().lower() for k in keywords.split() if k.strip()]
                matched_all = True
                for kw in kw_list:
                    match_found = False
                    if kw in item['name'].lower() or kw in item['email'].lower() or kw in item['department'].lower() or kw in item['designation'].lower():
                        match_found = True
                    elif any(kw in d.lower() for d in domains):
                        match_found = True
                    else:
                        for l in item['directed_labs']:
                            if kw in l['lab_name'].lower() or kw in l['focus_area'].lower():
                                match_found = True
                                break
                        if not match_found:
                            for p in faculty_papers:
                                if kw in p['title'].lower() or kw in p['domain'].lower():
                                    match_found = True
                                    break
                    
                    if not match_found:
                        matched_all = False
                        break
                
                if not matched_all:
                    continue
                    
            results.append(item)
            
        return results

    @staticmethod
    def get_faculty_details(faculty_id):
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
        SELECT u.user_id, u.name, u.email, u.department, 
               f.designation, f.h_index, f.research_domains, 
               f.remaining_slots, f.min_cgpa_req, f.thesis_available,
               COALESCE(f.is_verified, 1) as is_verified
        FROM faculty f
        JOIN users u ON f.faculty_id = u.user_id
        WHERE u.user_id = ?
        """
        cursor.execute(query, (faculty_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
            
        item = dict(row)
        item['research_domains'] = parse_json_list(item['research_domains'])
        
        # Labs
        cursor.execute("SELECT lab_id, lab_name, focus_area, facilities FROM research_labs WHERE faculty_id = ?", (faculty_id,))
        labs = cursor.fetchall()
        item['directed_labs'] = []
        for l in labs:
            l_dict = dict(l)
            l_dict['facilities'] = parse_json_list(l_dict['facilities'])
            item['directed_labs'].append(l_dict)
        
        # Papers
        cursor.execute("SELECT paper_id, title, authors, domain, publication_year, abstract, doi, download_url, faculty_id FROM research_papers")
        papers = cursor.fetchall()
        conn.close()
        
        faculty_papers = []
        for p in papers:
            p_dict = dict(p)
            p_authors = parse_json_list(p_dict['authors'])
            p_dict['authors'] = p_authors
            
            is_author = any(item['name'].lower() in author.lower() for author in p_authors)
            is_fac_paper = (p_dict.get('faculty_id') == faculty_id)
            
            if is_author or is_fac_paper:
                faculty_papers.append(p_dict)
                
        item['publications'] = faculty_papers
        
        return item

    @staticmethod
    def verify_faculty_profile(faculty_id, is_verified):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE faculty SET is_verified = ? WHERE faculty_id = ?", (1 if is_verified else 0, faculty_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def admin_update_faculty(faculty_id, designation=None, research_domains=None, h_index=None, remaining_slots=None, min_cgpa_req=None, is_verified=None):
        conn = get_db()
        cursor = conn.cursor()
        updates = []
        params = []
        
        if designation is not None:
            updates.append("designation = ?")
            params.append(designation)
        if research_domains is not None:
            domains = parse_json_list(research_domains)
            updates.append("research_domains = ?")
            params.append(json.dumps(domains))
        if h_index is not None:
            updates.append("h_index = ?")
            params.append(int(h_index))
        if remaining_slots is not None:
            updates.append("remaining_slots = ?")
            params.append(int(remaining_slots))
        if min_cgpa_req is not None:
            updates.append("min_cgpa_req = ?")
            params.append(float(min_cgpa_req))
        if is_verified is not None:
            updates.append("is_verified = ?")
            params.append(1 if is_verified else 0)

        if not updates:
            conn.close()
            return False

        params.append(faculty_id)
        sql = f"UPDATE faculty SET {', '.join(updates)} WHERE faculty_id = ?"
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return True
