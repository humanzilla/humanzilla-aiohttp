import asyncio
import os

import pytest
from aiohttp.test_utils import loop_context
from motor import motor_asyncio

from {{ cookiecutter.project_module }}.main import create_app


def pytest_configure(config):
    os.environ['ENVIRONMENT'] = 'testing'
    os.environ['MONGODB_DSN'] = 'mongodb://localhost:27017/wiki_test'


@pytest.fixture
def loop(loop_factory, fast, loop_debug):
    """Return an instance of the event loop."""
    with loop_context(loop_factory, fast=fast) as _loop:
        if loop_debug:
            _loop.set_debug(True)  # pragma: no cover

        _loop._close = _loop.close
        _loop.close = lambda: None

        yield _loop

        # _loop._close() # TODO: Enable again when needed

    asyncio.set_event_loop(None)


@pytest.fixture()
def webapp(loop):
    app = create_app(loop=loop, debug=False)

    yield app

    collections = loop.run_until_complete(app['db'].collection_names())

    for name in collections:
        collection = app['db'][name]
        loop.run_until_complete(collection.drop())


@pytest.fixture()
def mongodb(loop):
    conn = motor_asyncio.AsyncIOMotorClient(ssl=False, io_loop=loop)
    db = motor_asyncio.AsyncIOMotorDatabase(conn, 'wiki_test')

    yield db
    await = loop.run_until_complete

    collections = await(db.collection_names())

    for name in collections:
        collection = db[name]
        await(collection.drop())


@pytest.fixture()
def active_user(webapp):
    from {{ cookiecutter.project_module }}.models.user import User
    await = webapp.loop.run_until_complete

    user = User(webapp['db'])
    user['email'] = 'user1@mail.com'
    user['roles'] = ['admin']
    user.set_password('password')

    await(user.commit())

    yield user

    await(user.delete())


@pytest.fixture()
def logged_user(webapp, active_user, test_client):
    await = webapp.loop.run_until_complete

    client = await(test_client(webapp))

    await(client.get('/auth/login/'))

    await(client.post('/auth/login/', data={
        'email': active_user['email'],
        'password': 'password'
    }, allow_redirects=False))

    yield webapp, active_user, client
