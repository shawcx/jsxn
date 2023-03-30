#!/usr/bin/env python3

import sys
import os

from setuptools import setup

setup(
    name             = 'jsxn',
    version          = '0.1',
    author           = 'Matthew Shaw',
    author_email     = 'mshaw.cx@gmail.com',
    license          = 'MIT',
    description      = 'Python Metaclass JSON library',
    long_description = open('README.md').read(),
    url              = 'https://github.com/shawcx/jsnx',
    py_modules = ['jsxn'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ],
    zip_safe = True
    )
