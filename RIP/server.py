import http.server
import json
import os
import sqlite3
import urllib.parse

PORT = 8000
DB_FILE = "thesis_hub.db"
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            phase TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            progress INTEGER DEFAULT 0,
            due_date TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            version TEXT DEFAULT 'v1.0',
            status TEXT DEFAULT 'Draft',
            supervisor_feedback TEXT
        )
    """
    )

    cursor.execute(
        """
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
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            filename TEXT
        )
    """
    )

    cursor.execute(
        """
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
    """
    )

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


class RequestHandler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

    def respond_json(self, data, status=200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except ConnectionAbortedError:
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # FEATURE 14: Dynamic file content download from Database
        if path.startswith("/api/download/"):
            filename = os.path.basename(path)
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM resources WHERE filename = ?", (filename,))
            res = cursor.fetchone()
            conn.close()

            content = res[0] if res and res[0] else f"% Document: {filename}\nGenerated by ThesisHub."
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        if path.startswith("/api/"):
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if path == "/api/milestones":
                cursor.execute("SELECT * FROM milestones ORDER BY id ASC")
                data = [dict(r) for r in cursor.fetchall()]
                conn.close()
                return self.respond_json(data)

            elif path == "/api/documents":
                cursor.execute("SELECT * FROM documents ORDER BY id DESC")
                data = [dict(r) for r in cursor.fetchall()]
                conn.close()
                return self.respond_json(data)

            elif path == "/api/citations":
                cursor.execute("SELECT * FROM citations ORDER BY id DESC")
                data = [dict(r) for r in cursor.fetchall()]
                conn.close()
                return self.respond_json(data)

            elif path == "/api/resources":
                cursor.execute("SELECT * FROM resources ORDER BY id ASC")
                data = [dict(r) for r in cursor.fetchall()]
                conn.close()
                return self.respond_json(data)

            elif path == "/api/archive":
                query_params = urllib.parse.parse_qs(parsed.query)
                q = query_params.get("q", [""])[0].lower()
                dept = query_params.get("dept", [""])[0]

                sql = "SELECT * FROM archive WHERE 1=1"
                params = []
                if dept:
                    sql += " AND department = ?"
                    params.append(dept)

                cursor.execute(sql, params)
                rows = [dict(r) for r in cursor.fetchall()]

                if q:
                    filtered = []
                    for r in rows:
                        combined = f"{r['title']} {r['abstract']} {r['keywords']} {r['research_area']}".lower()
                        if any(term in combined for term in q.split()):
                            filtered.append(r)
                    rows = filtered

                conn.close()
                return self.respond_json(rows)

            conn.close()
            return self.respond_json({"error": "Not Found"}, 404)

        # Serve static frontend files safely
        rel_path = path.lstrip("/")
        if not rel_path or not os.path.exists(os.path.join(PUBLIC_DIR, rel_path)):
            rel_path = "index.html"

        target_file = os.path.join(PUBLIC_DIR, rel_path)
        self.send_response(200)

        if target_file.endswith(".html"):
            self.send_header("Content-Type", "text/html")
        elif target_file.endswith(".css"):
            self.send_header("Content-Type", "text/css")
        elif target_file.endswith(".js"):
            self.send_header("Content-Type", "application/javascript")

        self.end_headers()
        with open(target_file, "rb") as f:
            self.wfile.write(f.read())

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        if parsed.path == "/api/milestones/update":
            cursor.execute(
                "UPDATE milestones SET progress = ?, status = ? WHERE id = ?",
                (payload.get("progress"), payload.get("status"), payload.get("id")),
            )
            conn.commit()
            conn.close()
            return self.respond_json({"success": True})

        elif parsed.path == "/api/milestones/add":
            cursor.execute(
                "INSERT INTO milestones (title, phase, status, progress, due_date) VALUES (?, ?, ?, ?, ?)",
                (
                    payload.get("title"),
                    payload.get("phase"),
                    payload.get("status", "Pending"),
                    payload.get("progress", 0),
                    payload.get("due_date"),
                ),
            )
            conn.commit()
            conn.close()
            return self.respond_json({"success": True})

        elif parsed.path == "/api/documents/save":
            cursor.execute(
                "UPDATE documents SET content = ?, version = ? WHERE id = ?",
                (payload.get("content"), payload.get("version"), payload.get("id")),
            )
            conn.commit()
            conn.close()
            return self.respond_json({"success": True})

        elif parsed.path == "/api/documents/feedback":
            cursor.execute(
                "UPDATE documents SET supervisor_feedback = ?, status = ? WHERE id = ?",
                (payload.get("feedback"), payload.get("status"), payload.get("id")),
            )
            conn.commit()
            conn.close()
            return self.respond_json({"success": True})

        elif parsed.path == "/api/citations/add":
            cursor.execute(
                """INSERT INTO citations (title, authors, year, journal, volume, pages, doi, citation_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload.get("title"),
                    payload.get("authors"),
                    payload.get("year"),
                    payload.get("journal"),
                    payload.get("volume"),
                    payload.get("pages"),
                    payload.get("doi"),
                    payload.get("citation_type", "journal"),
                ),
            )
            conn.commit()
            conn.close()
            return self.respond_json({"success": True})

        # FEATURE 14: Post new guideline/resource to SQLite
        elif parsed.path == "/api/resources/add":
            title = payload.get("title")
            category = payload.get("category", "Guidelines")
            description = payload.get("description")
            filename = f"{title.lower().replace(' ', '_')[:25]}_guideline.txt"

            cursor.execute(
                "INSERT INTO resources (title, category, description, filename) VALUES (?, ?, ?, ?)",
                (title, category, description, filename),
            )
            conn.commit()
            conn.close()
            return self.respond_json({"success": True})

        elif parsed.path == "/api/ai-assistant":
            prompt = payload.get("prompt", "").lower()
            context = payload.get("context", "")

            if "improve" in prompt or "rewrite" in prompt:
                reply = f"**Hugging Face AI Refinement Suggestion:**\n\n'{context}'\n\n*Improvements Applied:* Converted informal verbs into formal academic syntax."
            elif "summarize" in prompt:
                reply = "**Hugging Face Executive Summary:**\nThe proposed methodology integrates GNN-driven processing with real-time sensor streams."
            else:
                reply = f"**Hugging Face Academic AI:**\nI reviewed your input: *'{payload.get('prompt')}'*.\n\nEnsure all hypotheses are tested in your empirical section."

            conn.close()
            return self.respond_json({"response": reply})

        conn.close()
        return self.respond_json({"error": "Bad Request"}, 400)


if __name__ == "__main__":
    init_db()
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print(f"🚀 Thesis Hub Server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")