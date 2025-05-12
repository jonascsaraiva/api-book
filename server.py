# server.py
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

books = [
    {"id": 1, "title": "1984", "author": "George Orwell"},
    {"id": 2, "title": "Brave New World", "author": "Aldous Huxley"}
]
next_id = 3

class SimpleAPI(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')

        if path_parts[0] == 'books':
            if len(path_parts) == 1:
                self._set_headers()
                self.wfile.write(json.dumps(books).encode())
            elif len(path_parts) == 2:
                try:
                    book_id = int(path_parts[1])
                    book = next((b for b in books if b["id"] == book_id), None)
                    if book:
                        self._set_headers()
                        self.wfile.write(json.dumps(book).encode())
                    else:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "Book not found"}).encode())
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid ID"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        global next_id
        if self.path == '/books':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
                new_book = {"id": next_id, "title": data["title"], "author": data["author"]}
                books.append(new_book)
                next_id += 1
                self._set_headers(201)
                self.wfile.write(json.dumps(new_book).encode())
            except (json.JSONDecodeError, KeyError):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid data"}).encode())

def run():
    server = HTTPServer(('0.0.0.0', 8000), SimpleAPI)
    print("Server running on port 8000...")
    server.serve_forever()

if __name__ == '__main__':
    run()