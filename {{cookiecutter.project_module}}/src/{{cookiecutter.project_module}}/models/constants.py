import trafaret as t

__all__ = ['Optional', 'SimpleType', 'PageType']

Optional = partial(t.Key, optional=True)
Required = partial(t.Key, optional=False)

SimpleType = t.IntRaw | t.Bool | t.String | t.FloatRaw
