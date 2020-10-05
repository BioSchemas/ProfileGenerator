#!/usr/bin/env python

# Copyright 2020 Heriot-Watt University, UK
# Copyright 2020 The University of Manchester, UK
#

__author__ = "Bioschemas.org community"
__copyright__ = """© 2020 Heriot-Watt University, UK
© 2020 The University of Manchester, UK
"""
__license__ = "MIT" # https://spdx.org/licenses/MIT

from setuptools import setup, find_packages
from codecs import open
from os import path
import re

# https://www.python.org/dev/peps/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions  # noqa
PEP440_PATTERN = r"([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?"  # noqa


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    required = f.read().splitlines()

with open(path.join(here, 'profilegenerator', '_version.py'), encoding='utf-8') as f:
    # "parse" rocrate/_version.py which MUST have this pattern
    # __version__ = "0.1.1"
    # see https://www.python.org/dev/peps/pep-0440
    v = f.read().strip()
    m = re.match(r'^__version__ = "(' + PEP440_PATTERN + ')"$', v)
    if not m:
        msg = ('rocrate/_version.py did not match pattern '
               '__version__ = "0.1.2"  (see PEP440):\n') + v
        raise Exception(msg)
    __version__ = m.group(1)


setup(
    name='profilegenerator',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    version=__version__,  # update in rocrate/_version.py
    description='BioSchemas Profile Generator',
    long_description_content_type='text/markdown',
    long_description=long_description,
    author=('Alasdair J G Gray, Stian Soiland-Reyes'),
    python_requires='>=3.6',
    author_email='public-bioschemas@w3.org',
    package_data={'': ['data/*.jsonld', 'templates/*.j2']},
    license="MIT",
    url='https://github.com/bioschemas/ProfileGenerator/',
    download_url=('https://github.com/bioschemas/ProfileGenerator/archive/'
                  f'{__version__}.tar.gz'),
    keywords="bioschemas schema.org jekyll profile",
    install_requires=[required],
    test_suite='test',
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Database',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities',
    ],
)
