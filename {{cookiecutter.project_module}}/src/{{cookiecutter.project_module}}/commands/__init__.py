import asyncio

from ..main import create_app

__all__ = ['create_app', 'make_app']


def make_app(stage=1):
    loop = asyncio.get_event_loop()
    app = create_app(loop=loop, stage=stage)
    await = app.loop.run_until_complete
    return app, await
