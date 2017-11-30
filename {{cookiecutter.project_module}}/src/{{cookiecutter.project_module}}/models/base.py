from collections import MutableMapping
from datetime import datetime

from bson import ObjectId
from bson.json_util import dumps


class Model(MutableMapping):
    _collection = None

    def __init__(self, request, **data):
        super().__init__()
        self._data = data

    def __eq__(self, other):
        return self is other

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f'<Document id={self["_id"]}>'

    def __str__(self):
        return self["title"]

    @property
    def collection(self):
        if not self._collection:
            self._collection = self.app['db'][self.collection]
        return self._collection

    def serialize(self):
        return dumps(self._data)

    async def commit(self, **kwargs):
        data = self._data.copy()
        data['modified'] = datetime.now()
        data.update(kwargs)
        await self.collection.update_one({'_id': self['_id']}, {'$set': data})
        self.update(data)

    async def delete(self):
        await self.collection.pages.update({'_id': self['_id']}, {'$set': {'deleted': datetime.now()}})

    @classmethod
    async def find_all(cls, collection, query: dict = None, limit=10):
        if not query:
            query = {}

        cursor = collection.find(query).sort('created', -1).limit(limit)
        return [cls(collection, **document) async for document in cursor]

    @classmethod
    async def find_by_id(cls, collection, doc_id):
        data = await collection.find_one({'_id': ObjectId(doc_id)})
        doc = cls(collection)
        doc.update(**data)
        return doc

    @classmethod
    async def insert_one(cls, collection, **kwargs):
        data = kwargs
        data['created'] = datetime.now()
        await collection.insert_one(data)
        doc = cls(collection)
        doc.update(data)
        return doc
