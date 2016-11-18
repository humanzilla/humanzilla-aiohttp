import json
import aiohttp_jinja2
from aiohttp import web


async def json_response(data, **kwargs):
    kwargs.setdefault('content_type', 'application/json')
    return web.Response(body=json.dumps(data).encode('utf-8'), **kwargs)


async def handle_404(request, response):
    response = aiohttp_jinja2.render_template('404.html', request, {})
    return response


async def handle_500(request, response):
    response = aiohttp_jinja2.render_template('500.html', request, {})
    return response
