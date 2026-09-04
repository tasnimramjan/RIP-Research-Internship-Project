import sqlite3
import os
import json
import urllib.request

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rip_database.sqlite")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class ThesisHubModel:

    @staticmethod
    def init_db():
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                phase TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                progress INTEGER DEFAULT 0,
                due_date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                version TEXT DEFAULT 'v1.0',
                status TEXT DEFAULT 'Draft',
                supervisor_feedback TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT NOT NULL,
                year INTEGER,
                journal TEXT,
                volume TEXT,
                pages TEXT,
                doi TEXT,
                citation_type TEXT DEFAULT 'journal'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                filename TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                department TEXT NOT NULL,
                year INTEGER NOT NULL,
                research_area TEXT NOT NULL,
                keywords TEXT,
                abstract TEXT
            )
        """)

        # Seed Milestones
        cursor.execute("SELECT COUNT(*) FROM milestones")
        if cursor.fetchone()[0] == 0:
            milestones = [
                ("Thesis Proposal Defense", "Proposal", "Completed", 100, "2026-02-15"),
                ("Systematic Literature Review", "Literature Review", "In Progress", 75, "2026-04-10"),
                ("Core Architecture Implementation", "Implementation", "In Progress", 40, "2026-06-01"),
                ("Drafting Methodology & Results", "Writing", "Pending", 10, "2026-07-20"),
                ("Final Document Submission", "Submission", "Pending", 0, "2026-09-01"),
                ("Thesis Oral Defense Prep", "Defense", "Pending", 0, "2026-09-25"),
            ]
            cursor.executemany(
                "INSERT INTO milestones (title, phase, status, progress, due_date) VALUES (?, ?, ?, ?, ?)",
                milestones,
            )

        # Seed Documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        if cursor.fetchone()[0] == 0:
            default_latex = (
                "\\documentclass{article}\n\\title{Deep Learning in Autonomous Navigation}\n"
                "\\author{John Doe}\n\\date{August 2026}\n\n\\begin{document}\n"
                "\\maketitle\n\n\\section{Introduction}\nThis thesis explores real-time spatial path planning.\n\n"
                "\\section{Methodology}\nWe utilize Graph Neural Networks (GNNs) combined with LiDAR sensors.\n\n"
                "\\section{Expected Results}\nA 35% reduction in latency compared to classical A* search algorithms.\n"
                "\\end{document}"
            )
            cursor.execute(
                "INSERT INTO documents (title, content, version, status, supervisor_feedback) VALUES (?, ?, ?, ?, ?)",
                (
                    "Main_Thesis_Draft.tex",
                    default_latex,
                    "v1.2",
                    "Needs Revision",
                    "Please expand Section 2 on GNN baseline hyperparameters.",
                ),
            )

        # Seed Citations
        cursor.execute("SELECT COUNT(*) FROM citations")
        if cursor.fetchone()[0] == 0:
            citations = [
                (
                    "Deep Residual Learning for Image Recognition",
                    "He, K., Zhang, X., Ren, S., & Sun, J.",
                    2016,
                    "IEEE Conference on Computer Vision and Pattern Recognition",
                    "CVPR",
                    "770-778",
                    "10.1109/CVPR.2016.90",
                    "conference",
                ),
                (
                    "Attention Is All You Need",
                    "Vaswani, A., Shazeer, N., Parmar, N., et al.",
                    2017,
                    "Advances in Neural Information Processing Systems",
                    "30",
                    "5998-6008",
                    "10.48550/arXiv.1706.03762",
                    "journal",
                ),
            ]
            cursor.executemany(
                "INSERT INTO citations (title, authors, year, journal, volume, pages, doi, citation_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                citations,
            )

        # Seed Resources
        cursor.execute("SELECT COUNT(*) FROM resources")
        if cursor.fetchone()[0] == 0:
            resources = [
                ("Official University LaTeX Thesis Template", "Templates", "Standard layout approved by Academic Senate.", "latex_thesis_template.tex"),
                ("Academic Writing & Methodology Guide", "Guides", "Guide on structuring research questions.", "thesis_writing_guide.pdf"),
                ("Defense Presentation Deck Template", "Presentation", "Slide templates for thesis defenses.", "defense_presentation_template.pptx"),
                ("Recorded Seminar: Effective Citation & Ethics", "Seminars", "1-hour workshop on peer review.", "ethics_seminar_notes.txt"),
            ]
            cursor.executemany(
                "INSERT INTO resources (title, category, description, filename) VALUES (?, ?, ?, ?)",
                resources,
            )

        # Seed Archive
        cursor.execute("SELECT COUNT(*) FROM archive")
        if cursor.fetchone()[0] == 0:
            archive = [
                (
                    "Optimization of Graph Neural Networks for Robotic Edge Computing",
                    "Sarah Jenkins",
                    "Computer Science",
                    2025,
                    "Artificial Intelligence",
                    "GNN, Edge Computing, Robotics, Real-time Systems",
                    "This thesis presents lightweight graph neural networks optimized for low-power robotics hardware.",
                ),
                (
                    "Blockchain Architecture for Decentralized Academic Credentialing",
                    "Michael Chang",
                    "Software Engineering",
                    2024,
                    "Distributed Systems",
                    "Blockchain, Smart Contracts, Security, Web3",
                    "An investigation into immutable credential storage using Zero-Knowledge proofs.",
                ),
                (
                    "Quantum-Resistant Encryption Protocols for IoT Devices",
                    "Elena Rostova",
                    "Cybersecurity",
                    2025,
                    "Cryptography",
                    "Quantum Computing, Lattice Cryptography, IoT",
                    "Analysis and implementation of post-quantum cryptographic primitives.",
                ),
            ]
            cursor.executemany(
                "INSERT INTO archive (title, author, department, year, research_area, keywords, abstract) VALUES (?, ?, ?, ?, ?, ?, ?)",
                archive,
            )

        conn.commit()
        conn.close()

    # ── Milestones ──────────────────────────────────────────
    @staticmethod
    def get_milestones():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM milestones ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def add_milestone(title, phase, status="Pending", progress=0, due_date=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO milestones (title, phase, status, progress, due_date) VALUES (?, ?, ?, ?, ?)",
            (title, phase, status, progress, due_date),
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def update_milestone(milestone_id, progress, status):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE milestones SET progress = ?, status = ? WHERE id = ?",
            (progress, status, milestone_id),
        )
        conn.commit()
        conn.close()
        return True

    # ── Documents (LaTeX Manager & Supervisor Approval) ────
    @staticmethod
    def get_documents():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def save_document(doc_id, content, version):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documents SET content = ?, version = ? WHERE id = ?",
            (content, version, doc_id),
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def update_document_feedback(doc_id, status, feedback):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documents SET supervisor_feedback = ?, status = ? WHERE id = ?",
            (feedback, status, doc_id),
        )
        conn.commit()
        conn.close()
        return True

    # ── Citations ───────────────────────────────────────────
    @staticmethod
    def get_citations():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM citations ORDER BY id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def add_citation(title, authors, year, journal="", volume="", pages="", doi="", citation_type="journal"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO citations (title, authors, year, journal, volume, pages, doi, citation_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, authors, year, journal, volume, pages, doi, citation_type),
        )
        conn.commit()
        conn.close()
        return True

    # ── Resources ───────────────────────────────────────────
    @staticmethod
    def get_resources():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resources ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def add_resource(title, category="Guidelines", description=""):
        filename = f"{title.lower().replace(' ', '_')[:25]}_guideline.txt"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO resources (title, category, description, filename) VALUES (?, ?, ?, ?)",
            (title, category, description, filename),
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_resource_content(filename):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM resources WHERE filename = ?", (filename,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res and res[0] else f"% Document: {filename}\nGenerated by ThesisHub."

    # ── Archive ─────────────────────────────────────────────
    @staticmethod
    def search_archive(q="", dept=""):
        conn = get_db()
        cursor = conn.cursor()
        sql = "SELECT * FROM archive WHERE 1=1"
        params = []
        if dept:
            sql += " AND department = ?"
            params.append(dept)

        sql += " ORDER BY id DESC"

        cursor.execute(sql, params)
        rows = [dict(r) for r in cursor.fetchall()]

        if q:
            filtered = []
            for r in rows:
                combined = f"{r['title']} {r['abstract']} {r['keywords']} {r['research_area']}".lower()
                if any(term in combined for term in q.lower().split()):
                    filtered.append(r)
            rows = filtered

        conn.close()
        return rows

    @staticmethod
    def add_archive_thesis(title, author, department, year, research_area, keywords="", abstract=""):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO archive (title, author, department, year, research_area, keywords, abstract)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, author, department, int(year), research_area, keywords, abstract))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    # ── AI Assistant (Gemini API Integration) ───────────────
    @staticmethod
    def generate_ai_response(prompt="", context=""):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        # 1. Direct call to Google Gemini API if key is present
        if api_key:
            preferred_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            candidate_models = [preferred_model]
            for fallback in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"]:
                if fallback not in candidate_models:
                    candidate_models.append(fallback)

            system_instruction = (
                "You are the Gemini Academic AI Assistant for a university research, thesis, and internship platform. "
                "Provide clear, insightful, professional guidance for thesis proposals, literature reviews, "
                "methodology formulations, academic writing, and LaTeX authoring. Format with Markdown."
            )

            full_prompt = f"{system_instruction}\n\n"
            if context:
                full_prompt += f"Document/LaTeX Context:\n\"\"\"\n{context}\n\"\"\"\n\n"
            full_prompt += f"User Request:\n{prompt}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024
                }
            }

            for model_name in candidate_models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"}
                    )

                    with urllib.request.urlopen(req, timeout=15) as response:
                        resp_data = json.loads(response.read().decode("utf-8"))
                        candidates = resp_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"]
                except Exception as e:
                    print(f"[Gemini API Exception for {model_name}] {e}")
                    continue

        # 2. High-quality academic fallback responses
        prompt_lower = prompt.lower()
        if "improve" in prompt_lower or "rewrite" in prompt_lower:
            return f"**Gemini AI Refinement Suggestion:**\n\n'{context or prompt}'\n\n*Improvements Applied:*\n- Converted informal phrases to formal academic terminology\n- Balanced passive and active voice for clarity\n- Sharpened technical thesis contribution claims\n\n*(Note: Set `GEMINI_API_KEY` in environment for live Gemini responses)*"
        elif "summarize" in prompt_lower:
            return "**Gemini Executive Summary:**\n\nThe proposed framework synthesizes graph-structured data pipelines with real-time streaming telemetry, maintaining computational tractability while preserving empirical precision.\n\n*(Note: Set `GEMINI_API_KEY` in environment for live Gemini responses)*"
        elif "methodology" in prompt_lower or "method" in prompt_lower:
            return "**Gemini Methodology Recommendation:**\n\n1. Formulate formal research hypotheses with measurable parameters.\n2. Detail baseline architectures and ablation test protocols.\n3. Validate empirical claims with appropriate statistical confidence measures.\n\n*(Note: Set `GEMINI_API_KEY` in environment for live Gemini responses)*"
        else:
            return f"**Gemini Academic AI:**\n\nI reviewed your input: *'{prompt}'*.\n\nEnsure that your research problem statement is grounded in recent literature and that empirical evaluation metrics are formally defined.\n\n*(Note: Set `GEMINI_API_KEY` in environment for live Gemini responses)*"

# Initialize tables when model is loaded
ThesisHubModel.init_db()
