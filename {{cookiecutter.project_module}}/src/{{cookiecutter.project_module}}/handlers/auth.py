import time

import aiohttp
from aiohttp import web
from aiohttp_session import get_session
from bson.objectid import ObjectId

__all__ = ['auth_login', 'auth_logout', 'auth_callback']


async def auth_login(request):
    request_auth_url = build_authorize_url(request)
    return web.HTTPFound(request_auth_url)


async def auth_logout(request):
    session = await get_session(request)
    session.invalidate()

    return web.HTTPFound(request.app['AUTH_LOGIN_URL'])


async def auth_callback(request):
    if request.GET.get('error', None):
        raise web.HTTPUnauthorized(body=b'Unauthorized, denied Google Authentication')

    data, request_access_token_url = build_request_access_url(
        request,
        request.GET.get('code'))

    async with aiohttp.ClientSession() as session:
        async with session.post(request_access_token_url, data=data) as resp:
            token_info = await resp.json()

        if token_info.get('error', None):
            message = token_info['error']

            if message == 'invalid_grant':
                raise web.HTTPFound(request['AUTH_LOGIN_REDIRECT'])

            if 'error_description' in token_info:
                message = f'{message}: {token_info["error_description"]}'

            raise web.HTTPBadRequest(text=message)

        # TODO: deal with reautorize the Access token when expires
        headers = {'Authorization': f'Bearer {token_info["access_token"]}'}

        async with session.get(request.app["GOOGLE_ENDPOINT_USERINFO"], headers=headers) as resp:
            user_info = await resp.json()

        user = await request.app['db'].users.find_one({'email': user_info['email']})
        session = await get_session(request)

        if user:
            await request.app['db'].users.update_one(
                {'_id': ObjectId(user['_id'])},
                {'$set': {'access_token': token_info}})

            session['user'] = str(user['_id'])
        else:
            user_info['access_token'] = token_info

            if user_info['email'] in request.app['ADMINS']:
                user_info['roles'] = 'admin'

            document = await request.app['db'].users.insert_one(user_info)
            session['user'] = str(document.inserted_id)

        session['last_login'] = time.time()

    return web.HTTPFound(request.app['AUTH_LOGIN_REDIRECT'])


def build_authorize_url(request):
    redirect_uri = request.app.router['google_auth_callback'].url_for()
    redirect_uri = f'{request.scheme}://{request.host}{redirect_uri}'

    opts = urlencode({
        'scope': ' '.join([
            'email',
            'profile'
        ]),
        'state': 'security_token',
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'client_id': request.app['GOOGLE_CLIENT_ID'],
        'access_type': 'offline',
    })

    return f"{request.app['GOOGLE_AUTHORIZE_URL']}?{opts}"


def build_request_access_url(request, code):
    redirect_uri = request.app.router['google_auth_callback'].url_for()
    redirect_uri = f'{request.scheme}://{request.host}{redirect_uri}'

    data = {
        'code': code,
        'client_id': request.app['GOOGLE_CLIENT_ID'],
        'client_secret': request.app['GOOGLE_SECRET'],
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }

    return data, request.app['GOOGLE_ACCESS_TOKEN_URL']
