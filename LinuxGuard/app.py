"""LinuxGuard local dashboard. Uses only the Python stdlib for HTTP serving."""
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from monitor import LinuxMonitor, processes, recommendations, system_info
from security import run_security_scan
from storage import Store

BASE = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('LINUXGUARD_DATA', str(BASE / 'data')))
HOST = os.environ.get('LINUXGUARD_HOST', '127.0.0.1')
PORT = int(os.environ.get('LINUXGUARD_PORT', '8088'))
STORE = Store(DATA_DIR / 'linuxguard.sqlite3')
MONITOR = LinuxMonitor(STORE)


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, mime='application/json; charset=utf-8'):
        if isinstance(data, (dict, list)):
            body = json.dumps(data, allow_nan=False).encode('utf-8')
        elif isinstance(data, str):
            body = data.encode('utf-8')
        else:
            body = data
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        uri = urlsplit(self.path)
        query = parse_qs(uri.query)
        if uri.path in ('/', '/static/styles.css', '/static/app.js'):
            mapping = {'/': ('index.html', 'text/html; charset=utf-8'),
                       '/static/styles.css': ('static/styles.css', 'text/css; charset=utf-8'),
                       '/static/app.js': ('static/app.js', 'text/javascript; charset=utf-8')}
            filename, mimetype = mapping[uri.path]
            return self.reply(200, (BASE / filename).read_bytes(), mimetype)
        if uri.path == '/api/status':
            latest = MONITOR.get_latest()
            score = LinuxMonitor.health_score(latest['cpu'], latest['memory'], latest['disk']) if latest else None
            return self.reply(200, {'sample': latest, 'score': score, 'system': system_info(),
                                    'recommendations': recommendations(latest),
                                    'processes': processes()})
        if uri.path == '/api/history':
            try:
                limit = int(query.get('limit', ['60'])[0])
            except ValueError:
                limit = 60
            return self.reply(200, {'samples': STORE.samples(limit)})
        if uri.path == '/api/alerts':
            return self.reply(200, {'alerts': STORE.alerts(30)})
        return self.reply(404, {'error': 'Route not found'})

    def do_POST(self):
        if urlsplit(self.path).path != '/api/security-scan':
            return self.reply(404, {'error': 'Route not found'})
        # Prevent cross-origin browser POSTs. This is not a substitute for authentication.
        origin = self.headers.get('Origin', '')
        if origin:
            expected = f'http://{self.headers.get("Host", "")}'
            if origin != expected:
                return self.reply(403, {'error': 'Cross-origin request blocked'})
        return self.reply(200, run_security_scan(STORE))

    def log_message(self, fmt, *args):
        print(f'[{self.log_date_time_string()}] {self.address_string()} {fmt % args}')


def main():
    if HOST not in ('127.0.0.1', '::1', 'localhost'):
        raise SystemExit('For safety LinuxGuard only permits localhost binding. Set LINUXGUARD_HOST=127.0.0.1.')
    MONITOR.start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f'LinuxGuard running at http://{HOST}:{PORT} (Ctrl+C to exit)')
    print('This is a local student demo; no authentication is included.')
    try:
        server.serve_forever(poll_interval=.3)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        MONITOR.stop()


if __name__ == '__main__':
    main()
