from datetime import datetime
from functools import partial

from . import base
from . import types as ct


class User(base.Model):
    collection = 'users'

    doctype = ct.TimestampDoc + t.Dict({
        'email': t.Email,
        'password': t.String,
        t.Key('roles', default=[]): t.List(t.Enum('admin', 'user')),
        t.Key('first_name', default=''): t.String(allow_blank=True),
        t.Key('last_name', default=''): t.String(allow_blank=True),
        t.Key('joined', default=datetime.datetime.now): ct.DateTimeType,
        t.Key('last_login', optional=True): ct.DateTimeType,
    })

    _data = {
        'email': '',
        'roles': [],
        'first_name': '',
        'last_name': '',
        'password': ''
    }

    is_authenticated = None

    async def find_by_email(self, email: str):
        return await self.find_one({'email': email})

    def set_password(self, value: str):
        iterations = 100000
        salt = secrets.token_bytes(60)
        hash = hashlib.pbkdf2_hmac('sha256', value.encode(), salt, iterations)
        encoded_hash = binascii.hexlify(hash).decode()
        encoded_salt = binascii.hexlify(salt).decode()
        self['password'] = f'{encoded_salt}${encoded_hash}${iterations}'

    def check_password(self, value: str):
        try:
            encoded_salt, encoded_hash, iterations = self['password'].split('$', 3)
        except (KeyError, ValueError):
            return False

        salt = binascii.unhexlify(encoded_salt)
        hash = hashlib.pbkdf2_hmac('sha256', value.encode(), salt, int(iterations))
        return binascii.unhexlify(encoded_hash) == hash

    def asdict(self):
        return {
            'id': self.pk,
            'first_name': self.get('first_name', ''),
            'last_name': self.get('last_name', ''),
            'email': self['email'],
            'roles': self['roles'],
        }

    async def setup(self):
        await self.collection.create_index([('email', 1)], unique=True)


class AnonymousUser(models.ModelMapping):
    pk = None
    _id = None
    is_authenticated = False

    _data = {
        'roles': [],
        'first_name': '',
        'last_name': '',
        'email': '',
    }

    def __str__(self):
        return 'AnonymousUser'

    def __eq__(self, other):
        return isinstance(other, AnonymousUser)

    def __hash__(self):
        return 1

    def asdict(self):
        return {'id': None}
