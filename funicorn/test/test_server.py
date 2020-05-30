from threading import Thread

import pytest
import requests

from funicorn.main import Funicorn


@pytest.fixture(scope="module")
def funicorn_server():
    app_path, app_obj = ('funicorn.examples.flask', 'app')
    try:
        host, port = ('localhost', 8000)
        server = Funicorn(app_path=app_path, app_obj=app_obj, host=host, port=port)
    except Exception:
        host, port = ('localhost', 8001)
        server = Funicorn(app_path=app_path, app_obj=app_obj, host=host, port=port)

    thread = Thread(target=server.run)
    thread.setDaemon(True)
    thread.start()

    print(f'{host}:{port}')
    yield (host, port)

    server.stop()


def test_get_success(funicorn_server):
    response = requests.get(f'http://{funicorn_server[0]}:{funicorn_server[1]}/hola')

    assert response.status_code == 200
    assert response.text == 'Hello World'


def test_post_success(funicorn_server):
    data = {'hola': 1}
    response = requests.post(f'http://{funicorn_server[0]}:{funicorn_server[1]}/hola', json=data)

    assert response.status_code == 200
    assert response.json() == data


def test_get_not_found(funicorn_server):
    response = requests.get(f'http://{funicorn_server[0]}:{funicorn_server[1]}/adios')

    assert response.status_code == 404
