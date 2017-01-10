#!/bin/usr/python3
#pylint: disable=C0103,W0401,R0903,C0321,W0201,W0231,C0111,C0330,C0326
"""This module implements the serialization behavior for the completerc file.
"""

import sys

from scraper import (
    AfterbirthApi, LuaClass, LuaAttribute, LuaType,
    LuaFunction, LuaEnumerator, LuaNamespace )

def serializedType(luaType: LuaType) -> dict:
    if luaType.name in ('boolean', 'integer', 'float', 'string'):
        return {'type': luaType.name}
    else:
        return {'type': 'ref', 'name': luaType.name}

def serializedAttrib(var: LuaAttribute) -> dict:
    ret = serializedType(var.luaType)
    ret.update({'description': var.description})
    return ret

def serializedFunction(fun : LuaFunction) -> dict:
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

def serializedClass(c: LuaClass) -> dict:
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

def serializedEnumeration(e: LuaEnumerator) -> dict:
    ret = {
        'type': 'table',
        'fields': {},
    }
    for m in e.members:
        ret['fields'][m.name] = {
            'type': 'integer',
            'description': m.description
        }
    return ret

def serializedNamespace(ns: LuaNamespace) -> dict:
    ret = {
        'type': 'table',
        'fields': {},
    }
    for f in ns.functions:
        ret['fields'][f.name] = serializedFunction(f)
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
    for e in api.enumerators:
        globalScope['namedTypes'][e.name] = serializedEnumeration(e)
        globalScope['global']['fields'][e.name] = serializedEnumeration(e)
    for ns in api.namespaces:
        globalScope['namedTypes'][ns.name] = serializedNamespace(ns)
        globalScope['global']['fields'][ns.name] = serializedNamespace(ns)
    globalScope['global']['fields']['Game'] = {
        'type': 'function',
        'returnTypes': [{'type': 'ref', 'name': 'Game'}]
    }
    return globalScope


if __name__ == '__main__':
    print(' '.join(sys.argv[1:]))
    abapi = AfterbirthApi(' '.join(sys.argv[1:]))
    seriabapi = constructCompleterc(abapi)
    print(seriabapi)
