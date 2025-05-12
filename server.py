from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, start_http_server

# Configura logs
logging.basicConfig(level=logging.INFO)

# Inicia Prometheus em porta separada
start_http_server(8001)

# Métricas Prometheus
REQUEST_COUNT = Counter('api_requests_total', 'Total de requisições HTTP', ['method', 'endpoint'])

# Dados em memória
books = []

class SimpleHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        REQUEST_COUNT.labels(method='GET', endpoint=self.path).inc()
        if self.path == '/books':
            self._send_response(200, books)
        elif self.path == '/health':
            self._send_response(200, {'status': 'ok'})
        elif self.path == '/metrics':
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest())
        else:
            self._send_response(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path == '/books':
            REQUEST_COUNT.labels(method='POST', endpoint=self.path).inc()
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            book = json.loads(data)
            books.append(book)
            self._send_response(201, book)
        else:
            self._send_response(404, {'error': 'Not found'})

    def do_DELETE(self):
        if self.path.startswith('/books/'):
            REQUEST_COUNT.labels(method='DELETE', endpoint='/books/:id').inc()
            book_id = self.path.split('/')[-1]
            global books
            books = [b for b in books if str(b.get('id')) != book_id]
            self._send_response(204)
        else:
            self._send_response(404, {'error': 'Not found'})

    def _send_response(self, code, data=None):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if data is not None:
            self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    logging.info("Iniciando API em http://localhost:8000")
    server = HTTPServer(('0.0.0.0', 8000), SimpleHandler)
    server.serve_forever()
