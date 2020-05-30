import io
from collections import OrderedDict
from typing import List, Dict, Optional


class Body:

    def __init__(self, data: bytes = None):
        self._data = io.BytesIO(data) if data else io.BytesIO()

    def read(self):
        return self._data.getvalue()

    def write(self, data: bytes):
        return self._data.write(data)

    def __len__(self):
        return len(self._data.getvalue())


class Header:

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class Request:

    def __init__(self, method: str, uri: str, headers: Dict[str, Header], body: Body, query_param: Optional[str],
                 server_name: str, ssl=False, protocol: str='HTTP/1.1'):
        self.method = method
        self.headers = headers
        self.body = body
        self.uri = uri
        self.server_name = server_name
        self.query_param = query_param or ''
        self.scheme = 'https' if ssl else 'http'
        self.protocol = protocol


class Response:

    def __init__(self, status: str, headers: List[Header], body: Body, protocol: str):
        self.status = status
        self.headers = headers
        self.body = body
        self.protocol = protocol


class ResponseBuilder:

    def __init__(self):
        self.headers: List[Header] = None
        self.status: str = None
        self.body: Body = None
        self.protocol: str = 'HTTP/1.1'

    def set_headers(self, headers: List[Header]):
        self.headers = headers

    def set_status(self, status: str):
        self.status = status

    def set_body(self, body: Body):
        self.body = body

    def set_protocol(self, protocol: str):
        self.protocol = protocol

    def build(self) -> Response:
        return Response(status=self.status, headers=self.headers, body=self.body, protocol=self.protocol)

