import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class FacultyModel:
    @staticmethod
    def search_faculty(keywords=None, department=None, domain=None, lab_name=None):
        conn = get_db()
        cursor = conn.cursor()
        
        # We need to fetch all faculty profiles along with their labs and publications
        # and then do the filtering in Python for robust multi-keyword and partial matching.
        
        query = """
        SELECT u.user_id, u.name, u.email, u.department, 
               f.designation, f.h_index, f.research_domains, 
               f.remaining_slots, f.min_cgpa_req, f.thesis_available
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
            
            # parse facilities if it is JSON
            try:
                lab_copy = dict(lab)
                lab_copy['facilities'] = json.loads(lab_copy['facilities'])
            except:
                lab_copy['facilities'] = []
            lab_dict[fac_id].append(lab_copy)
            
        # Fetch papers to associate with faculty
        cursor.execute("SELECT paper_id, title, authors, domain, publication_year FROM research_papers")
        papers = cursor.fetchall()
        
        conn.close()
        
        results = []
        for f in faculty_rows:
            item = dict(f)
            domains = json.loads(item['research_domains'])
            item['research_domains'] = domains
            
            # Associate labs
            item['directed_labs'] = lab_dict.get(item['user_id'], [])
            
            # Associate papers by string matching author names
            faculty_papers = []
            for p in papers:
                p_dict = dict(p)
                p_authors = json.loads(p_dict['authors'])
                # If faculty name is a substring of any author in the paper
                if any(item['name'].lower() in author.lower() for author in p_authors):
                    p_dict['authors'] = p_authors
                    faculty_papers.append(p_dict)
            
            item['publications'] = faculty_papers
            
            # Filter by department
            if department and item['department'] != department:
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
                    # Check across name, domains, lab name/focus, and publication titles
                    match_found = False
                    if kw in item['name'].lower():
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
                                if kw in p['title'].lower():
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
               f.remaining_slots, f.min_cgpa_req, f.thesis_available
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
        item['research_domains'] = json.loads(item['research_domains'])
        
        # Labs
        cursor.execute("SELECT lab_id, lab_name, focus_area, facilities FROM research_labs WHERE faculty_id = ?", (faculty_id,))
        labs = cursor.fetchall()
        item['directed_labs'] = []
        for l in labs:
            l_dict = dict(l)
            try:
                l_dict['facilities'] = json.loads(l_dict['facilities'])
            except:
                l_dict['facilities'] = []
            item['directed_labs'].append(l_dict)
        
        # Papers
        cursor.execute("SELECT paper_id, title, authors, domain, publication_year, abstract, doi, download_url FROM research_papers")
        papers = cursor.fetchall()
        conn.close()
        
        faculty_papers = []
        for p in papers:
            p_dict = dict(p)
            p_authors = json.loads(p_dict['authors'])
            if any(item['name'].lower() in author.lower() for author in p_authors):
                p_dict['authors'] = p_authors
                faculty_papers.append(p_dict)
                
        item['publications'] = faculty_papers
        
        return item
