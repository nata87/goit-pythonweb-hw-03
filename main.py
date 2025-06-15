from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote_plus
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import json
import mimetypes

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"  # якщо шаблони в підпапці
STORAGE_DIR = BASE_DIR / "storage"
DATA_FILE = STORAGE_DIR / "data.json"

env = Environment(loader=FileSystemLoader("."))


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/':
            self.send_html('index.html')
        elif parsed_url.path == '/message.html':
            self.send_html('message.html')
        elif parsed_url.path == '/read':
            self.send_read_page()
        else:
            if Path(BASE_DIR / parsed_url.path[1:]).exists():
                self.send_static(parsed_url.path[1:])
            else:
                self.send_html('error.html', status=404)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/message':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data_parse = unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            self.save_message(data_dict)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_html('error.html', status=404)

    def send_html(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(BASE_DIR / filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_static(self, filepath):
        self.send_response(200)
        mt, _ = mimetypes.guess_type(filepath)
        self.send_header("Content-type", mt or "application/octet-stream")
        self.end_headers()
        with open(BASE_DIR / filepath, 'rb') as f:
            self.wfile.write(f.read())

    def save_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        if DATA_FILE.exists():
            with open(DATA_FILE, encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        data[timestamp] = message

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def send_read_page(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        template = env.get_template('read.html')
        html_content = template.render(messages=data)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

def run():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server started on http://localhost:3000")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run()
