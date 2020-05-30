from socketserver import BaseRequestHandler, TCPServer
from typing import Tuple

from funicorn.http2 import Request, Response
from funicorn.utils import load_application
from funicorn.wsgi import RequestDTO, ResponseDTO


class FunicornHandler(BaseRequestHandler):
    app_path: Tuple[str, str] = None

    def handle(self):
        application = load_application(self.app_path[0], self.app_path[1])

        http_request = self.request.recv(1024)

        request: Request = RequestDTO(http_request).request

        response: Response = application.process_request(request)

        response_data = ResponseDTO(response).http_data
        self.request.sendall(response_data)


class Funicorn:

    def __init__(self, app_path: str, app_obj: str, host: str, port: int):
        FunicornHandler.app_path = (app_path, app_obj)

        self.server = TCPServer((host, port), FunicornHandler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()


if __name__ == '__main__':

    try:
        f = Funicorn(app_path='examples.flask', app_obj='app', host='localhost', port=8001)
        print('port 8001')
    except Exception:
        f = Funicorn(app_path='examples.flask', app_obj='app', host='localhost', port=8000)
        print('port 8000')

    f.run()

