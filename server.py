from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, start_http_server

# Configura logs
logging.basicConfig(level=logging.INFO)

# Inicia Prometheus em porta separada
start_http_server(8001)

# Métricas Prometheus
REQUEST_COUNTER = Counter(
    'api_requests_total',
    'Total de requisições na API',
    ['method', 'endpoint', 'status_code']
)

# Dados em memória
books = []

class SimpleHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/books':
            self._send_response(200, books, method='GET', endpoint='/books')
        elif self.path == '/health':
            self._send_response(200, {'status': 'ok'}, method='GET', endpoint='/health')
        elif self.path == '/metrics':
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest())
        else:
            self._send_response(404, {'error': 'Not found'}, method='GET', endpoint=self.path)

    def do_POST(self):
        if self.path == '/books':
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            book = json.loads(data)
            books.append(book)
            self._send_response(201, book, method='POST', endpoint='/books')
        else:
            self._send_response(404, {'error': 'Not found'}, method='POST', endpoint=self.path)

    def do_DELETE(self):
        if self.path.startswith('/books/'):
            book_id = self.path.split('/')[-1]
            global books
            books = [b for b in books if str(b.get('id')) != book_id]
            self._send_response(204, None, method='DELETE', endpoint='/books/:id')
        else:
            self._send_response(404, {'error': 'Not found'}, method='DELETE', endpoint=self.path)

    def _send_response(self, code, data=None, method='GET', endpoint='unknown'):
        # Registra no Prometheus
        REQUEST_COUNTER.labels(method=method, endpoint=endpoint, status_code=str(code)).inc()

        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if data is not None and code != 204:
            self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    logging.info("Iniciando API em http://localhost:8000")
    server = HTTPServer(('0.0.0.0', 8000), SimpleHandler)
    server.serve_forever()
