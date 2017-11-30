from aiohttp import request
import pytest

from tests.conftest import create_server, async_test


class TestCoreHandler(object):

    @pytest.mark.handlers
    @async_test
    async def test_index(self, application):
        srv, url = await create_server(application)
        resp = await request('GET', url, loop=application.loop)
        assert resp.status == 200
        result = await resp.text()
        assert '{{cookiecutter.project_module}}' in result
