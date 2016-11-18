import os

import aiohttp_debugtoolbar
import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_debugtoolbar import toolbar_middleware_factory
from cryptography import fernet
import base64

from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from .middlewares import error_middleware

location = lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def config_static(app):
    app.router.add_static('/static/', path=location('static'), name='static')
    app.router.add_static('/media/', path=location('../public/media'), name='media')


def config_templates(app):
    template_loader = jinja2.FileSystemLoader(location('templates'))
    aiohttp_jinja2.setup(
        app,
        loader=template_loader,
        extensions=[
            'jinja2.ext.with_',
            'jinja2.ext.loopcontrols'
        ])


def make_app(debug=False):
    app = web.Application(middlewares=[toolbar_middleware_factory])
    app['debug'] = debug

    # Session
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))

    # Debug
    aiohttp_debugtoolbar.setup(app)
    app.middlewares.append(error_middleware)

    config_templates(app)
    config_static(app)

    return app
