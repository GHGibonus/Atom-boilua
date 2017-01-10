#!/bin/usr/python3
#pylint: disable=C0103,W0401,R0903,C0321,W0201,W0231,C0111,C0330,C0326
"""This module implements the serialization behavior for the completerc file.

"""

#TO EXTRACT:
# types,
# enumerators and their
#oop to lua translation:
#  class -> table with specific type
#  class method -> table field of type function
#  class attribute -> table field of arbitrary type

# first we need to find all 'root' named types, which are:
# Enumerators
# Namespaces
# class names
import sys

from typing import Dict, List, Union

from scraper import (
    AfterbirthApi, LuaClass, LuaAttribute, LuaType,
    LuaFunction )


def serializedType(luaType: LuaType) -> Dict:
    if luaType.name in ('boolean', 'integer', 'float', 'string'):
        return {'type': luaType.name}
    else:
        return {'type': 'ref', 'name': luaType.name}

def serializedAttrib(var: LuaAttribute) -> Dict:
    ret = serializedType(var.luaType)
    ret.update({'description': var.description})
    return ret

def serializedFunction(fun : LuaFunction) -> Dict:
    ret = {
        'type': 'function',
        'description': fun.description,
        'returnTypes': [serializedType(fun.returnType)],
        'args': [],
        'argTypes': []
    }
    for arg in fun.parameters:
        ret['args'].append({'name': arg.name})
        ret['argTypes'].append(serializedType(arg.luaType))
    return ret

def serializedClass(c: LuaClass) -> Dict:
    ret = {
        'type': 'table',
        'fields': {},
        'description': c.description
    }
    for attrib in c.attributes:
        ret['fields'][attrib.name] = serializedAttrib(attrib)
    for method in c.methods:
        ret['fields'][method.name] = serializedFunction(method)
    return ret


def constructCompleterc(api: AfterbirthApi):
    globalScope = {
        'global': {
            'type':'table',
            'fields':{}
        },
        'namedTypes':{}
    }
    for c in api.classes:
        globalScope['namedTypes'][c.name] = serializedClass(c)
        globalScope['global']['fields'][c.name] = serializedClass(c)
    return globalScope


if __name__ == '__main__':
    print(' '.join(sys.argv[1:]))
    abapi = AfterbirthApi(' '.join(sys.argv[1:]))
    seriabapi = constructCompleterc(abapi)
    print(seriabapi)
