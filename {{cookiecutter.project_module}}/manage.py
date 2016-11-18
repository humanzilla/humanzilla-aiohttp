import click
from aiohttp import web

from {{cookiecutter.project_module}}.core.utils import check
from {{cookiecutter.project_module}}.apps import make_app


@click.group()
@click.option('--debug/--no-debug', default=True)
@click.pass_context
def cli(ctx, debug):
    ctx.obj = {}
    ctx.obj['DEBUG'] = debug
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default='8000', type=int)
@click.pass_context
def runserver(ctx, host, port):
    click.echo('Performing system check')

    with check('Check database settings'):
        raise check.Failed()

    web.run_app(make_app(ctx.obj['DEBUG']), host=host, port=port)


if __name__ == '__main__':
    cli()
