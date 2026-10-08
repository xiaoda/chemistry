"""Task-owned, loopback-only static preview with a strict route allowlist."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.preview'


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond(head=False)

    def respond(self, head):
        path = urlsplit(self.path).path
        if path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        if path not in ('/', '/lesson-01.html'):
            self.send_error(404, 'Not found')
            return
        content = (ROOT / 'lesson-01.html').read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        if not head:
            self.wfile.write(content)


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    port = server.server_address[1]
    RUNTIME.mkdir(exist_ok=True)
    metadata = {'task': 'chemistry-lesson-01', 'pid': os.getpid(), 'cwd': str(ROOT), 'host': '127.0.0.1', 'port': port, 'url': f'http://127.0.0.1:{port}/lesson-01.html'}
    (RUNTIME / 'server.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False), flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
