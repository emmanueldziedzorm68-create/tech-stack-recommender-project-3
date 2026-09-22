"""Run the local browser interface with: python app.py"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from recommender import Recommender

engine = Recommender()
PAGE = Path(__file__).with_name('index.html')


class Handler(BaseHTTPRequestHandler):
    def send(self, status, data, content_type='application/json; charset=utf-8'):
        body = json.dumps(data).encode() if isinstance(data, dict) else data
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/':
            self.send(200, PAGE.read_bytes(), 'text/html; charset=utf-8')
        elif self.path == '/api/skills':
            self.send(200, {'skills': sorted(engine.idf), 'role_count': len(engine.roles)})
        else:
            self.send(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path != '/api/recommend':
            self.send(404, {'error': 'Not found'})
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 16384:
                raise ValueError('Request must contain between 1 and 16384 bytes.')
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError('Request must be a JSON object.')
            result = engine.recommend(payload.get('skills'), goals=payload.get('goals'))
            self.send(200, result)
        except (ValueError, UnicodeError) as error:
            self.send(400, {'error': str(error)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Open http://127.0.0.1:{server.server_port} | Press Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
