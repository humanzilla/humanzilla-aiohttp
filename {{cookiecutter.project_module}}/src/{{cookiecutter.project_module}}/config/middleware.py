import base64

from aiohttp import web
from aiohttp.web import middleware
from aiohttp_session import get_session
from bson import ObjectId


@middleware
async def common_middleware(request, handler):
    response = await handler(request)
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Xss-Protection'] = '1; mode=block'

    return response


@middleware
async def auth_middleware(request, handler):
    if request.app.debug or True:
        request['user'] = {
            'given_name': 'admin',
            'picture': None,
            'roles': ['admin']}

        return await handler(request)

    session = await get_session(request)
    user_id = session.get('user', None)

    if not user_id:
        if request.path.startswith('/auth'):
            session.invalidate()
            return await handler(request)
        else:
            raise web.HTTPFound(request.app['AUTH_LOGIN_URL'])

    user = await request.app['db'].users.find_one({'_id': ObjectId(user_id)})

    if not user:
        session.invalidate()
        # TODO: Allow just registered users
        # return await handler(request)
        raise web.HTTPFound(request.app['AUTH_LOGIN_URL'])

    request['user'] = user

    return await handler(request)


@middleware
async def append_slash_middleware(request, handler):
    response = await handler(request)

    if isinstance(response, web.HTTPNotFound) or response.status == 404:
        if not request.path.endswith('/'):
            raise web.HTTPFound(f'{request.path}/')

    return response


@middleware
async def allowed_hosts_middleware(request, handler):
    if request.host not in request.app['ALLOWED_HOSTS']:
        raise web.HTTPBadRequest(text="Bad request: Host not allowed")
    return await handler(request)


def configure_session(app: web.Application):
    from aiohttp_session import setup
    from aiohttp_session.cookie_storage import EncryptedCookieStorage
    from cryptography import fernet

    # Session
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))


def setup(app: web.Application):
    import aiohttp_debugtoolbar
    from aiohttp_debugtoolbar import toolbar_middleware_factory

    app.middlewares.append(allowed_hosts_middleware)
    app.middlewares.append(append_slash_middleware)
    app.middlewares.append(common_middleware)

    configure_session(app)
    app.middlewares.append(auth_middleware)

    if app.debug:
        app.middlewares.append(toolbar_middleware_factory)
        aiohttp_debugtoolbar.setup(app, intercept_redirects=False)
