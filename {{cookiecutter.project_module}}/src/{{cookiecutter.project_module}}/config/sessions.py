from datetime import datetime, timedelta

from aiohttp import web
from aiohttp_session import AbstractStorage, Session
from bson import ObjectId
from bson.errors import InvalidId


class MongoSessionStorage(AbstractStorage):
    def __init__(self, collection, *, cookie_name="sessionid",
                 domain=None, max_age=None, path='/',
                 secure=None, httponly=True):
        self.collection = collection
        super().__init__(cookie_name=cookie_name, domain=domain,
                         max_age=max_age, path=path, secure=secure,
                         httponly=httponly)

    async def load_session(self, request):
        cookie = self.load_cookie(request)

        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)
        else:
            try:
                key = ObjectId(str(cookie))
            except InvalidId:
                key = None

            if key:
                data = await self.collection.find_one(filter={'_id': key})
                if data:
                    return Session(key, data=data, new=False, max_age=self.max_age)

            return Session(None, data=None, new=True, max_age=self.max_age)

    async def save_session(self, request, response, session):
        key = session.identity
        data = self._get_session_data(session)

        if key is None:
            ret = await self.collection.insert_one(data)
            self.save_cookie(response, str(ret.inserted_id), max_age=session.max_age)
        else:
            if session.empty:
                self.save_cookie(response, '', max_age=session.max_age)
            else:
                self.save_cookie(response, key, max_age=session.max_age)
                await self.collection.update_one(
                    {'_id': ObjectId(key)},
                    {'$set': data}, upsert=True)

    async def clearsessions(self, days=7):
        limit = (datetime.now() - timedelta(days=days)).timestamp()
        await self.collection.delete_many({'created': {'$lte': limit}})


def setup(app: web.Application):
    from aiohttp_session import session_middleware

    session_storage = MongoSessionStorage(app['db']['users.sessions'], max_age=60 * 60 * 24 * 30)

    app.middlewares.append(session_middleware(session_storage))

    app['session_storage'] = session_storage
