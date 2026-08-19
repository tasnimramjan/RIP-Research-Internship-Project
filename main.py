import http.server
import socketserver
import json
import os
import urllib.parse
from seed import seed_data

# Controllers — only those needed for the 5 remaining feature sets
from controllers.auth_controller        import AuthController
from controllers.supervisor_controller  import SupervisorController
from controllers.faculty_controller     import FacultyController
from controllers.lab_controller         import LabController
from controllers.internship_controller  import InternshipController   # KEPT
from controllers.paper_controller       import PaperController
from controllers.thesis_group_controller import ThesisGroupController
from controllers.admin_controller       import AdminController
from controllers.forum_controller       import ForumController
from controllers.project_controller     import ProjectController
from controllers.message_controller     import MessageController

# Removed (features stripped from v2, now restored):
#   MatchingController   — Research Interest Matching & 1-to-1 Chat (Partially restored)
# Routes for Faculty Profile Explorer removed below.

PORT = int(os.environ.get("PORT", 8001))
BASE_DIR = os.path.dirname(__file__)


class RIPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_html(self, filepath):
        if os.path.exists(filepath):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

    # ── GET ────────────────────────────────────────────────
    def do_GET(self):
        parsed      = urllib.parse.urlparse(self.path)
        path        = parsed.path
        params      = urllib.parse.parse_qs(parsed.query)
        params_flat = {k: v[0] for k, v in params.items()}

        # Serve HTML
        if path in ("/", "/index.html"):
            self.send_html(os.path.join(BASE_DIR, "templates", "index.html"))
            return

        # Serve static assets
        if path.startswith("/static/"):
            file_path = os.path.join(BASE_DIR, path.lstrip("/"))
            if os.path.exists(file_path):
                self.send_response(200)
                if   path.endswith(".css"): self.send_header('Content-Type', 'text/css')
                elif path.endswith(".js"):  self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Static Asset Not Found")
                return

        # REST API GET routes (v2)
        if path.startswith("/api/"):
            # -- Smart Supervisor Finder (KEPT) --
            if path == "/api/supervisors/search":
                res = SupervisorController.handle_search(params_flat)
                self.send_json(res)

            # -- Research Lab Board (KEPT) --
            elif path == "/api/labs/all":
                search_name = params_flat.get('name') or params_flat.get('search')
                res = LabController.get_all_labs(search_name=search_name)
                self.send_json(res)

            # -- Internship Opportunity Portal (KEPT) --
            elif path == "/api/internships/all":
                student_id = params_flat.get('student_id')
                res = InternshipController.get_opportunities(student_id=student_id)
                self.send_json(res)

            # -- Research Paper Discovery (KEPT) --
            elif path == "/api/papers/search":
                res = PaperController.search_papers(params_flat)
                self.send_json(res)
            elif path == "/api/papers/citation":
                paper_id = params_flat.get('paper_id')
                style    = params_flat.get('style', 'IEEE')
                res = PaperController.export_citation(paper_id, style=style)
                self.send_json(res)

            # -- Thesis Group Finder (KEPT) --
            elif path == "/api/thesis_groups/all":
                topic = params_flat.get('topic')
                res = ThesisGroupController.get_groups(topic=topic)
                self.send_json(res)
            elif path == "/api/chat/group":
                grp_id = params_flat.get('group_id')
                res = ThesisGroupController.get_group_messages(grp_id)
                self.send_json(res)

            # -- Admin Control Panel (KEPT) --
            elif path == "/api/admin/users":
                res = AdminController.get_users()
                self.send_json(res)
            elif path == "/api/admin/analytics":
                res = AdminController.get_system_analytics()
                self.send_json(res)

            # -- Forum & Project & Chat APIs --
            elif path == '/api/forums/threads':
                category = params_flat.get('category')
                self.send_json(ForumController.get_threads(category))
            elif path == '/api/forums/reminders':
                self.send_json(ForumController.check_reminders(params_flat.get('user_id')))
            elif path == '/api/projects/all':
                self.send_json(ProjectController.get_all_posts())
            elif path == '/api/messages/history':
                self.send_json(MessageController.get_direct_messages(params_flat.get('user1'), params_flat.get('user2')))

            # -- REMOVED routes return 404 --
            # /api/matching/*          → Research Interest Matching (REMOVED)
            # /api/faculty/<id> GET    → Faculty Profile Explorer (REMOVED)
            else:
                self.send_json({"error": "Endpoint not found"}, status=404)
            return

        self.send_error(404)

    # ── POST ───────────────────────────────────────────────
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            data = json.loads(body.decode('utf-8'))
        except Exception:
            data = {}

        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path

        # Authentication
        if path == "/api/auth/login":
            res = AuthController.handle_login(data)
            self.send_json(res)
        elif path == "/api/auth/signup":
            res = AuthController.handle_signup(data)
            self.send_json(res)

        # Group Chat — Thesis Groups only (1-to-1 direct chat REMOVED)
        elif path == "/api/chat/group/send":
            res = ThesisGroupController.send_group_message(data.get('sender_id'), data.get('group_id'), data.get('text'))
            self.send_json(res)

        # Thesis Group Finder
        elif path == "/api/thesis_groups/join":
            res = ThesisGroupController.join_group(data.get('group_id'), data.get('student_id'))
            self.send_json(res)
        elif path == "/api/thesis_groups/leave":
            res = ThesisGroupController.leave_group(data.get('group_id'), data.get('student_id'))
            self.send_json(res)
        elif path == "/api/thesis_groups/create":
            res = ThesisGroupController.create_group(data.get('student_id'), data)
            self.send_json(res)

        # Faculty Lab & Profile Management
        elif path == "/api/faculty/update_profile":
            res = FacultyController.update_faculty_profile(data.get('faculty_id'), data)
            self.send_json(res)
        elif path == "/api/faculty/create_lab":
            res = FacultyController.create_lab(data.get('faculty_id'), data)
            self.send_json(res)
        elif path == "/api/faculty/add_project":
            res = FacultyController.add_lab_project(data)
            self.send_json(res)
        elif path == "/api/labs/post_ra":
            res = LabController.post_ra(data.get('lab_id'), data)
            self.send_json(res)

        # Admin — User Management
        elif path == "/api/admin/toggle_user":
            res = AdminController.toggle_user_status(data.get('user_id'))
            self.send_json(res)
        elif path == "/api/admin/delete_user":
            res = AdminController.delete_user(data.get('user_id'))
            self.send_json(res)
        elif path == "/api/admin/add_user":
            res = AdminController.add_user(data)
            self.send_json(res)

        # Admin — Internship Management (KEPT)
        elif path == "/api/admin/create_internship":
            res = AdminController.create_internship(data)
            self.send_json(res)
        elif path == "/api/admin/delete_internship":
            res = AdminController.delete_internship(data.get('opportunity_id'))
            self.send_json(res)

        # Admin — Lab & Group Moderation
        elif path == "/api/admin/delete_lab":
            res = AdminController.delete_lab(data.get('lab_id'))
            self.send_json(res)
        elif path == "/api/admin/delete_group":
            res = AdminController.delete_thesis_group(data.get('group_id'))
            self.send_json(res)

        # Forum & Project & Chat APIs
        elif path == '/api/forums/create':
            self.send_json(ForumController.create_thread(data.get('user_id'), data))
        elif path == '/api/forums/comment':
            self.send_json(ForumController.add_comment(data.get('user_id'), data))
        elif path == '/api/forums/react':
            self.send_json(ForumController.add_reaction(data.get('user_id'), data))
        elif path == '/api/forums/reminder':
            self.send_json(ForumController.set_reminder(data.get('user_id'), data))
        elif path == '/api/projects/create':
            self.send_json(ProjectController.create_post(data.get('student_id'), data))
        elif path == '/api/projects/join':
            self.send_json(ProjectController.join_team(data.get('post_id'), data.get('student_id')))
        elif path == '/api/messages/send':
            self.send_json(MessageController.send_message(data))

        else:
            self.send_json({"error": "POST endpoint not found"}, status=404)


def run_server():
    seed_data()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), RIPRequestHandler) as httpd:
        print(f"R.I.P. Platform v2 running at http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server shutting down.")


if __name__ == "__main__":
    run_server()
