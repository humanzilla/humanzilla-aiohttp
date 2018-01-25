import importlib
import os
import re
from os.path import abspath, dirname, join


def load_envfile():
    envpath = join(dirname(dirname(dirname(dirname(abspath(__file__))))), '.env')

    if os.path.exists(envpath):
        with open(envpath, 'rt') as fobj:
            for line in fobj:
                line = line.strip()

                if line and not line.startswith('#'):
                    key, value = re.split(r'\s?=\s?', line, 1)

                    quoted = re.match(r'''[^"]*"(.+)"''', value)

                    if quoted:
                        value = str(quoted.groups()[0])
                    elif value in {'true', 'on', 'yes'}:
                        value = 'True'
                    elif value in {'false', 'off', 'no'}:
                        value = 'False'

                    for match_replace in re.findall(r'(\${([\w\d\-_]+)})', value):
                        # Reference variables in values
                        # ej: DB_DEBUG = ${DEBUG}

                        replace, name = match_replace
                        value = value.replace(replace, os.environ.get(name, ''))

                    os.environ.setdefault(key, value)


def register_settings(app):
    settings_module = os.environ.get('AIOHTTP_SETTINGS_MODULE', '{{ cookiecutter.project_module }}.settings')
    mod = importlib.import_module(settings_module)

    for setting in dir(mod):
        if setting.isupper() and setting not in app:
            value = getattr(mod, setting)
            app[setting] = value


def setup(app):
    load_envfile()
    register_settings(app)
