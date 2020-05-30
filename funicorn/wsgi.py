from typing import Callable, List, Tuple, Iterator
import sys
import io
import datetime

from funicorn.http2 import Response, Request, ResponseBuilder, Header, Body


class WSGIApplication:

    def __init__(self, application: Callable):
        self.application = application
        self.buffer_output = io.BytesIO()

        self._request: Request = None

        self._response_builder = ResponseBuilder()
        self._response: Response = None

    @property
    def request(self):
        if not self._request:
            raise Exception('You have to call process_request method first')
        return self._request

    @request.setter
    def request(self, request: Request):
        self._request = request

    @property
    def response(self):
        if not self._response:
            raise Exception('You have to call process_request method first')
        return self._response

    @response.setter
    def response(self, response: Response):
        self.response = response

    def process_request(self, request: Request) -> Response:
        self.request = request

        environ = WSGIEnvironment(request).environ

        http_body = self.application(environ, self.start_response)

        self.set_response_body(http_body)
        response: Response = self._response_builder.build()

        return response

    def set_response_metadata(self, status, headers: List[Tuple[str, str]]):
        default_headers = [("Server", 'funicorn'),
                           ("Date", f'{datetime.date.today()}'),
                           ("Connection", "close"),
                           ("Transfer-Encoding", "chunked")]

        headers = default_headers + headers

        response_headers = [Header(f'{hkey.strip()}', f'{hvalue.strip().lower()}') for hkey, hvalue in headers if hkey.lower() != 'content-length']

        self._response_builder.set_headers(response_headers)
        self._response_builder.set_status(f'{status.strip()}')
        self._response_builder.set_protocol(f'{self.request.protocol}')

    def set_response_body(self, http_response: Iterator[bytes]):
        body = Body()
        for data in http_response:
            body.write(data)

        self._response_builder.set_body(body)

    def start_response(self, status, response_headers: List[Tuple[str, str]], **kwargs):
        self.set_response_metadata(status, response_headers)


class WSGIEnvironment:

    def __init__(self, request: Request):
        self.environ = {}

        self._request = request

        self.set_cgi_environ()
        self.set_wsgi_environ()

    def set_cgi_environ(self):
        self.environ['REQUEST_METHOD'] = self._request.method
        self.environ['SCRIPT_NAME'] = ''
        self.environ['PATH_INFO'] = self._request.uri
        self.environ['QUERY_STRING'] = self._request.query_param
        self.environ['SERVER_NAME'] = self._request.server_name
        self.environ['SERVER_PROTOCOL'] = self._request.protocol
        self.environ['SERVER_PORT'] = '8000'
        self.environ['CONTENT_TYPE'] = self._request.headers.pop('CONTENT_TYPE', Header('', '')).value
        self.environ['CONTENT_LENGTH'] = self._request.headers.pop('CONTENT_LENGTH', Header('', '')).value
        self.environ.update({f'HTTP_{header.key}': header.value for header in self._request.headers.values()})

    def set_wsgi_environ(self):
        self.environ['wsgi.input'] = self._request.body

        self.environ.update({
            "wsgi.errors": sys.stderr,
            "wsgi.version": (1, 0),
            "wsgi.multithread": True,
            "wsgi.input_terminated": True,
            "wsgi.url_scheme": self._request.scheme
        })


class RequestDTO:

    def __init__(self, data: bytes):
        self._data = data

    @property
    def request(self) -> Request:
        return self._to_request()

    def _to_request(self):
        headers, body = self._data.split(b'\r\n\r\n')

        [path, *headers] = headers.decode().splitlines()

        method, path, protocol = path.split(' ')
        uri, query_param = path.split('?') if '?' in path else (path, None)

        headers = [header.split(':') for header in headers]
        headers = [Header(header[0].upper().replace('-', '_'), header[1]) for header in headers]
        headers = {header.key: header for header in headers}

        return Request(method=method, headers=headers, body=Body(body), uri=uri,
                       query_param=query_param, server_name='localhost')


class ResponseDTO:

    def __init__(self, response: Response):
        self._response = response

    @property
    def http_data(self) -> bytes:
        return self._to_http_response()

    def _to_http_response(self) -> bytes:
        buffer = io.BytesIO()

        buffer.write(f'{self._response.protocol} {self._response.status}\r\n'.encode('utf8'))
        buffer.write('\r\n'.join(f'{header.key}: {header.value}' for header in self._response.headers).encode('utf8'))
        buffer.write('\r\n\r\n'.encode('utf8'))

        if self._response.body:
            body_data = [f'{len(self._response.body)}\r\n'.encode('utf8'),
                         self._response.body.read(),
                         b'\r\n']

            buffer.write(b''.join(body_data))

        return buffer.getvalue()
