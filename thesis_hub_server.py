import http.server
import json
import os
import sqlite3
import urllib.parse
from models.thesis_hub import ThesisHubModel
from controllers.thesis_hub_controller import ThesisHubController

PORT = int(os.environ.get("THESIS_HUB_PORT", 8000))
BASE_DIR = os.path.dirname(__file__)

class StandaloneThesisHubHandler(http.server.SimpleHTTPRequestHandler):

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
        params = urllib.parse.parse_qs(parsed.query)
        params_flat = {k: v[0] for k, v in params.items()}

        if path.startswith("/api/download/"):
            filename = os.path.basename(path)
            content = ThesisHubController.get_download(filename)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        if path.startswith("/api/"):
            if path == "/api/milestones":
                return self.respond_json(ThesisHubController.get_milestones())
            elif path == "/api/documents":
                return self.respond_json(ThesisHubController.get_documents())
            elif path == "/api/citations":
                return self.respond_json(ThesisHubController.get_citations())
            elif path == "/api/resources":
                return self.respond_json(ThesisHubController.get_resources())
            elif path == "/api/archive":
                return self.respond_json(ThesisHubController.search_archive(params_flat))

            return self.respond_json({"error": "Not Found"}, 404)

        # Serve frontend files
        if path in ("/", "/index.html"):
            target_file = os.path.join(BASE_DIR, "templates", "index.html")
        else:
            target_file = os.path.join(BASE_DIR, path.lstrip("/"))

        if os.path.exists(target_file) and os.path.isfile(target_file):
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
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if parsed.path == "/api/milestones/update":
            return self.respond_json(ThesisHubController.update_milestone(payload))
        elif parsed.path == "/api/milestones/add":
            return self.respond_json(ThesisHubController.add_milestone(payload))
        elif parsed.path == "/api/documents/save":
            return self.respond_json(ThesisHubController.save_document(payload))
        elif parsed.path == "/api/documents/feedback":
            return self.respond_json(ThesisHubController.update_document_feedback(payload))
        elif parsed.path == "/api/citations/add":
            return self.respond_json(ThesisHubController.add_citation(payload))
        elif parsed.path == "/api/resources/add":
            return self.respond_json(ThesisHubController.add_resource(payload))
        elif parsed.path == "/api/ai-assistant":
            return self.respond_json(ThesisHubController.ask_ai_assistant(payload))
        elif parsed.path == "/api/archive/add":
            return self.respond_json(ThesisHubController.add_archive_thesis(payload))

        return self.respond_json({"error": "Bad Request"}, 400)


if __name__ == "__main__":
    ThesisHubModel.init_db()
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, StandaloneThesisHubHandler)
    print(f"🚀 Thesis Hub Standalone Server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
