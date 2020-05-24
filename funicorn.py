import datetime
import io
from socketserver import ThreadingTCPServer, BaseRequestHandler
from typing import Tuple, List

import sys

from http2.http import Request, RequestFactory
from utils import load_application


class FunicornWorker(BaseRequestHandler):
    app_path: Tuple[str, str] = None

    def handle(self):
        self.environ = {}
        self.buffer_output = io.BytesIO()
        request = self._get_wsgi_request()
        self.set_cgi_environ(request)
        self.set_wsgi_environ(request)
        application = load_application(self.app_path[0], self.app_path[1])
        response = application(self.environ, self.start_response)

        for data in response:
            self.write_chunk(data)

    def _get_wsgi_request(self) -> Request:
        return RequestFactory.from_wsgi_data(self.request.recv(1024))

    def set_cgi_environ(self, request: Request):
        self.environ['REQUEST_METHOD'] = request.method
        self.environ['SCRIPT_NAME'] = ''
        self.environ['PATH_INFO'] = request.uri
        self.environ['QUERY_STRING'] = request.query_param
        self.environ['SERVER_NAME'] = request.server_name
        self.environ['SERVER_PROTOCOL'] = 'HTTP/1.1'
        self.environ['SERVER_PORT'] = '8000'
        self.environ.update({f'HTTP_{header.key}'.upper(): header.value for header in request.headers})

    def set_wsgi_environ(self, request: Request):
        self.environ['wsgi.input'] = request.body

        self.environ.update({
            "wsgi.errors": sys.stderr,
            "wsgi.version": (1, 0),
            "wsgi.multithread": True,
            "wsgi.input_terminated": True,
            "wsgi.url_scheme": request.scheme
        })

    def write_chunk(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')

        headers = self.buffer_output.getvalue()

        body_size = f'{len(data)}\r\n'.encode('utf8')
        body = b"".join([body_size, data, b"\r\n"])

        self.send_response(headers, body)

    def write(self, data: bytes):
        self.buffer_output.write(data)

    def write_headers(self, status, headers: List[Tuple[str, str]]):
        self.write(f'HTTP/1.1 {status.strip()}\r\n'.encode('utf8'))

        default_headers = [("Server", 'funicorn'), ("Date", f'{datetime.date.today()}'), ("Connection", "close"),
                           ("Transfer-Encoding", "chunked")]
        headers = default_headers + headers

        for hkey, hvalue in headers:
            if hkey.lower() != 'content-length':
                self.write(f'{hkey.strip()}: {hvalue.strip().lower()}\r\n'.encode('utf8'))

        self.write('\r\n'.encode())

    def start_response(self, status, response_headers: List[Tuple[str, str]], **kwargs):
        self.write_headers(status, response_headers)

    def send_response(self, headers, body):
        self.request.sendall(headers)
        self.request.sendall(body)


class Funicorn:

    def __init__(self, app_path: str, app_obj: str, host: str, port: int):
        FunicornWorker.app_path = (app_path, app_obj)

        self.server = ThreadingTCPServer((host, port), FunicornWorker)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()


if __name__ == '__main__':

    f = Funicorn('flask_example', 'app', 'localhost', 8000)

    try:
        f.run()
    except KeyboardInterrupt:
        f.stop()
