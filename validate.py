#!/usr/bin/env python3

from jsxn import jsxn

@jsxn
class Sleep:
    one : str
    two : int

    def hello(self):
        print(self.one, self.two)

@jsxn('radios')
class Radios:
    __slots__ = [
        'radio',
        'rig',
        'input',
        'output',
        ]

    def save(self):
        print('save:', self)


r = jsxn.radios(radio = 1, rig = 'a')
r.save()

r = jsxn.radios({'radio':2,'rig':'b'})
r.save()


z = jsxn.Sleep(one='b', two='c')
print(z)
z.two = 100
print(dict(z))
z.hello()
