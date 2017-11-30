from collections import defaultdict
from datetime import datetime

from aiohttp import web


class Application(web.Application):
    def __repr__(self):
        return "<{{ cookiecutter.project_module }} 0x{:x}>".format(id(self))


def create_app(loop, debug=True, stage: int = 3):
    from . import config, handlers
    from .shortcuts import template_view

    app = Application(loop=loop, debug=debug)

    config.settings.setup(app)

    if stage < 1:
        return app

    if stage > 0:
        config.database.setup(app)

    if stage > 1:
        config.assets.setup(app)
        config.templates.setup(app)
        config.middleware.setup(app)

        app.router.add_get('/', template_view('landing.html'), name='landing')

        app.router.add_get('/auth/login/', handlers.auth_login, name='login')
        app.router.add_get('/auth/logout/', handlers.auth_logout, name='logout')
        app.router.add_get('/auth/authorize/', handlers.auth_callback, name='google_auth_callback')

        app.router.add_get('/user/', handlers.user_detail, name='user_detail')
        app.router.add_post('/user/edit/', handlers.user_edit, name='user_edit')

    return app
