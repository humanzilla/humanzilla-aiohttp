import pydash as _
import trafaret as t
import datetime
from functools import partial

from jinja2.utils import import_string
from trafaret.contrib.object_id import MongoId
from trafaret.contrib.rfc_3339 import DateTime


Optional = partial(t.Key, optional=True)
SimpleType = t.IntRaw | t.Bool | t.String | t.FloatRaw

DateTimeType = DateTime | t.Type(datetime.datetime)
NumericType = t.Float | t.Int >> (lambda val: float(val))
URLType = t.Regexp(r'^([a-z]{2,5}:)?(\/\/?)?[a-z][a-z0-9\.\-\/]+$')

OptionValue = t.String(allow_blank=True) | t.Bool | t.Float | t.Int | t.Type(dict)
Optional = partial(t.Key, optional=True)

SimpleDoc = t.Dict({
    t.Key('id', optional=True) >> '_id': MongoId,
    Optional('_id'): MongoId
})

TimestampDoc = SimpleDoc + t.Dict({
    Optional('created', default=datetime.datetime.now): DateTimeType | t.Null,
    Optional('modified'): DateTimeType
})

BucketFile = t.Dict({
    'attach_id': MongoId,
    'filename': t.String(allow_blank=''),
    'content_type': t.String(allow_blank='')
})