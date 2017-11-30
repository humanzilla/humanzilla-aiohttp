import aiohttp_jinja2
import jinja2
from aiohttp import web
from bson.json_util import dumps, loads
from json2html import json2html


def tobson_filter(value):
    return dumps(value)


def astable_filter(value):
    return json2html.convert(
        json=loads(dumps(value)),
        table_attributes='class="table table-sm"')


@jinja2.contextfunction
def static(context, value):
    app = context['app']
    url = app.router['static'].url_for(filename=value)
    return f'{url}?{app["started"].timestamp()}'


async def user_context_processor(request):
    return {'user': getattr(request, 'user', None)}


def setup(app: web.Application):
    template_loader = jinja2.FileSystemLoader(app['TEMPLATES_DIRS'])

    environment.aiohttp_jinja2.setup(
        app=app,
        loader=template_loader,
        context_processors=[user_context_processor],
        extensions=[
            'jinja2.ext.with_',
            'jinja2.ext.loopcontrols'
        ])

    environment.filters['astable'] = astable_filter
    environment.filters['tobson'] = tobson_filter
    environment.globals['static'] = static
