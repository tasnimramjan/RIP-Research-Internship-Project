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
    def add_paper(data):
        faculty_id = data.get('faculty_id')
        title = data.get('title')
        authors = data.get('authors', [])
        domain = data.get('domain')
        year = data.get('year')
        abstract = data.get('abstract')
        
        if not title or not domain or not year or not abstract:
            return {"success": False, "message": "Missing required fields."}
            
        paper_id = ResearchPaperModel.add_paper(
            faculty_id, title, authors, domain, year, abstract
        )
        return {"success": True, "paper_id": paper_id, "message": "Publication added successfully."}

    @staticmethod
    def export_citation(paper_id, style="IEEE"):
        citation = ResearchPaperModel.export_citation(paper_id, format_style=style)
        return {"success": True, "paper_id": paper_id, "style": style, "citation": citation}

    @staticmethod
    def delete_paper(user_id, data):
        paper_id = data.get('paper_id')
        if not paper_id or not user_id:
            return {"success": False, "message": "Paper ID and User ID are required."}
            
        from models.user import UserModel
        user = UserModel.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "User not found."}
            
        is_admin = user['role'] == 'Admin'
        
        # Only Admin or the faculty owner can delete
        if not is_admin and user['role'] != 'Faculty':
            return {"success": False, "message": "Unauthorized. Only administrators can delete research papers."}
            
        success = ResearchPaperModel.delete_paper(paper_id, user_id=user_id, is_admin=is_admin)
        if success:
            return {"success": True, "message": "Research paper deleted successfully."}
        else:
            return {"success": False, "message": "Failed to delete paper or paper not found."}
