import asyncio
from functools import wraps
import os
import socket
import pytest

from {{ cookiecutter.project_module }}.main import create_app


@pytest.yield_fixture('function')
def application(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    app = create_app(loop=loop)

    yield app

    loop.run_until_complete(app.close())
    loop.run_until_complete(app.finish())
    loop.close()


async def create_server(application):
    def find_unused_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = find_unused_port()

    server = await application.loop.create_server(
        application.make_handler(keep_alive=False),
        host='127.0.0.1',
        port=port)

    url = 'http://127.0.0.1:{port}'.format(port=port)
    return server, url


def async_test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        application = kwargs.get('application')
        application.loop.run_until_complete(func(*args, **kwargs))

    return wrapper
