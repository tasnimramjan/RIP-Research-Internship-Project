import json
import math
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db

class ResearchPaperModel:
    @staticmethod
    def get_all_papers(keyword=None, domain=None, year=None, author=None):
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT * FROM research_papers WHERE 1=1"
        params = []
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if year:
            query += " AND publication_year = ?"
            params.append(int(year))
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        papers = []
        for r in rows:
            p = dict(r)
            p['authors'] = json.loads(p['authors'])
            p['vector_embedding'] = json.loads(p['vector_embedding'])
            
            if author:
                aut = author.lower().strip()
                if not any(aut in a.lower() for a in p['authors']):
                    continue

            if keyword:
                kw = keyword.lower()
                in_title = kw in p['title'].lower()
                in_abstract = kw in p['abstract'].lower()
                in_authors = any(kw in a.lower() for a in p['authors'])
                if not (in_title or in_abstract or in_authors):
                    continue
                    
            papers.append(p)
        return papers

    @staticmethod
    def cosine_similarity(v1, v2):
        if len(v1) != len(v2) or not v1 or not v2:
            return 0.0
        dot_prod = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = math.sqrt(sum(a * a for a in v1))
        norm_v2 = math.sqrt(sum(b * b for b in v2))
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return dot_prod / (norm_v1 * norm_v2)

    @staticmethod
    def _text_to_pseudo_vector(text):
        # Generate a 4-dimensional semantic embedding vector based on domain keywords
        t = text.lower()
        cv_keywords = ['vision', 'image', 'cnn', 'detection', 'medical', 'segmentation', 'yolo', 'resnet']
        nlp_keywords = ['nlp', 'language', 'transformer', 'bert', 'llm', 'attention', 'speech', 'text', 'sentiment']
        sec_keywords = ['security', 'blockchain', 'privacy', 'cyber', 'encryption', 'attack']
        iot_keywords = ['iot', 'robotics', 'drone', 'embedded', 'hardware', 'sensor', 'microcontroller']

        v = [
            sum(1 for k in cv_keywords if k in t) + 0.1,
            sum(1 for k in nlp_keywords if k in t) + 0.1,
            sum(1 for k in sec_keywords if k in t) + 0.1,
            sum(1 for k in iot_keywords if k in t) + 0.1
        ]
        norm = math.sqrt(sum(x * x for x in v))
        return [x / norm for x in v] if norm > 0 else [0.25, 0.25, 0.25, 0.25]

    @staticmethod
    def semantic_search(semantic_query, limit=5):
        query_vec = ResearchPaperModel._text_to_pseudo_vector(semantic_query)
        all_papers = ResearchPaperModel.get_all_papers()
        
        scored_papers = []
        for p in all_papers:
            sim = ResearchPaperModel.cosine_similarity(query_vec, p['vector_embedding'])
            p['similarity_score'] = round(sim * 100, 1)
            scored_papers.append(p)
            
        scored_papers.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_papers[:limit]

    @staticmethod
    def export_citation(paper_id, format_style="IEEE"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM research_papers WHERE paper_id = ?", (paper_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return "Paper not found."
            
        p = dict(row)
        authors = json.loads(p['authors'])
        author_str = ", ".join(authors)
        title = p['title']
        year = p['publication_year']
        domain = p['domain']
        doi = p.get('doi') or "N/A"
        
        fmt = format_style.upper()
        if fmt == "APA":
            return f"{author_str} ({year}). {title}. {domain}. https://doi.org/{doi}"
        elif fmt == "MLA":
            return f'{author_str}. "{title}." {domain}, {year}.'
        else: # Default IEEE
            return f'{author_str}, "{title}," in {domain}, {year}. doi: {doi}'
