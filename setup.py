# -*- coding: utf-8 -*-
"""Setup file for env_utils."""
import os
from os.path import join, normpath, abspath, dirname
from setuptools import setup, find_packages

README = open(join(dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

setup(
    name="hipchat-notifications",
    version="0.4.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests>=2.1'],
    license='MIT',
    description="Basic functions for sending notifications via HipChat API (v2)",
    long_description=README,
    url='https://github.com/yunojuno/hipchat-notifications',
    author="YunoJuno",
    author_email='code@yunojuno.com',
    maintainer="YunoJuno",
    maintainer_email='code@yunojuno.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)
