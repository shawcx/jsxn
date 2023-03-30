
import json
import functools

__all__ = ['jsxn']


class _Jsxn:
    __slots__ = []

    def __init__(self, *args, **kwds):
        self(*args, **kwds)
        for attr in self.__slots__:
            if not hasattr(self, attr):
                setattr(self, attr, None)

    def __call__(self, *args, **kwds):
        if not args:
            args = kwds
        else:
            args = args[0]

        if isinstance(args, str):
            args = json.loads(args)
        if isinstance(args, dict):
            for key,value in args.items():
                setattr(self, key, value)
        elif not isinstance(args, list):
            raise TypeError('Invalid type') from None

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def __iter__(self):
        for attr in self.__slots__:
            yield((attr, getattr(self, attr)))

    def __len__(self):
        return len(self.__slots__)

    def __str__(self):
        return json.dumps(dict(self))


class _Cache(dict):
    def create(self, name, *args, **kwds):
        if name in self:
            return self[name]

        if not args:
            slots = kwds
        else:
            slots = args[0]

        if isinstance(slots, str):
            slots = json.loads(slots)
        if isinstance(slots, dict):
            slots = tuple(slots.keys())
        elif not isinstance(slots, list):
            raise TypeError('Invalid type') from None

        cls = type(name, (_Jsxn,), {'__slots__':slots})
        self[name] = cls
        return cls(*args, **kwds)

_cache = _Cache()


class _JsxnFactory:
    def __getitem__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name):
        try:
            return _cache[name]
        except KeyError:
            return functools.partial(_cache.create, name)

    def __delattr__(self, name):
        try:
            del _cache[name]
        except KeyError:
            raise AttributeError(name) from None

    def __delitem__(self, name):
        del _cache[name]


jsxn = _JsxnFactory()
