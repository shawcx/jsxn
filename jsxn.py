#
# The MIT License (MIT)
#
# Copyright (c) 2023 Matthew Shaw
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import functools
import inspect
import json

__all__ = ['jsxn']


class _Jsxn:
    # required for the derived class to be also be slotted
    __slots__ = []

    def __init__(self, *args, **kwds):
        # Call the instance with the passed arguments.
        self(*args, **kwds)
        # Support partial initialization by setting undefined fields to null.
        for attr in self.__slots__:
            if not hasattr(self, attr):
                setattr(self, attr, None)

    def __call__(self, *args, **kwds):
        # Calling jsxn instances accepts a variety of types. This block assigns
        # values to the attributes based on the type of arguments passed in.
        if not args:
            args = kwds
        else:
            args = args[0]
        if isinstance(args, str):
            args = json.loads(args)
        if isinstance(args, dict):
            for key,value in args.items():
                setattr(self, key, value)
        elif isinstance(args, _Jsxn):
            for key,value in args:
                setattr(self, key, value)
        elif not isinstance(args, list):
            raise TypeError('Invalid type') from None

    # Support access attributes via indices.
    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    # This is for passing jsxn instances to the dict constructor.
    def __iter__(self):
        for attr in self.__slots__:
            yield((attr, getattr(self, attr)))

    def __len__(self):
        return len(self.__slots__)

    # Use JSON for string representations of the jsxn instance.
    def __str__(self):
        return json.dumps(dict(self))


# The _Cache class is used to hold the generated classes. It is defined outside
# of _JsxnFactory in order to reduce the potential for any name collisions with
# the names used by consumers of the library.
class _Cache(dict):
    def generate(self, _name_for_jsxn_class, *args, **kwds):
        # Creation of jsxn classes accepts a variety of types when specifying
        # the schema of the class. This block derives the slots based on
        # the arguments passed in.
        inherit = [_Jsxn,]
        if _name_for_jsxn_class in self:
            inherit.append(self[_name_for_jsxn_class])

        if not args:
            slots = kwds
        else:
            slots = args[0]
        if isinstance(slots, str):
            slots = json.loads(slots)
        if isinstance(slots, dict):
            slots = tuple(slots.keys())
        elif isinstance(slots, _Jsxn):
            slots = slots.__slots__
        elif not isinstance(slots, list):
            raise TypeError('Invalid type') from None

        # Create the derived jsxn class.
        cls = type(_name_for_jsxn_class, tuple(inherit), {'__slots__':slots})

        # Cache the jsxn class.
        self[_name_for_jsxn_class] = cls

        # Instantiate the class and return the instance.
        return cls(*args, **kwds)

# Instantiate the cache dictionary.
_cache = _Cache()


# _JsxnFactory manages the creation and access to jsxn classes. When a derived
# class is accessed it will return the cached jsxn class. If the jsxn class has
# not been defined it will return a curried _Cache.generate function with the
# attribute name bound as the first argument
class _JsxnFactory:
    # Let the instance be a decorator function.
    def __call__(self, arg=None):
        # Helpher function to inject a class into an existing jsnx class.
        def inject(name, cls):
            if name in _cache:
                og = _cache[name]
                cls = type(name, (og,cls), {'__slots__':og.__slots__})
            _cache[name] = cls
            return cls

        # If a string is passed in use that as the name.
        if isinstance(arg, str):
            def wrap(cls):
                return inject(arg, cls)
            return wrap
        # Use the class name if no argument is supplied
        elif arg is None:
            def wrap(cls):
                return inject(cls.__name__, cls)
            return wrap
        elif inspect.isclass(arg):
            return inject(arg.__name__, arg)

        raise TypeError(arg)

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, name):
        try:
            cls = _cache[name]
            if not issubclass(cls, _Jsxn):
                raise KeyError(name)
            return cls
        except KeyError:
            return functools.partial(_cache.generate, name)

    def __delattr__(self, name):
        try:
            del _cache[name]
        except KeyError:
            raise AttributeError(name) from None

    def __delitem__(self, name):
        del _cache[name]

# This is the way to access the jsxn library.
jsxn = _JsxnFactory()
