#!/bin/usr/python3
#pylint: disable=C0103,W0401,R0903,C0321,W0201,W0231,C0111,C0330,C0326
#mypy: disable=all
"""This module implements the serialization behavior for the completerc file.
"""

import sys

from scraper import (
    AfterbirthApi, LuaClass, LuaAttribute, LuaType,
    LuaFunction, LuaEnumerator, LuaNamespace )

# If you want to customize your autocompletion suggestions, modify the
# following three variables.
# This package uses the autocomplete-lua completion provider, use
# that format to write your custom variables.
CUSTOM_GLOBALS = {
    'RegisterMod': {
        'type': 'function',
        'description': 'Register your mod using this function.',
        'args': [{'name': 'mod name'},{'name': 'mod version'}],
        'returnTypes': [{'type': 'ref', 'name': 'Isaac'}]
    }
}

CUSTOM_TYPES = {
}

CUSTOM_FUNCTIONS = {
    'GetRoomEntities': {
        'returnTypes': [{'type': 'unknown'}]
    }
}


def serializedType(luaType: LuaType):
    if luaType.name in ('boolean', 'string', 'nil'):
        return {'type': luaType.name}
    elif luaType.name in ('int', 'float', 'integer'):
        return {'type': 'number'}
    elif luaType.name == 'table':
        return {'type': 'unknown'}
    else:
        return {'type': 'ref', 'name': luaType.name}

def serializedAttrib(var: LuaAttribute):
    ret = serializedType(var.luaType)
    ret.update({'description': var.description})
    return ret

def serializedFunction(fun: LuaFunction, isMethod: bool= False):
    ret = {
        'type': 'function',
        'description': fun.description,
        'returnTypes': [serializedType(fun.returnType)],
        'args': [],
        'argTypes': []
    }
    if isMethod:
        ret['args'].append({'name': 'self'})
        ret['argTypes'].append({'type': 'unknown'})

    for arg in fun.parameters:
        ret['args'].append({'name': arg.name})
        ret['argTypes'].append(serializedType(arg.luaType))

    if fun.name in CUSTOM_FUNCTIONS.keys():
        for key in CUSTOM_FUNCTIONS[fun.name]:
            ret[key] = CUSTOM_FUNCTIONS[fun.name][key]
    return ret

def serializedClass(c: LuaClass):
    ret = {
        'type': 'table',
        'fields': {},
        'description': c.description
    }
    for attrib in c.attributes:
        ret['fields'][attrib.name] = serializedAttrib(attrib)
    for method in c.methods:
        if method.name != c.name:
            ret['fields'][method.name] = serializedFunction(method, True)
    return ret

def serializedEnumeration(e: LuaEnumerator):
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

def serializedNamespace(ns: LuaNamespace):
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
        if c.constructor is not None:
            globalScope['global']['fields'][c.name] =\
                serializedFunction(c.constructor)
    for e in api.enumerators:
        globalScope['namedTypes'][e.name] = serializedEnumeration(e)
        globalScope['global']['fields'][e.name] = serializedEnumeration(e)
    for ns in api.namespaces:
        if ns.name == '_G':
            for f in ns.functions:
                globalScope['global']['fields'][f.name] = serializedFunction(f)
        else:
            globalScope['namedTypes'][ns.name] = serializedNamespace(ns)
            globalScope['global']['fields'][ns.name] = serializedNamespace(ns)
    for gKey in CUSTOM_GLOBALS:
        globalScope['global']['fields'][gKey] = CUSTOM_GLOBALS[gKey]
    for vKey in CUSTOM_TYPES:
        globalScope['namedTypes'][vKey] = CUSTOM_TYPES[vKey]
    return globalScope


if __name__ == '__main__':
    print(' '.join(sys.argv[1:]))
    abapi = AfterbirthApi(' '.join(sys.argv[1:]))
    seriabapi = constructCompleterc(abapi)
    print(seriabapi)
