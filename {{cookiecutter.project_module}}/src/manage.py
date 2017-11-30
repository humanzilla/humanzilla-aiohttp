import asyncio
from sys import stdout

import click
from aiohttp import web

from {{ cookiecutter.project_module }}.main import create_app


@click.group()
@click.option('--debug/--no-debug', default=True)
@click.pass_context
def cli(ctx, debug):
    ctx.obj = {'DEBUG': debug}


@cli.command()
def diffsettings():
    loop = asyncio.get_event_loop()
    app = create_app(loop, stage=0)

    for key in app.keys():
        if key.isupper():
            stdout.write(f'{key} = {app[key]}\n')
            stdout.flush()


@cli.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default='8000', type=int)
@click.pass_context
def runserver(ctx, host, port):
    click.echo('Performing system check')
    loop = asyncio.get_event_loop()
    web.run_app(create_app(loop, debug=ctx.obj['DEBUG']), host=host, port=port)


if __name__ == '__main__':
    cli()
