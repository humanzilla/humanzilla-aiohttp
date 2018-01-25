from aiohttp import web

from {{ cookiecutter.project_module }}.shortcuts import render


__ENVIRONMEMT__ = os.environ.get('ENVIRONMENT', 'development') == 'testing'

assert __ENVIRONMEMT__ in ['develop', 'testing', 'production'], f'Unknown environment {__ENVIRONMEMT__}'


class Application(web.Application):
    def __repr__(self):
        return "<{{ cookiecutter.project_module|title }} 0x{:x}>".format(id(self))

    def setup(self, stage=3):
        from . import config, handlers

        config.config.setup(self)

        if stage >= 1:
            config.database.setup(self)

        if stage < 2:
            return self

        if not self.debug and __ENVIRONMEMT__ != 'testing':
            logging.config.dictConfig(self['LOGGING'])

        config.errors.setup(self)
        config.sessions.setup(self)
        config.middleware.setup(self)
        config.tasks.setup(self)
        config.templates.setup(self)

        handlers.setup()


def create_app(loop, debug=True, stage: int = 3):
    app = Application(loop=loop, debug=debug)
    app.setup(stage=stage)
    return app
