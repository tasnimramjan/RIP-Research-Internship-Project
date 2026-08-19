import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.paper import ResearchPaperModel

class PaperController:
    @staticmethod
    def search_papers(params):
        keyword = params.get('keyword')
        domain = params.get('domain')
        year = params.get('year')
        author = params.get('author')
        
        papers = ResearchPaperModel.get_all_papers(keyword=keyword, domain=domain, year=year, author=author)
        return {"success": True, "count": len(papers), "papers": papers}

    @staticmethod
    def vector_semantic_search(query):
        if not query or not query.strip():
            return {"success": False, "message": "Semantic query cannot be empty."}
            
        results = ResearchPaperModel.semantic_search(query.strip())
        return {"success": True, "query": query, "count": len(results), "papers": results}

    @staticmethod
    def export_citation(paper_id, style="IEEE"):
        citation = ResearchPaperModel.export_citation(paper_id, format_style=style)
        return {"success": True, "paper_id": paper_id, "style": style, "citation": citation}
