from aiohttp import web

from .auth import *
from .user import *
from .home import *


def setup(app: web.Application):
    from os import makedirs
    from os.path import exists

    static_dir = app['STATIC_ROOT']
    media_dir = app['MEDIA_ROOT']

    if not exists(static_dir):
        makedirs(static_dir, exist_ok=True)

    if not exists(media_dir):
        makedirs(media_dir, exist_ok=True)

    app.router.add_static('/static/', path=static_dir, name='static')
    app.router.add_static('/media/', path=media_dir, name='media')

    app.router.add_get('/', handler_landing, name='landing')

    app.router.add_get('/auth/login/', auth_login, name='login')
    app.router.add_get('/auth/logout/', auth_logout, name='logout')
    app.router.add_get('/auth/authorize/', auth_callback, name='google_auth_callback')

    app.router.add_get('/user/', user_detail, name='user_detail')
    app.router.add_post('/user/edit/',user_edit, name='user_edit')
