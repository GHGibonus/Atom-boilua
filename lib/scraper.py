#!/bin/usr/python3
#pylint: disable=C0103,W0401,R0903,C0321,W0201,W0231,C0111,C0330,C0326
"""Scraps data from the isaac API doc and copies it in the target file.
The script takes in argument the path to the Afterbirth API docs."""

import re
import os
import os.path as pth
import sys
from typing import (
    Iterator, Tuple, List, Match, cast,
    Optional, Union, NamedTuple, IO, Callable )

from scraper_regexs import *

def tryMatch(x: Match, prop: str) -> bool:
    """Convinience function to test existance of a group in match object"""
    try:
        return x.group(prop) is not None
    except (IndexError, AttributeError):
        return False

def tryMatchNone(x: Optional[Match], prop: str) -> Optional[str]:
    """Convinience function to test existance of a group in an U[Match,None]."""
    if x is None:
        return None
    else:
        return x.group(prop)

def tryMatchString(x: Optional[Match], prop: str) -> str:
    """Like tryMatchNone but returns '' instead of None"""
    if x is None:
        return ''
    else:
        ret = x.group(prop)
        return ret if ret is not None else ''


class InvalidRematcher(Exception):
    """Rose when trying to create an object from an invalid matcher."""
    def __init__(self,
                 msg: str= 'Couldn\'t construct Class from matcher') -> None:
        super().__init__()
        self.message = msg

class InvalidFunctionRematcher(InvalidRematcher):
    def __init__(self,
                 msg: str= 'Couldn\'t construct function form line') -> None:
        super().__init__()
        self.message = msg

class InvalidAttributeRematcher(InvalidRematcher):
    def __init__(self,
                 msg: str= 'Couldn\'t construct attribute form line') -> None:
        super().__init__()
        self.message = msg

class UpdatedDocError(Exception):
    """Rose when the script detects that the Afterbirth API doc structure
    changed."""
    def __init__(self,
                 msg: str= 'This script is probably not compatible with the \
                 current Afterbirth+ doc API, please see what you \
                 can do') -> None:
        super().__init__()
        self.message = msg


class LuaType:
    """A simple lua type description.
    The constructor provides means to interpolate the type from the docs."""
    name = None #type: str
    isConst = None #type: bool
    isStatic = None #type: bool

    def __init__(self,
                 typeHint: Union[Match, str]= None,
                 isConst: bool= False,
                 isStatic: bool= False) -> None:
        if typeHint is None:
            self.__initFlat('nil')
        elif not isinstance(typeHint, str):
            self.__initFlat(
                typeHint.group('type'),
                tryMatch(typeHint, 'const'),
                tryMatch(typeHint, 'static') )
        else:
            self.__initFlat(typeHint, isConst, isStatic)

    def __initFlat(self,
                   name: str='', isConst: bool= False, isStatic: bool= False):
        self.name = name if name != '' else 'nil' # type: str
        self.isConst = isConst # type: bool
        self.isStatic = isStatic # type: bool


class LuaVariable:
    """A lua variable, inherited by classes describing attributes and other."""
    name = None #type: str
    luaType = None #type: LuaType

    def __init__(self, name: str, luaType: LuaType) -> None:
        self.name = name # type: str
        self.luaType = luaType # type: LuaType


class LuaParam(LuaVariable):
    """A parameter of a Lua function."""
    def __init__(self, line: str) -> None:
        """Initializes the parameter interpolating from line."""
        paramMatcher = RE_FUNCTION_PARAMETER.search(line)
        super().__init__(paramMatcher.group('name'), LuaType(paramMatcher))


class LuaAttribute(LuaVariable):
    """An attribute of a Lua class.
    The constructor can interpolate from the doc strings"""
    # super()
    description = None #type: str

    def __init__(self, line: str) -> None:
        """Initializes the attribute using a reg-exed line."""
        attribScraper = RE_ATTRIBUTE.search(line)
        name  = tryMatchNone(attribScraper, 'name')
        if name is None:
            raise InvalidAttributeRematcher()
        self.name = name # type: str
        typeFetcher = RE_ATTRIBUTE_TYPE.search(
            RE_HTML_REPLACER.sub('', attribScraper.group('type')))
        self.description = '' # type: str
        self.luaType = LuaType(typeFetcher) # type: LuaType


class LuaFunction:
    """A structure to hold information about lua functions."""
    name = None #type: str
    description = None #type: str
    parameters = None #type: List[LuaParam]
    returnType = None #type: LuaType

    def __init__(self, arg: Union[Match, str]) -> None:
        """Initializes a function with a re.Match object or a string
        to parse."""
        if not isinstance(arg, str):
            arg = cast(Match, arg)
            self.__initMatch(arg)
        else:
            self.__initLine(arg)

    def __initLine(self, line: str):
        functionSignMatcher = RE_FUNCTION_SIGNATURE.search(line)
        if functionSignMatcher is not None:
            self.__initMatch(functionSignMatcher)
        else:
            raise InvalidFunctionRematcher()

    def __initMatch(self, functionRematcher: Match):
        if functionRematcher is None:
            raise InvalidFunctionRematcher()
        self.name = functionRematcher.group('name') # type: str
        self._findParameters(functionRematcher.group('parameters'))
        self._findReturnval(functionRematcher.group('returns'))
        self.description = '' # type: str

    def _findParameters(self, paramMatchedVals: str):
        """Finds the parameters and adds them to instance."""
        if not paramMatchedVals: return
        paramScraper = RE_HTML_REPLACER.sub('', paramMatchedVals).split(', ')
        self.parameters = [LuaParam(param) for param in paramScraper]

    def _findReturnval(self, retMatchval: str):
        """Finds the function return value in retMatchval."""
        if not retMatchval:
            self.returnType = LuaType() # type: LuaType
        else:
            returnMatcher = RE_FUNCTION_RETURNS.search(
                RE_HTML_REPLACER.sub('', retMatchval))
            self.returnType = LuaType(returnMatcher) # type: LuaType


class LuaMethod(LuaFunction):
    """Extends lua functions to account for class constructors."""
    def __init__(self, args: Union[Match, str], className: str) -> None:
        super().__init__(args)
        if self.name == className:
            self.returnType = LuaType(className, isStatic= True)


def _parseDescription(line: str) -> Optional[str]:
    """Returns a string if it parsed a description in line.
    Returns None otherwise."""
    try:
        description = subHtmlFlags(
            RE_DESCRIPTION.search(line).group(1).strip())
    except AttributeError:
        return None
    else:
        return description


class LuaClass:
    """Describes a lua class."""
    parents = None #type: List[LuaClass]
    name = None #type: str
    description = None #type: str
    methods = None #type: List[LuaFunction]
    attributes = None #type: List[LuaAttribute]

    def __init__(self, classPath: str) -> None:
        """Initializes the class based on infos gathered in the class file.
        TODO: implement parent class inheritance"""
        with open(classPath, 'r') as classFile:
            content = classFile.read()
            self.name = RE_CLASS_NAME.search(content).group(1) # type: str
            self._parentNames = [] # type: List[str]
            self.attributes = [] # type: List[LuaAttribute]
            self.methods = [] # type: List[LuaFunction]

            inheritedMatcher = RE_INHERITS_FROM.search(content)
            if inheritedMatcher is not None:
                self._parentNames += [inheritedMatcher.group(1)]
            del inheritedMatcher
            del content

            classFile.seek(0)
            METHOD_SET = 1 #flags to decide to whome
            ATTRIB_SET = 2 #the last description must
            lastSet = 0 # be attributed
            for curLine in classFile:
                try: #try to find a function.
                    self.methods += [LuaFunction(curLine)]
                except InvalidFunctionRematcher: pass
                else: lastSet = METHOD_SET

                try: #try to find an attribute.
                    self.attributes += [LuaAttribute(curLine)]
                except InvalidAttributeRematcher: pass
                else: lastSet = ATTRIB_SET

                lineDescr = _parseDescription(curLine)
                if lineDescr is None:
                    continue
                else:
                    if lastSet == METHOD_SET:
                        self.methods[-1].description = lineDescr
                    elif lastSet == ATTRIB_SET:
                        self.attributes[-1].description = lineDescr
                    else: continue


class LuaNamespace:
    """Describes a lua namespace."""
    name = None #type: str
    functions = None #type: List[LuaFunction]

    def __init__(self, namespacePath: str) -> None:
        """Initializes the namespace descibed in the file namespacePath."""
        with open(namespacePath, 'r') as namespaceFile:
            content = namespaceFile.read()
            self.name = RE_NAMESPACE_NAME.search(content).group(1) # type: str
            self.functions = [] # type: List[LuaFunction]
            del content

            namespaceFile.seek(0)
            for curLine in namespaceFile:
                try: #try to find a function
                    self.functions += [LuaFunction(curLine)]
                except InvalidFunctionRematcher: pass

                lineDescr = _parseDescription(curLine)
                if lineDescr is not None:
                    self.functions[-1].description = lineDescr


EnumTag = NamedTuple('EnumTag', [
    ('name', str),
    ('value', int),
    ('description', str)
])


class LuaEnumerator:
    name = None # type: str
    members = None # type: List[EnumTag]
    streamInit = None # type: Callable[[IO],Optional[LuaEnumerator]]

    def __init__(self, name: str, members: List[EnumTag]) -> None:
        """Initializes the class as a struct."""
        self.name = name
        self.members = members


def streamInit(openFile: IO) -> Optional[LuaEnumerator]:
    """Reads the text stream for a lua enumerator.

    It will reads the stream untill it completes a LuaEnumerator,
    it will then return it. Note that the IO pointer in argument will
    be modified by this function."""
    curMemberList = [] # type: List[EnumTag]
    curEnumName = None # type: str

    oldPointerPosition = openFile.tell()
    curLine = openFile.readline() # type: str
    while curLine != '':
        enumNameScraper = RE_ENUM_NAME.search(curLine)
        if enumNameScraper is not None:
            if curEnumName is None:
                curEnumName = enumNameScraper.group(1)
            else:
                openFile.seek(oldPointerPosition) #unconsumes last line
                return LuaEnumerator(curEnumName, curMemberList)
        else:
            memberScraper = RE_ENUM_MEMBER.search(curLine)
            if memberScraper is not None:
                descripString = tryMatchString(memberScraper, 'desc')
                curMemberList += [EnumTag(
                    memberScraper.group('name'),
                    0, #the value enumTag field might be pertinent one day
                    RE_HTML_REPLACER.sub('', descripString)
                )]
        oldPointerPosition = openFile.tell()
        curLine = openFile.readline()
    # reached end of file
    if curEnumName is not None:
        return LuaEnumerator(curEnumName, curMemberList)
    else:
        return None
LuaEnumerator.streamInit = streamInit #add the method to the class as static


def allDocFiles(docPath: str) -> Iterator[Tuple[str, str]]:
    """List all files in the docPath.

    Returns their file name and associated directory paths.
    Note: currently the doc only has one level deep file organization,
    and this function only works if it is the case.
    If this ever came to change, this function needs update."""
    for dirEntry in os.scandir(docPath):
        if dirEntry.is_dir():
            try: assert dirEntry.name == 'search'
            except AssertionError: raise UpdatedDocError

            for searchFile in os.scandir(dirEntry.path):
                yield searchFile.name, dirEntry.path
        else:
            yield dirEntry.name, docPath


def categorizeFiles(docPath: str) \
        -> Tuple[List[str], List[str], List[str], List[str]]:
    """Lists all pertinent files in the documentation.
    Returns: class-files, namespace-files, enumerator-files"""

    def isClassFile(name: str) -> bool: #filter for class-description files
        """Returns True if name matches a class description file."""
        return re.fullmatch(r'class_[0-9A-Za-z_]*(?!-members.html)\.html',
                            name) is not None
    #classFiles = [] # type: List[str]
    #for (curFile, curDir) in allDocFiles(docPath):
    #    if isClassFile(curFile):
    #        classFiles += [pth.join(curDir, curFile)]
    return (
        [pth.join(curDir, curFile) for curFile, curDir in allDocFiles(docPath)
                                   if isClassFile(curFile)],
        [pth.join(docPath, 'namespace_isaac.html')],
        [pth.join(docPath, 'group___enumerations.html')],
        [pth.join(docPath, 'group___functions.html')] )


class AfterbirthApi:
    """Holds all the informations about the API."""
    classes = [] # type: List[LuaClass]
    enumerators = [] # type: List[LuaEnumerator]
    namespaces = [] # type: List[LuaNamespace]
    globalFunctions = [] # type: List[LuaFunction]

    def __init__(self, docPath: str) -> None:
        classFiles, nsFiles, enumFiles, funFiles = categorizeFiles(docPath)

        self.classes = [LuaClass(f) for f in classFiles]
        self.namespaces = [LuaNamespace(f) for f in nsFiles]
        for curFile in enumFiles + funFiles:
            with open(curFile, 'r') as enumStream:
                while True: #do while, breaks when reached end of stream
                    curEnum = LuaEnumerator.streamInit(enumStream)
                    if curEnum is None:
                        break
                    self.enumerators += [curEnum]


if __name__ == '__main__':
    argDocPath = ' '.join(sys.argv[1:])
    abpApi = AfterbirthApi(argDocPath)
    print(abpApi)
