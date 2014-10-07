import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pymutester",
    version = "0.1.0",
    author = "Michael Teo",
    author_email = "miketeo@miketeo.net",
    description = ("Python Mutant Tester (PyMuTester) facilitates mutant testing for python applications"),
    license = "Apache License version 2.0",
    keywords = "mutant unit testing",
    url = "http://miketeo.net/wp/index.php/projects/python-mutant-testing-pymutester",
    packages=['mutester', 'mutester.mutators'],
    scripts=['mutant-nosetests'],
    long_description=read('README'),
    install_requires=[ 'nose>=0.11.4' ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: Apache Software License",
    ],
)
