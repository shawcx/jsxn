#!/usr/bin/env python3

import json

from jsxn import jsxn


# A typical REST API response: a list of objects sharing the same attributes.
response = '''[
    {"id": 1, "name": "alpha", "status": "up",   "addr": "10.0.0.1"},
    {"id": 2, "name": "bravo", "status": "down", "addr": "10.0.0.2"},
    {"id": 3, "name": "charlie", "status": "up", "addr": "10.0.0.3"}
]'''


# Bind helper methods to the generated class. Fields come from annotations.
@jsxn('host')
class Host:
    id     : int
    name   : str
    status : str
    addr   : str

    def is_up(self):
        return self.status == 'up'


hosts = [jsxn.host(item) for item in json.loads(response)]

for h in hosts:
    print(h.name, 'UP' if h.is_up() else 'DOWN', h.addr)

# Update an instance with keywords or JSON; calls return self so they chain.
hosts[1](status='up')('{"addr": "10.0.0.20"}')
print(hosts[1])

# Unknown fields are rejected because generated classes use slots.
try:
    hosts[0].owner = 'matt'
except AttributeError as e:
    print('rejected:', e)

# Instances convert cleanly back to dicts for re-serialising.
print(json.dumps([dict(h) for h in hosts if h.is_up()], indent=2))
