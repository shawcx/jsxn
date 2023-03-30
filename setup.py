#!/usr/bin/env python3

import sys
import os

from setuptools import setup

setup(
    name             = 'jsxn',
    version          = '0.2',
    author           = 'Matthew Shaw',
    author_email     = 'mshaw.cx@gmail.com',
    license          = 'MIT',
    description      = 'Python Metaclass JSON library',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    url              = 'https://github.com/shawcx/jsxn',
    py_modules = ['jsxn'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ],
    zip_safe = True
    )
