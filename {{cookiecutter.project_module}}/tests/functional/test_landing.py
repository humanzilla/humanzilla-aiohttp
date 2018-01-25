import pytest


async def test_landing(webapp, test_client):
    client = await test_client(webapp)

    response = await client.get('/')

    assert response.status == 200


async def test_assets(webapp, test_client):
    client = await test_client(webapp)

    response = await client.get('/static/')

    assert response.status == 403
