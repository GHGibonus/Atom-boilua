#!/bin/usr/python3
#pylint: disable=C0103,W0401,R0903,C0321,W0201,W0231,C0111,C0330,C0326
#disabled warnings:
# C0103: Naming convention. Here, we use:
#   camelCase for variables, functions and methods.
#   CamelCase for class names.
#   SNAKE_CASE for constants
# W0401: Wildcard import, used once to import all regex paterns
# R0903: too few methods in class: Is in contradiction with the
#        relational-oriented OOP based design pattern used in this package
# C0321: several statements on a line are Ok as long as it is used
#        sparingly
# W0201, W0231: Defining attributes outside of the __init__ is sadly necessary
#        to implement a overloading-like behavior in constructors.
# C0111: Class docstrings are unecessary if the class type is simple and
#        its name is explicit
# C0330: Incompatible with recommended notation for generators

# Your code must pass pylint and MyPy successfully to be considered for
# upstream integration (ok, you can get away with three warnings)

"""Scraps the doc and creates the completerc file.

Takes as argument:
    1: The Afterbirth lua documentation path,
    2: The .luacompleterc file location, to write the scrapped doc into."""

import sys

import json

from scraper import AfterbirthApi
from serializer import constructCompleterc

def scrapAndSerialize(docPath: str, completercFile: str):
    api = AfterbirthApi(docPath)
    with open(completercFile, 'w') as f:
        json.dump(constructCompleterc(api), f)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        scrapAndSerialize(sys.argv[1], sys.argv[2])
    else:
        sys.exit(212)
