import click
import glob

from click import command
from importlib import import_module
from pathlib import Path

from {{cookiecutter.project_module}}.main import create_app

project_root = Path(__file__).parent.resolve() / "{{ cookiecutter.project_module }}"


@click.group()
@click.option('--verbose')
@click.option('--debug/--no-debug', default=True)
@click.pass_context
def cli(ctx, verbose, debug):
    ctx.obj = {'DEBUG': debug, 'VERBOSE': verbose}


def load_commands():
    command_dirs = project_root / 'commands'

    for fname in glob.glob(str(command_dirs / '*.py')):
        fname = Path(fname)

        if not str(fname.name).startswith('_'):
            name = fname.name.strip('.py')
            mod = import_module(f'{project_root.name}.commands.{name}')

            for prop in dir(mod):
                if prop.startswith('command_'):
                    command_handler = getattr(mod, prop)
                    command_name = command_handler.__name__[8:]
                    make_command = command(name=f'{name}:{command_name}')
                    cli.add_command(make_command(command_handler))


if __name__ == '__main__':
    load_commands()
    cli()
