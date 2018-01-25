import base64

from aiohttp import web
from aiohttp.web import middleware
from aiohttp_session import get_session
from bson import ObjectId


@middleware
async def allowed_hosts_middleware(request, handler):
    if request.host not in request.app['ALLOWED_HOSTS']:
        raise web.HTTPBadRequest(text="Bad request: Host not allowed")
    return await handler(request)


@middleware
async def common_middleware(request, handler):
    response = await handler(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Xss-Protection'] = '1; mode=block'

    return response


def setup(app: web.Application):
    app.middlewares.append(allowed_hosts_middleware)
    app.middlewares.append(common_middleware)
