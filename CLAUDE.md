# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

jsxn is a single-module Python library (`jsxn.py`, no dependencies) that generates slotted classes from a JSON schema-by-example, for REST APIs returning lists of same-shaped objects. Packaged with `setup.py` (`py_modules=['jsxn']`); the version lives there. `README.md` is the user-facing usage doc and is also the PyPI long description.

## Commands

- Install for development: `pip install -e .`
- Build: `python3 setup.py sdist bdist_wheel`
- Run tests (stdlib `unittest`, no dependencies): `python3 -m unittest -v`
- Run one test: `python3 -m unittest tests.test_jsxn.TestSubclass.test_inherited_fields`
- Tests clear the global `_cache` in `setUp`/`tearDown`; keep that in any new test class (subclass `JsxnTestCase`).
- `test_from_list` is marked `expectedFailure`: the README's list-schema example is currently broken.
- There is no linter. `validate.py` and `example.py` are ad-hoc smoke scripts.

## Architecture (jsxn.py)

Three cooperating pieces, all private except the `jsxn` singleton:

- **`_Jsxn`** — base class for every generated class. Instances are callable to update fields from a JSON string, dict, another `_Jsxn`, or kwargs (`__call__` returns `self`, and `__init__` delegates to it, then sets unset slots to `None`). Provides `__getitem__`/`__setitem__`, `__iter__` yielding `(name, value)` pairs (so `dict(obj)` works), and `__str__` as JSON. It declares `__slots__ = []` so subclasses stay slotted — unknown attributes raise `AttributeError`.
- **`_Cache(dict)`** — module-level `_cache` mapping class name → generated class. `_generate` derives slots from a JSON string, dict keys, an existing `__slots__`, `__annotations__`, or a list, then builds the class with `type(name, bases, {'__slots__': slots})`. When given a user class that isn't already a `_Jsxn`, the bases are `(user_cls, _Jsxn)` so user methods take precedence. User classes are first rebuilt with empty slots by `_slotted()` (otherwise instances would get a `__dict__`), and each class declares only its own fields; `_fields()` collects fields from all parent classes for iteration, `len()` and null-filling.
- **`_JsxnFactory`** — the exported `jsxn` object. `jsxn.Name` / `jsxn['Name']` returns the cached class if it exists, otherwise a `functools.partial(_cache._instantiate, name)` that generates *and* instantiates it on first call. That is why the first `jsxn.foo({...})` defines the schema and later calls construct instances. `del jsxn.Name` evicts from the cache. Used as a decorator (`@jsxn`, `@jsxn()`, `@jsxn('name')`), `__call__` registers the user class; if the name is already cached, it combines the existing class and the new one, keeping the original slots.

The cache is global, so class names are shared process-wide. Tests or scripts that redefine a name must `del jsxn.Name` first.
