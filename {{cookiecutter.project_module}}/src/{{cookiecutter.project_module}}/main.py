from aiohttp import web

from {{ cookiecutter.project_module }}.shortcuts import render


async def landing(request):
    return await render(request, 'landing.html')


class Application(web.Application):
    def __repr__(self):
        return "<{{ cookiecutter.project_module }} 0x{:x}>".format(id(self))

    def setup(self, stage=3):
        from . import config, handlers

        config.settings.setup(self)

        if stage < 1:
            return self

        if stage > 0:
            config.database.setup(self)

        if stage > 1:
            config.assets.setup(self)
            config.templates.setup(self)
            config.middleware.setup(self)

            self.router.add_get('/', landing, name='landing')

            self.router.add_get('/auth/login/', handlers.auth_login, name='login')
            self.router.add_get('/auth/logout/', handlers.auth_logout, name='logout')
            self.router.add_get('/auth/authorize/', handlers.auth_callback, name='google_auth_callback')

            self.router.add_get('/user/', handlers.user_detail, name='user_detail')
            self.router.add_post('/user/edit/', handlers.user_edit, name='user_edit')


def create_app(loop, debug=True, stage: int = 3):
    from . import config, handlers
    from .shortcuts import template_view

    app = Application(loop=loop, debug=debug)
    app.setup(stage=stage)

    return app
