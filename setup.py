#!/usr/bin/env python
import os
import sys

from qgenda import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as requirement_file:
    requirements = [line.strip() for line in requirement_file.readlines() if not line.strip().startswith('#')]

setup(
    name='python-qgenda',
    version=__version__,
    description='Python client for QGenda REST API',
    long_description=long_description,
    url='https://github.com/jjorissen52/python-qgenda',
    author='JP Jorissen',
    author_email='jjorissen52@gmail.com',
    maintainer='JP Jorissen',
    maintainer_email='jjorissen52@gmail.com',
    keywords=['QGenda', 'python api', 'python client'],
    license='Apache',
    packages=[
        'qgenda',
        'qgenda.api',
        'qgenda.cache',
        'qgenda.pipeline',
        'qgenda.tests'
    ],
    install_requires=requirements,
    extras_require={
        'redis': [
            "redis==2.10.6",
        ],
        'memcache': [
            "python-memcached==1.59"
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ]
)