from collections import MutableMapping
from datetime import datetime
from typing import Union

import pydash as _
import trafaret as t
from bson import ObjectId
from bson.json_util import dumps
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from pymongo.errors import DuplicateKeyError

from .types import SimpleDoc


class ModelMapping(MutableMapping):
    collection_name = None

    def __init__(self, **data):
        super().__init__()

        if not self.collection_name:
            self.collection_name = type(self).__name__.lower()

        self.doctype = getattr(self, 'doctype', SimpleDoc)

        if not hasattr(self, '_data'):
            self._data = {}

        assert type(self._data) == dict

        self._data = _.assign({}, self._data, data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._data == other._data
        return False

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __str__(self):
        return dumps(self._data)

    @property
    def pk(self):
        oid = self.get('_id', None)
        return ObjectId(oid) if oid else None

    @pk.setter
    def pk(self, value: Union[str, ObjectId]):
        if isinstance(value, str):
            value = ObjectId(value)

        self['_id'] = value

    def asdict(self):
        return self._data


class ValidationError(Exception):
    def __init__(self, errors: dict):
        self.errors = errors


class Model(ModelMapping):
    def __init__(self, db, **data):
        super().__init__(**data)

        assert isinstance(db, AsyncIOMotorDatabase), 'DB must be instance of AsyncIOMotorDatabase'
        assert hasattr(self, 'doctype'), 'Missing Doctype'
        assert isinstance(self.doctype, t.Trafaret), 'Invalid type for doctype'

        self.db = db

    def __repr__(self):
        return f'<{self.collection_name.title()} id={self["_id"]}>'

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.pk == other.pk

    @property
    def bucket(self):
        return AsyncIOMotorGridFSBucket(self.collection.database, collection=self.collection_name)

    @property
    def collection(self):
        return self.db[self.collection_name]

    async def validate(self, data: Union[dict, None] = None) -> (bool, dict):
        if data is None:
            data = self._data

        try:
            data = self.doctype.check(data)
        except t.DataError as error:
            return False, error.as_dict()
        else:
            return True, data

    async def commit(self, *, update_fields: Union[set, None] = None, raise_invalid=True):
        is_valid, data = await self.validate(self._data.copy())
        validated = _.pick(self._data, *update_fields) if update_fields else data

        if not is_valid:
            if raise_invalid:
                raise ValidationError(data)
            else:
                return False, validated

        if self.pk:
            if 'modified' in self.doctype.keys:
                validated['modified'] = datetime.now()

        try:
            if self.pk:
                data = {'$set': validated}
                await self.collection.update_one({'_id': self['_id']}, data)
            else:
                ret = await self.collection.insert_one(validated)
                validated['_id'] = ret.inserted_id
        except DuplicateKeyError:
            errors = {'_all': ['Uno o mas valores estan duplicados']}

            if raise_invalid:
                raise ValidationError(errors=errors)
            else:
                return False, errors

        self.update(validated)

        return True, validated

    async def update_one(self, query: dict):
        if '$set' in query:
            query['$set']['modified'] = datetime.now()
        else:
            query['$set'] = {'modified': datetime.now()}
        await self.collection.update_one({'_id': self['_id']}, query)

    async def find_all(self, query: dict = None, projection: dict = None, sort: dict = None, limit=100):
        if not query:
            query = {}

        cursor = self.collection.find(query, projection)
        cursor.limit(limit)
        if sort:
            cursor.sort(list(sort.items()))

        return [self.__class__(db=self.db, **document) async for document in cursor]

    async def find_by_id(self, doc_id: Union[str, ObjectId]):
        if not isinstance(doc_id, ObjectId):
            doc_id = ObjectId(doc_id)
        return await self.find_one({'_id': doc_id})

    async def find_one(self, query: dict):
        data = await self.collection.find_one(query)

        if '_id' in query:
            if not isinstance(query['_id'], ObjectId):
                query['_id'] = ObjectId(query['_id'])

        if data is not None:
            return self.__class__(db=self.db, **data)

    async def insert_one(self, data: dict):
        is_valid, cleaned_data = await self.validate(data)

        if is_valid:
            await self.collection.insert_one(cleaned_data)
            return True, self.__class__(db=self.db, **cleaned_data)

        return False, cleaned_data

    async def delete(self):
        return await self.collection.delete_one(
            {'_id': self.pk})

    async def trash(self):
        return await self.collection.update(
            {'_id': self.pk},
            {'$set': {'deleted': datetime.now()}})

    async def recover(self):
        return await self.collection.update(
            {'_id': self.pk},
            {'$unset': {'deleted': 1}})
