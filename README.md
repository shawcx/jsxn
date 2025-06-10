jsxn
====

jsxn is a Python library for JSON objects that use a strict schema. Designed for use with REST APIs that return lists of objects that all have the same attributes.

The jsxn object will pragmatically generate a Python class based on a JSON string, Python dictionary, keyword arguments, or an iterable collection of attribute names.


```python
from jsxn import jsxn

# this will create a jsxn class 'dynamic' that has 'schema' and 'key' as attributes
instance = jsxn.dynamic({'schema':100,'key':'value'})

# str representations of jsxn instances will be JSON
print(instance)
# {"schema": 100, "key": "value"}

# jsxn instances can be passed to dict
print(dict(instance))
# {'schema': 100, 'key': 'value'}

# future references of the class will use the generated class
another = jsxn.dynamic('{"schema":200,"key":"something"}')

# previously generated classes can be called without arguments
builder = jsxn.dynamic()
print(builder)
# {"schema": null, "key": null}

# attributes can be accessed directly
builder.schema = 300
# or by indices
builder['key'] = 'populate'
print(builder)
# {"schema": 300, "key": "populate"}

# jsxn instances are callable with JSON strings
builder('{"schema":500}')
# and keywords
builder(key='hello')
print(builder)
# {"schema": 500, "key": "hello"}

# jsxn objects use slots so only attributes defined at creation can be assigned
try:
    builder.not_defined = True
except AttributeError as e:
    print(e)
    # 'dynamic' object has no attribute 'not_defined'

# delete a jsxn class in order to reuse it
del jsxn.dynamic

# a jsxn class can be defined with a list of keys
instance = jsxn.dynamic(['attr1','attr2','attr3'])
# all the variables will be uninitialized
print(instance)
# {"attr1": null, "attr2": null, "attr3": null}

# jsxn classes can also be deleted by indices
del jsxn['dynamic']

# it is possible to create a jsxn class that accept nothing
empty = jsxn.empty()
print(empty)
# {}
# but it is not very useful...
```

Class can define the names of the fields via typing or slots.

```python
from jsxn import jsxn

@jsxn
class example1:
    first : str
    second : int
    third : dict

@jsxn
class example2:
    __slots__ = [
        'first',
        'second',
        'third',
        ]
```

jsxn supports binding classes to generated types. This allows the creation of helper functions to perform actions with the underlying data.

```python
from jsxn import jsxn

@jsxn
class domain:
    name : str
    def save(self):
        print('SAVE:', self)

d = jsxn.domain({'name':'www.example.com'})
d.save()

@jsxn('computer')
class MachineClass:
    cpu   : str
    cores : int
    ram   : int
    addr  : str
    def ping(self):
        print('PING:', self.addr)

c = jsxn.computer(cpu='x86_64',cores=8,ram=8192,addr='192.168.1.1')
c.ping()
```
