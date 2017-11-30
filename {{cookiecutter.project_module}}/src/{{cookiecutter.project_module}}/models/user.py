from . import base

from datetime import datetime
from functools import partial


class User(base.Model):
    collection = 'users'
