import asyncio
import click
import uvloop

from aiohttp import web
from click import get_current_context

from . import create_app


@click.option('--host', default='127.0.0.1')
@click.option('--port', default='8000', type=int)
@click.option('--path')
def command_runserver(host, port, path):
    """Run the web application server"""

    ctx = get_current_context()
    kwargs = {'shutdown_timeout': 5}

    if path:
        kwargs.update({'path': path})
    else:
        kwargs.update({'port': port, 'host': host})

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()
    web.run_app(create_app(loop, debug=ctx.obj['DEBUG']), **kwargs)
