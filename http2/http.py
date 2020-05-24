import io
from typing import List, Dict, Any

import sys


class Body:

    def __init__(self, data: bytes):
        self._data = io.BytesIO(data)

    def read(self):
        return self._data.read()


class Header:

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class Request:

    def __init__(self, method: str, uri: str, headers: List[Header], body: Body, query_param: str, server_name: str,
                 ssl=False):
        self.method = method
        self.headers = headers
        self.body = body
        self.uri = uri
        self.server_name = server_name
        self.query_param = query_param
        self.scheme = 'https' if ssl else 'http2'


class RequestBuilder:

    def __init__(self):
        self.method = None
        self.headers = None
        self.body = None
        self.uri = None
        self.query_param = None
        self.server_name = 'localhost'

    def build(self) -> Request:
        return Request(method=self.method, headers=self.headers, body=self.body, uri=self.uri,
                       query_param=self.query_param, server_name=self.server_name)


class RequestFactory:

    @staticmethod
    def from_wsgi_data(data: bytes) -> Request:
        builder = RequestBuilder()

        headers, body = data.split(b'\r\n\r\n')

        [path, *headers] = headers.decode().splitlines()

        builder.method, path, builder.protocol = path.split(' ')
        builder.uri, builder.query_param = path.split('?') if '?' in path else (path, None)
        headers = [header.split(':') for header in headers]
        builder.headers = [Header(header[0].replace('-','_'), header[1]) for header in headers]

        return builder.build()


class Response:

    def __init__(self):
        self.status = None
        self.headers = []
        self.headers_sent = False
        self.body = None

    def write_headers(self):
        pass

    def write(self, data: bytes):
        pass

    def start_response(self, status, headers, exc_info=None):
        return self.write
