#!/bin/usr/python3
#pylint: disable=C0301,C0103
"""Scraps data from the isaac API doc and copies it in the target file.

    The module must be called directly, the arguments are as following:
    1. the doc directory
    2. the luacompleterc output file."""

import re
import os
import os.path as pth
import sys
import json
from typing import Iterator, Tuple, List, NewType, TypeVar, Generic, Match
from enum import Enum

#Regular expression patterns defined by Kapiainen
RE_CLASS_NAME = re.compile(r"<div class=\"title\">(.+?) class reference</div>", re.IGNORECASE)
RE_NAMESPACE_NAME = re.compile(r"<div class=\"title\">(.+?) namespace reference</div>", re.IGNORECASE)
RE_INHERITS_FROM = re.compile(r"inherited from <a.+?>(.+?)</a>", re.IGNORECASE)
RE_FUNCTION_SIGNATURE = re.compile(r"(?:<td class=\"memitemleft\".+?>(?P<returns>.+?))?&#.+?;</td><td class=\"memitemright\".+?><a.+?>(?P<name>.+?)</a>\s+\((?P<parameters>.+?)?\)", re.IGNORECASE)
RE_FUNCTION_RETURNS = re.compile(r"(?:(?:(?P<const>const)\s*)?(?:(?P<static>static)\s*)?)*(?:(?P<type>[_a-z][_a-z0-9]*(?:::[_a-z][_a-z0-9]*)*))(?:\s+&amp;)?", re.IGNORECASE)
RE_FUNCTION_PARAMETER = re.compile(r"(?P<type>([_a-z][_a-z0-9]*(?:::[_a-z][_a-z0-9]*)*))(?:\s+(?P<name>[_a-z][_a-z0-9]*))?", re.IGNORECASE)
RE_ATTRIBUTE = re.compile(r"<td class=\"memitemleft\".+?>(?P<type>.+?)&#.+?;</td><td class=\"memitemright\".+?><a.+?>(?P<name>.+?)</a>", re.IGNORECASE)
RE_ATTRIBUTE_TYPE = re.compile(r"(?:(?:(?P<const>const)\s*)?(?:(?P<static>static)\s*)?)*(?:(?P<type>[_a-z][_a-z0-9]*(?:::[_a-z][_a-z0-9]*)*))(?:\s+&amp;)?", re.IGNORECASE)
RE_ENUM_NAME = re.compile(r"<h2 class=\"memtitle\"><span class=\"permalink\">.+?</span>(.+?)</h2>", re.IGNORECASE)
RE_ENUM_MEMBER = re.compile(r"<td class=\"fieldname\"><a.+?</a>(?P<name>.+?)&#.+?<td class=\"fielddoc\">(?:<p>(?P<desc>.+?)</p>)?", re.IGNORECASE)
RE_DESCRIPTION = re.compile(r"<td class=\"mdescright\">(.+?)<a.+?</td>", re.IGNORECASE)
RE_HTML_REPLACER = re.compile(r"<.*?>")

class IdentKey(Enum):
    CONST = "Const"
    STATIC = "Static"
    ATTRIBUTES = "Attributes"
    CLASSES = "Classes"
    DESCRIPTION = "Description"
    ENUMS = "Enums"
    FUNCTIONS = "Functions"
    MEMBERS = "Members"
    NAME = "Name"
    NAMESPACES = "Namespaces"
    PARAMETERS = "Parameters"
    RETURNS = "Returns"
    TYPE = "Type"
    INHERITS_FROM = "Inherits from"

class InvalidMatcherError(Exception):
    """Rose when trying to create an object from an invalid matcher."""
    def __init__(self, msg: str = 'Couldn\'t construct Class from matcher'):
        super().__init__()
        self.message =  msg

KapiainenMatchReturnType = TypeVar[str, Tuple[str]]


class LuaType:
    """A simple lua class description."""
    #name: str
    #isConst: bool
    #isStatic: bool
    def __init__(self,
        *args: TypeVar[Match, Tuple[str, bool, bool]],
        **kwargs: Dict):
        """Initializes LuaType.

        Supports two constructor methods:
        1: LuaType(name: str, isConst: bool= False, isStatic: bool= False)
        builds the instance with the given arguments

        2: LuaType(reMatcher: Match)
        builds the instance using the matching object."""
        if isinstance(args[0], Match):
            self.__initRegex(*args)
        elif 'reMatcher' in kwargs.keys():
            self.__initRegex(kwargs['reMatcher'])
        else:
            self.__initFlat()

    def __initFlat(self,
            name: str, isConst: bool= False, isStatic: bool= False):
        self.name = name if name != '' else 'nil'
        self.isConst = isConst
        self.isStatic = isStatic

    def __initRegex(self, typeMatcher: Match):
        self.__initFlat(
            typeMatcher.group('type'),
            typeMatcher.group('const') is not None,
            typeMatcher.group('static') is not None)


class LuaVariable:
    """A lua variable, inherited by classes describing attributes and other."""
    #name: str
    #luaType: LuaType
    def __init__(self, name: str, luaType: LuaType):
        self.name = name
        self.luaType = LuaType(luaType)

class LuaParam(LuaVariable):
    """A parameter of a Lua function."""
    def __init__(self, name: str, luaType: LuaType):
        super().__init__(name, luaType)

class LuaAttribute(LuaVariable):
    """An attribute of a Lua class."""
    def __init__(self, name: str, luaType: LuaType, comment: str=''):
        super().__init__(name, luaType)
        self.comment = comment


class LuaFunction:
    """A structure to hold information about lua functions."""
    #name: str
    #comment: str
    #parameters: List[LuaParam]
    #returnType: LuaType
    def __init__(self, functionRematcher: Match):
        if functionRematcher is None:
            raise InvalidFunctionMatcher()
        self.name = functionRematcher.group('name')
        self._findParameters(functionRematcher.group('parameters'))
        self._findReturnval(functionRematcher.group('returns'))
        self.comment = ''

    def _findParameters(self, paramMatchedVals: KapiainenMatchReturnType):
        """Finds the parameters and adds them to instance.

        The type for paramMatchedVals is what I could interpolate from the
        Python doc."""
        self.parameters = []
        if not paramMatchedVals: #NOTE:not sure what this is checking for
            return
        paramScraper = RE_HTML_REPLACER.sub('', paramMatchedVals).split(', ')
        for param in paramScraper:
            paramMatcher = RE_FUNCTION_PARAMETER.search(param)
            paramName = paramMatcher.group('name')
            paramType = paramMatcher.group('type')
            self.parameters += [LuaParam(paramName, LuaType(paramType))]

    def _findReturnval(self, retMatchval: KapiainenMatchReturnType):
        """Finds the return value found from that retMatchval thingy."""
        if not retMatchval: #NOTE: not sure what this is for
            self.returnType = LuaType('')
            return
        returnMatcher = RE_FUNCTION_RETURNS.search(
            RE_HTML_REPLACER.sub('', retMatchval))
        self.returnType = LuaType(returnMatcher)


class LuaClass:
    """Describes a lua class."""
    #methods: [LuaFunction]
    #attributes: [LuaAttribute]
    def __init__(self, *args, **kwargs):
        pass

    def _findAttributes(self, ...):
        pass

    def _findFunctions(self, ...):
        pass

def allDocFiles(docPath: str) -> Iterator[Tuple[str, str]]:
    """List all files in the docPath.

    Returns their file name and associated directory paths"""
    for __, dirName, dirFileList in os.walk(docPath):
        for fileName in dirFileList:
            yield fileName, dirName

def scrapAll(docPath: str) -> Tuple[List[str], List[str], List[str]]:
    """Lists all pertinent files in the documentation.
    Returns: class-files, namespace-files, enumerator-files"""
    def isClassFile(name):
        """Returns True if name matches a class description file False if not"""
        return re.fullmatch(r'class_.*^(-members)\.html', name) != None
    classFiles = [pth.join(f,d) for f,d in allDocFiles(docPath)
                                if isClassFile(f)]
    namespaceFiles = [pth.join(docPath, 'namespace_isaac.html')]
    enumFiles = [pth.join(docPath, 'group___enumerations.html')]
    return classFiles, namespaceFiles, enumFiles

def findFunctionsInLine(line: str) -> Dict[Any]:
    """Parses a line to detect if it contains class functions.
    Returns what it found."""
    ret = {}
    functionSignMatcher = RE_FUNCTION_SIGNATURE.search(line)
    if functionSignMatcher is not None: #found a function signature
        #identifiy its name
        ret[IdentKey.NAME] = functionSignMatcher.group('name')

        #identify its parameters
        for
        #identify its return value
        funReturns = functionSignMatcher.group('returns')
        if funReturns is None:


def parseClass(fileName: str) -> 'some stuff':
    """Parses a file that holds info about classes."""
    with open(fileName, 'r') as classFile:
        content = classFile.read(); classFile.seek(0)
        className = RE_CLASS_NAME.search(content).group(1)
        classInheritence = {}

        inheritedMatcher = RE_INHERITS_FROM.search(content)
        if inheritedMatcher is not None:
            classInheritence[IdentKey.INHERITS_FROM] = inheritedMatcher.group(1)
        del inheritedMatcher
        del content

        for curLine in classFile:
            curLineFunction = findFunctionsInLine(curLine)
            curLineAttribs = findAttribInLine(curLine)
            foundFunction = RE_FUNCTION_SIGNATURE.search(curLine)
            if foundFunction is not None:

            else:




if __name__ == '__main__':
    argDocPath = sys.argv[1]
    argCompletercPath = sys.argv[2]
    scrapAll(argDocPath)
