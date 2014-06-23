__author__ = "Daniel Fath <daniel DOT fath 7 AT gmail DOT com>"
__version__ = "0.1"

from setuptools import setup

NAME = 'DOMMLite  parser and utilities'
VERSION = __version__
DESC = 'DOMM Parser for master thesis'
AUTHOR = 'Daniel Fath'
AUTHOR_EMAIL = 'daniel DOT fath 7 AT gmail DOT com'
LICENCE = 'MIT'
URL = 'https://github.com/danielfath/master'

setup(
    name = NAME,
    version = VERSION,
    description = DESC,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer = AUTHOR,
    maintainer_email = AUTHOR_EMAIL,
    license = LICENCE,
    url = URL,
    packages = ["domm"],
    keywords = "parser dommlite utils graphic",
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules'
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]

)
