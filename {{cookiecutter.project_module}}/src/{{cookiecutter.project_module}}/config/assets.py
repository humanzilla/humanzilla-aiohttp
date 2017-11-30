from os import makedirs
from os.path import exists

from aiohttp import web


def setup(app: web.Application):
    static_dir = app['STATIC_ROOT']
    media_dir = app['MEDIA_ROOT']

    if not exists(static_dir):
        makedirs(static_dir, exist_ok=True)

    if not exists(media_dir):
        makedirs(media_dir, exist_ok=True)

    app.router.add_static('/static/', path=static_dir, name='static')
    app.router.add_static('/media/', path=media_dir, name='media')
