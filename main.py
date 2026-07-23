import http.server
import socketserver
import json
import os
import urllib.parse
from seed import seed_data

from controllers.auth_controller        import AuthController
from controllers.internship_controller  import InternshipController
from controllers.paper_controller       import PaperController
from controllers.thesis_group_controller import ThesisGroupController
from controllers.admin_controller       import AdminController

PORT = int(os.environ.get("PORT", 8002))
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
            if path == "/api/internships/all":
                student_id = params_flat.get('student_id')
                res = InternshipController.get_opportunities(student_id=student_id)
                self.send_json(res)
            elif path == "/api/papers/search":
                res = PaperController.search_papers(params_flat)
                self.send_json(res)
            elif path == "/api/papers/citation":
                paper_id = params_flat.get('paper_id')
                style    = params_flat.get('style', 'IEEE')
                res = PaperController.export_citation(paper_id, style=style)
                self.send_json(res)
            elif path == "/api/thesis_groups/all":
                topic = params_flat.get('topic')
                res = ThesisGroupController.get_groups(topic=topic)
                self.send_json(res)
            elif path == "/api/chat/group":
                grp_id = params_flat.get('group_id')
                res = ThesisGroupController.get_group_messages(grp_id)
                self.send_json(res)
            elif path == "/api/admin/users":
                res = AdminController.get_users()
                self.send_json(res)
            elif path == "/api/admin/analytics":
                res = AdminController.get_system_analytics()
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
        elif path == "/api/chat/group/send":
            res = ThesisGroupController.send_group_message(data.get('sender_id'), data.get('group_id'), data.get('text'))
            self.send_json(res)
        elif path == "/api/thesis_groups/join":
            res = ThesisGroupController.join_group(data.get('group_id'), data.get('student_id'))
            self.send_json(res)
        elif path == "/api/thesis_groups/leave":
            res = ThesisGroupController.leave_group(data.get('group_id'), data.get('student_id'))
            self.send_json(res)
        elif path == "/api/thesis_groups/create":
            res = ThesisGroupController.create_group(data.get('student_id'), data)
            self.send_json(res)
        elif path == "/api/admin/toggle_user":
            res = AdminController.toggle_user_status(data.get('user_id'))
            self.send_json(res)
        elif path == "/api/admin/delete_user":
            res = AdminController.delete_user(data.get('user_id'))
            self.send_json(res)
        elif path == "/api/admin/add_user":
            res = AdminController.add_user(data)
            self.send_json(res)
        elif path == "/api/admin/create_internship":
            res = AdminController.create_internship(data)
            self.send_json(res)
        elif path == "/api/admin/delete_internship":
            res = AdminController.delete_internship(data.get('opportunity_id'))
            self.send_json(res)
        elif path == "/api/admin/delete_group":
            res = AdminController.delete_thesis_group(data.get('group_id'))
            self.send_json(res)
        else:
            self.send_json({"error": "POST endpoint not found"}, status=404)

def run_server():
    seed_data()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), RIPRequestHandler) as httpd:
        print(f"R.I.P. Member 2 Module Server running at http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server shutting down.")

if __name__ == "__main__":
    run_server()
