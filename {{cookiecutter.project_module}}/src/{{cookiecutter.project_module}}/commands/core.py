import io
import click

from click import get_current_context
from contextlib import redirect_stdout

from . import make_app


def command_diffsettings():
    """Show the loaded configuration in settings"""
    app, await = make_app()

    for key in app.keys():
        if key.isupper():
            click.echo(f'{key} = {app[key]}\n')


def command_showurls():
    """List application urls"""
    app, await = make_app(stage=3)

    click.echo(f'{("METHOD"):>8} {("URL"):38} {("HANDLER"):60} NAME')
    click.echo()

    for route in app.router.routes():
        if route.method == 'HEAD':
            continue

        handler = f'{route.handler.__module__}.{route.handler.__name__}'
        name = str(route.name)
        info = route.get_info()

        if 'formatter' in info:
            url = info['formatter']
        elif 'path' in info:
            url = info['path']
        elif 'directory' in info:
            url = f"{info['prefix']}/*"
        else:
            url = None

        if url:
            click.echo(f'{route.method:>8} {url:38} {handler:60} {name}')

