import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.thesis_hub import ThesisHubModel

class ThesisHubController:

    # ── Milestones ──────────────────────────────────────────
    @staticmethod
    def get_milestones():
        return ThesisHubModel.get_milestones()

    @staticmethod
    def add_milestone(data):
        title = data.get("title")
        phase = data.get("phase", "General")
        status = data.get("status", "Pending")
        progress = int(data.get("progress", 0))
        due_date = data.get("due_date")

        if not title:
            return {"success": False, "message": "Title is required."}

        ThesisHubModel.add_milestone(title, phase, status, progress, due_date)
        return {"success": True}

    @staticmethod
    def update_milestone(data):
        milestone_id = data.get("id")
        progress = data.get("progress")
        status = data.get("status")

        if milestone_id is None:
            return {"success": False, "message": "Milestone ID is required."}

        ThesisHubModel.update_milestone(milestone_id, progress, status)
        return {"success": True}

    # ── Documents (LaTeX & Supervisor Workflow) ──────────────
    @staticmethod
    def get_documents():
        return ThesisHubModel.get_documents()

    @staticmethod
    def save_document(data):
        doc_id = data.get("id")
        content = data.get("content")
        version = data.get("version", "v1.0")

        if doc_id is None:
            return {"success": False, "message": "Document ID is required."}

        ThesisHubModel.save_document(doc_id, content, version)
        return {"success": True}

    @staticmethod
    def update_document_feedback(data):
        doc_id = data.get("id")
        status = data.get("status", "Under Review")
        feedback = data.get("feedback", "")

        if doc_id is None:
            return {"success": False, "message": "Document ID is required."}

        ThesisHubModel.update_document_feedback(doc_id, status, feedback)
        return {"success": True}

    # ── Citations ───────────────────────────────────────────
    @staticmethod
    def get_citations():
        return ThesisHubModel.get_citations()

    @staticmethod
    def add_citation(data):
        title = data.get("title")
        authors = data.get("authors")
        year = int(data.get("year", 2026))
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        pages = data.get("pages", "")
        doi = data.get("doi", "")
        citation_type = data.get("citation_type", "journal")

        if not title or not authors:
            return {"success": False, "message": "Title and authors are required."}

        ThesisHubModel.add_citation(title, authors, year, journal, volume, pages, doi, citation_type)
        return {"success": True}

    # ── Resources ───────────────────────────────────────────
    @staticmethod
    def get_resources():
        return ThesisHubModel.get_resources()

    @staticmethod
    def add_resource(data):
        title = data.get("title")
        category = data.get("category", "Guidelines")
        description = data.get("description", "")

        if not title:
            return {"success": False, "message": "Title is required."}

        ThesisHubModel.add_resource(title, category, description)
        return {"success": True}

    @staticmethod
    def get_download(filename):
        return ThesisHubModel.get_resource_content(filename)

    # ── Archive ─────────────────────────────────────────────
    @staticmethod
    def search_archive(params):
        q = params.get("q", "")
        dept = params.get("dept", "")
        return ThesisHubModel.search_archive(q=q, dept=dept)

    @staticmethod
    def add_archive_thesis(data):
        title = data.get("title")
        author = data.get("author")
        department = data.get("department", "Computer Science")
        year = int(data.get("year", 2026))
        research_area = data.get("research_area", "General")
        keywords = data.get("keywords", "")
        abstract = data.get("abstract", "")

        if not title or not author:
            return {"success": False, "message": "Title and author are required."}

        new_id = ThesisHubModel.add_archive_thesis(title, author, department, year, research_area, keywords, abstract)
        return {"success": True, "id": new_id}

    # ── AI Assistant ────────────────────────────────────────
    @staticmethod
    def ask_ai_assistant(data):
        prompt = data.get("prompt", "")
        context = data.get("context", "")
        reply = ThesisHubModel.generate_ai_response(prompt=prompt, context=context)
        return {"response": reply}
