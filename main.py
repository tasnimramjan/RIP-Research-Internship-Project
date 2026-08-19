import http.server
import socketserver
import json
import os
import urllib.parse
from seed import seed_data

from controllers.auth_controller       import AuthController
from controllers.supervisor_controller import SupervisorController
from controllers.faculty_controller    import FacultyController
from controllers.lab_controller        import LabController
from controllers.forum_controller      import ForumController
from controllers.project_controller    import ProjectController
from controllers.message_controller    import MessageController

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

    def do_GET(self):
        parsed      = urllib.parse.urlparse(self.path)
        path        = parsed.path
        params      = urllib.parse.parse_qs(parsed.query)
        params_flat = {k: v[0] for k, v in params.items()}

        if path in ("/", "/index.html"):
            self.send_html(os.path.join(BASE_DIR, "templates", "index.html"))
            return

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

        if path.startswith("/api/"):
            if path == "/api/supervisors/search":
                res = SupervisorController.handle_search(params_flat)
                self.send_json(res)
            elif path == "/api/labs/all":
                search_name = params_flat.get('name') or params_flat.get('search')
                res = LabController.get_all_labs(search_name=search_name)
                self.send_json(res)
            elif path == "/api/forums/threads":
                category = params_flat.get('category')
                res = ForumController.get_threads(category=category)
                self.send_json(res)
            elif path == "/api/forums/reminders":
                user_id = params_flat.get('user_id')
                res = ForumController.check_reminders(user_id)
                self.send_json(res)
            elif path == "/api/projects/all":
                skill = params_flat.get('skill')
                res = ProjectController.get_all_posts(skill=skill)
                self.send_json(res)
            elif path == "/api/messages/history":
                user1 = params_flat.get('user1')
                user2 = params_flat.get('user2')
                res = MessageController.get_direct_messages(user1, user2)
                self.send_json(res)
            else:
                self.send_json({"error": "Endpoint not found"}, status=404)
            return

        self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            data = json.loads(body.decode('utf-8'))
        except Exception:
            data = {}

        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path

        if path == "/api/auth/login":
            res = AuthController.handle_login(data)
            self.send_json(res)
        elif path == "/api/auth/signup":
            res = AuthController.handle_signup(data)
            self.send_json(res)
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
        elif path == "/api/forums/create":
            res = ForumController.create_thread(data.get('user_id'), data)
            self.send_json(res)
        elif path == "/api/forums/comment":
            res = ForumController.add_comment(data.get('user_id'), data)
            self.send_json(res)
        elif path == "/api/forums/react":
            res = ForumController.add_reaction(data.get('user_id'), data)
            self.send_json(res)
        elif path == "/api/forums/remind":
            res = ForumController.set_reminder(data.get('user_id'), data)
            self.send_json(res)
        elif path == "/api/projects/create":
            res = ProjectController.create_post(data.get('student_id'), data)
            self.send_json(res)
        elif path == "/api/projects/join":
            res = ProjectController.join_team(data.get('post_id'), data.get('student_id'))
            self.send_json(res)
        elif path == "/api/messages/send":
            res = MessageController.send_message(data)
            self.send_json(res)
        else:
            self.send_json({"error": "POST endpoint not found"}, status=404)

def run_server():
    seed_data()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), RIPRequestHandler) as httpd:
        print(f"R.I.P. Member 1 Module Server running at http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server shutting down.")

if __name__ == "__main__":
    run_server()
