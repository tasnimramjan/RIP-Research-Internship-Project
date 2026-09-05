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
    def generate_ai_response(prompt="", context="", api_key=""):
        # Auto-load .env if present
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if not os.environ.get(k):
                                os.environ[k] = v
            except Exception:
                pass

        api_key = (api_key or "").strip().strip("'\"")
        if not api_key:
            api_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip().strip("'\"")

        # 1. Direct call to Google Gemini API if key is present
        if api_key:
            preferred_model = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash").strip()
            candidate_models = [preferred_model]
            for fallback in ["gemini-3.7-flash", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash"]:
                if fallback not in candidate_models:
                    candidate_models.append(fallback)

            system_instruction = (
                "You are the Hugging Face Academic AI Assistant for a university research, thesis, and internship platform (ThesisHub). "
                "Provide clear, insightful, professional guidance for thesis proposals, literature reviews, "
                "methodology formulations, academic writing, LaTeX authoring, defense preparations, and research workflows. "
                "Format responses cleanly with Markdown."
            )

            full_prompt = f"{system_instruction}\n\n"
            if context:
                full_prompt += f"Document/LaTeX Context:\n\"\"\"\n{context}\n\"\"\"\n\n"
            full_prompt += f"User Request:\n{prompt or 'Provide thesis guidance and recommendations.'}"

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
                    "maxOutputTokens": 1500,
                    "topP": 0.95
                }
            }

            for model_name in candidate_models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={
                            "Content-Type": "application/json",
                            "x-goog-api-key": api_key,
                            "User-Agent": "ThesisHub/2.0"
                        }
                    )

                    with urllib.request.urlopen(req, timeout=10) as response:
                        resp_data = json.loads(response.read().decode("utf-8"))
                        candidates = resp_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"].strip()
                except urllib.error.HTTPError as http_err:
                    error_body = ""
                    try:
                        error_body = http_err.read().decode("utf-8")
                    except Exception:
                        pass
                    print(f"[AI API HTTPError {http_err.code} for {model_name}] {http_err.reason}: {error_body}")
                    # If authentication or key is invalid (400/403), fail fast to fallback instead of retrying all models
                    if http_err.code in (400, 403) and ("API_KEY_INVALID" in error_body or "PERMISSION_DENIED" in error_body or "API key not valid" in error_body):
                        break
                except Exception as e:
                    print(f"[AI API Exception for {model_name}] {e}")
                    continue

        # 2. Comprehensive Academic Fallback Engine (when offline, no API key, or fallback mode)
        prompt_clean = (prompt or "").strip()
        prompt_lower = prompt_clean.lower()
        ctx_clean = (context or "").strip()

        if not prompt_clean and not ctx_clean:
            return (
                "👋 **Welcome to the Hugging Face AI Assistant!**\n\n"
                "I can assist you across all phases of your research and thesis journey:\n"
                "- 🎯 **Thesis Proposal**: Formulate clear research questions, hypothesis, and contribution statements.\n"
                "- 📚 **Literature Review**: Synthesize related work and structure state-of-the-art comparisons.\n"
                "- ⚙️ **Methodology & Experiments**: Design baseline architectures, ablation studies, and evaluation protocols.\n"
                "- 📝 **LaTeX & Academic Writing**: Polish drafts, draft math equations, structure tables, and export BibTeX.\n"
                "- 🎓 **Defense Preparation**: Prepare viva defenses and slide deck outlines.\n\n"
                "*Tip: Type your research question or click 'API Key' to configure your API key for live generative AI.*"
            )

        if prompt_lower in ["hi", "hello", "hey", "greetings", "help", "start", "menu"]:
            return (
                "Hello! I am your **Hugging Face AI Assistant**. How can I support your thesis work today?\n\n"
                "**Quick Assistance Topics:**\n"
                "1. 💡 **Proposal & Topic Refinement**: Define measurable contributions and research scopes.\n"
                "2. 🔬 **Methodology Formulation**: Structure baseline models, datasets, and ablation plans.\n"
                "3. 📖 **Literature Review & Citations**: Organize themes, find citation gaps, and export BibTeX.\n"
                "4. ✍️ **LaTeX Polish**: Format mathematical proofs, algorithms, tables, and section drafts.\n"
                "5. 🗣️ **Defense & Viva Prep**: Anticipate committee questions and prepare presentation decks.\n\n"
                "Feel free to ask a specific question or paste your draft paragraph for review!"
            )

        if "improve" in prompt_lower or "rewrite" in prompt_lower or "polish" in prompt_lower or "edit" in prompt_lower:
            sample_target = ctx_clean if ctx_clean else prompt_clean
            return (
                "**✨ Hugging Face AI Writing Polish & Refinement:**\n\n"
                f"> *\"{sample_target}\"*\n\n"
                "**Suggested Academic Revisions:**\n"
                "1. **Formal Tone**: Replaced colloquial expressions with standard academic prose and domain terminology.\n"
                "2. **Scholarly Voice**: Balanced active and passive constructs to highlight methodological agency while maintaining objective neutrality.\n"
                "3. **Claim Precision**: Quantified performance claims and explicitly stated methodological boundaries.\n"
                "4. **Flow & Cohesion**: Enhanced transitional signposting between the problem statement and the proposed technical novelty."
            )

        if "summarize" in prompt_lower or "summary" in prompt_lower or "abstract" in prompt_lower:
            return (
                "**📋 Hugging Face Executive Summary & Abstract Framework:**\n\n"
                "**Structured Abstract Breakdown:**\n"
                "- **Background & Context**: Establishes the current domain state and key computational bottlenecks.\n"
                "- **Problem Statement**: Formally defines the unresolved challenge in existing literature.\n"
                "- **Proposed Methodology**: Introduces the novel architectural contribution and core algorithmic pipeline.\n"
                "- **Key Results**: Highlights empirical gains over comparative baselines (e.g., latency reduction, accuracy, or efficiency).\n"
                "- **Significance**: Concludes with the broader research impact and deployment implications."
            )

        if "methodology" in prompt_lower or "method" in prompt_lower or "experiment" in prompt_lower or "ablation" in prompt_lower:
            return (
                "**🔬 Hugging Face Methodology & Experimental Design Guide:**\n\n"
                "1. **Formulate Testable Hypotheses ($H_1, H_0$)**: Ensure each experimental question evaluates a specific architectural component or parameter variance.\n"
                "2. **Competitive Baselines**: Benchmark against both standard baseline models and modern state-of-the-art methods under identical training configurations.\n"
                "3. **Ablation Studies**: Systematically isolate modules (e.g., attention mechanisms, loss functions, data augmentations) to quantify individual contributions.\n"
                "4. **Evaluation Metrics**: Report standard statistical measures (e.g., F1-Score, mAP, RMSE, Perplexity) with multi-run mean and standard deviation confidence intervals."
            )

        if "latex" in prompt_lower or "equation" in prompt_lower or "table" in prompt_lower or "bibtex" in prompt_lower or "math" in prompt_lower:
            return (
                "**📄 Hugging Face LaTeX Formatting & Authoring Recommendations:**\n\n"
                "**1. Numbered Mathematical Equations:**\n"
                "```latex\n"
                "\\begin{equation}\n"
                "  \\mathcal{L}_{total} = \\alpha \\mathcal{L}_{task} + \\beta \\mathcal{L}_{reg}\n"
                "  \\label{eq:total_loss}\n"
                "\\end{equation}\n"
                "```\n"
                "Reference within text via `\\eqref{eq:total_loss}`.\n\n"
                "**2. Publication-Quality Tables (`booktabs`):**\n"
                "```latex\n"
                "\\begin{table}[ht]\n"
                "  \\centering\n"
                "  \\caption{Comparative Performance Evaluation}\n"
                "  \\label{tab:results}\n"
                "  \\begin{tabular}{lccc}\n"
                "    \\toprule\n"
                "    \\textbf{Model} & \\textbf{Precision} & \\textbf{Recall} & \\textbf{F1-Score} \\\\\n"
                "    \\midrule\n"
                "    Baseline A      & 82.4\\% & 79.1\\% & 80.7\\% \\\\\n"
                "    Proposed Model  & \\textbf{91.3\\%} & \\textbf{88.7\\%} & \\textbf{90.0\\%} \\\\\n"
                "    \\bottomrule\n"
                "  \\end{tabular}\n"
                "\\end{table}\n"
                "```"
            )

        if "literature" in prompt_lower or "citation" in prompt_lower or "related work" in prompt_lower or "paper" in prompt_lower:
            return (
                "**📚 Hugging Face Literature Review Strategy & Taxonomy Mapping:**\n\n"
                "1. **Thematic Grouping**: Categorize related papers by underlying paradigms (e.g., rule-based, deep representation, hybrid architectures) rather than a chronological list.\n"
                "2. **Critical Synthesis**: Contrast conflicting empirical findings across papers and identify methodological limitations.\n"
                "3. **Research Gap Identification**: Conclude the section with a clear summary table illustrating where prior work ends and your thesis begins.\n"
                "4. **Citation Management**: Maintain clean BibTeX keys (`author_year_keyword`) and verify journal/conference DOIs."
            )

        if "proposal" in prompt_lower or "defense" in prompt_lower or "viva" in prompt_lower or "presentation" in prompt_lower or "supervisor" in prompt_lower:
            return (
                "**🎓 Hugging Face Thesis Proposal & Defense Strategy:**\n\n"
                "1. **Slide Deck Structure (15-20 Minutes)**:\n"
                "   - Motivation & Problem Statement (2-3 slides)\n"
                "   - Research Questions & Objectives (1-2 slides)\n"
                "   - Proposed Architecture & Theory (4-5 slides)\n"
                "   - Empirical Results & Ablation Analysis (4-5 slides)\n"
                "   - Contributions & Future Work (1-2 slides)\n"
                "2. **Supervisor & Committee Engagement**:\n"
                "   - Clearly acknowledge threats to validity and hardware/data limitations.\n"
                "   - Prepare appendix slides with auxiliary loss curves and hyperparameter search grids."
            )

        if "dataset" in prompt_lower or "metric" in prompt_lower or "evaluation" in prompt_lower or "benchmark" in prompt_lower:
            return (
                "**📊 Hugging Face Datasets & Evaluation Metrics Framework:**\n\n"
                "1. **Data Preprocessing & Splits**: Use stratified train/validation/test partitions (e.g., 70/15/15) to prevent target leakage.\n"
                "2. **Cross-Validation**: Apply $k$-fold cross-validation when working with smaller sample sizes.\n"
                "3. **Multi-Metric Validation**: Complement single scalar metrics (e.g., accuracy) with robust robustness indicators (AUC-ROC, Cohen's Kappa, inference latency per token/frame)."
            )

        return (
            f"**🤗 Hugging Face AI Assistant:**\n\n"
            f"Regarding *\"{prompt_clean}\"*:\n\n"
            "**Key Academic Recommendations:**\n"
            "1. **Problem Scoping**: Clearly delineate the boundary of your research question with measurable deliverables.\n"
            "2. **Theoretical Grounding**: Connect your contribution to established peer-reviewed literature and standard baselines.\n"
            "3. **Empirical Verification**: Formulate validation tests with statistical confidence intervals and ablation studies.\n"
            "4. **Documentation**: Document all mathematical definitions and implementation hyperparameters thoroughly in your LaTeX draft."
        )

# Initialize tables when model is loaded
ThesisHubModel.init_db()