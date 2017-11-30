import mimeparse

from functools import partial, wraps
from typing import Union, List, Collection

from aiohttp import web
from aiohttp.web_request import Request


def json_response(func):
    @wraps(func)
    async def wrapper(request):
        response = await func(request)

        kwargs = {}
        kwargs.setdefault('content_type', 'application/json')

        if isinstance(response, Collection):
            data = response
        elif isinstance(response, tuple):
            data, kwargs = response
        else:
            raise ValueError("Wrong value return response={response}".format(repr(response))))

        return web.Response(body=json.dumps(data).encode('utf-8'), **kwargs)

    wrapper.inner = func
    return wrapper


def accept_content(content_types: Union[List, str]):
    if isinstance(content_types, str):
        content_types = [content_types]

    def decorator(func):
        @wraps(func)
        async def wrapper(request):
            header = request.headers.get('ACCEPT', '*/*')
            best_match = mimeparse.best_match(content_types, header)

            if not best_match or best_match not in content_types:
                raise web.HTTPNotAcceptable

            return await func(request)

        return wrapper

    return decorator


def template_view(template_name):
    return partial(render, template_name=template_name)


def redirect(request, name, **kw):
    """Redirect to named url"""
    router = request.app.router
    location = router[name].url(**kw)
    return web.HTTPFound(location=location)


async def render(request, template_name, context: dict=None):
    return aiohttp_jinja2.render_template(template_name, request, context)
