import motor.motor_asyncio
from aiohttp import web
from pymongo.uri_parser import parse_uri


def setup(app: web.Application):
    config = parse_uri(app['MONGODB_DSN'])
    client = motor.motor_asyncio.AsyncIOMotorClient(
        app['MONGODB_DSN'],
        io_loop=app.loop,
    )

    async def close_connection(app):
        client.close()

    app['db'] = client[config['database']]
    app['client'] = client

    app.on_cleanup.append(close_connection)
