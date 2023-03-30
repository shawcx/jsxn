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

import json
import functools

__all__ = ['jsxn']


class _Jsxn:
    # required for the derived class to be also be slotted
    __slots__ = []

    def __init__(self, *args, **kwds):
        # call the instance with the passed arguments
        self(*args, **kwds)
        # support partial initialization by setting undefined fields to null
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
        elif not isinstance(args, list):
            raise TypeError('Invalid type') from None

    # Support access attributes via indices.
    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    # This is for passing jsnx instances to the dict constructor.
    def __iter__(self):
        for attr in self.__slots__:
            yield((attr, getattr(self, attr)))

    def __len__(self):
        return len(self.__slots__)

    # Use JSON for string representations of the jsnx instance.
    def __str__(self):
        return json.dumps(dict(self))


# The _Cache class is used to hold the generated classes. It is defined outside
# of _JsxnFactory in order to reduce the potential for any name collisions with
# the names used by consumers of the library.
class _Cache(dict):
    def generate(self, name, *args, **kwds):
        # return the class if it has already been generated
        if name in self:
            return self[name]

        # Creation of jsxn classes accepts a variety of types when specifying
        # the schema of the class. This block derives the slots based on
        # the arguments passed in.
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

        # Create the derived jsnx class.
        cls = type(name, (_Jsxn,), {'__slots__':slots})

        # Cache the jsnx class.
        self[name] = cls

        # Instantiate the class and return the instance.
        return cls(*args, **kwds)

# Instantiate the cache dictionary.
_cache = _Cache()


# _JsxnFactory manages the creation and access to jsnx classes. When a derived
# class is accessed it will return the cached jsnx class. If the jsnx class has
# not been defined it will return a curried _Cache.generate function with the
# attribute name bound as the first argument
class _JsxnFactory:
    def __getitem__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name):
        try:
            return _cache[name]
        except KeyError:
            return functools.partial(_cache.generate, name)

    def __delattr__(self, name):
        try:
            del _cache[name]
        except KeyError:
            raise AttributeError(name) from None

    def __delitem__(self, name):
        del _cache[name]


# This is the way to access the jsnx library.
jsxn = _JsxnFactory()
