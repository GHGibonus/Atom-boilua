#!/bin/usr/python3
#pylint: disable=C0103,W0401,R0903,C0321,C0326,W0201,C0111,W0231,C0330
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
# upstream integration

"""Scraps data from the isaac API doc and copies it in the target file.

The script takes in argument the path to the Afterbirth API docs."""

import re
import os
import os.path as pth
import sys
from typing import (
    Iterator, Tuple, List, Match,
    Optional, Union, NamedTuple, IO )

from scraper_regexs import *

class InvalidRematcher(Exception):
    """Rose when trying to create an object from an invalid matcher."""
    def __init__(self,
                 msg: str = 'Couldn\'t construct Class from matcher') -> None:
        super().__init__()
        self.message =  msg

class InvalidFunctionRematcher(InvalidRematcher):
    def __init__(self,
                 msg: str = 'Couldn\'t construct function form line') -> None:
        super().__init__()
        self.message =  msg

class InvalidAttributeRematcher(InvalidRematcher):
    def __init__(self,
                 msg: str = 'Couldn\'t construct attribute form line') -> None:
        super().__init__()
        self.message =  msg


class LuaType:
    """A simple lua type description.

    The constructor provides means to interpolate the type from the docs."""
    name = None #type: str
    isConst = None #type: bool
    isStatic = None #type: bool
    def __init__(self, typeMatcher: Match= None) -> None:
        if typeMatcher is None:
            self.__initFlat('nil')
        else:
            self.__initFlat(
                typeMatcher.group('type'),
                typeMatcher.group('const') is not None,
                typeMatcher.group('static') is not None )

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
    def __init__(self, name: str, luaType: LuaType) -> None:
        super().__init__(name, luaType)


class LuaAttribute(LuaVariable):
    """An attribute of a Lua class.

    The constructor can interpolate from the doc strings"""
    # super()
    comment = None #type: str
    def __init__(self, line: str) -> None:
        """Initializes the attribute using a reg-exed line."""
        attribScraper = RE_ATTRIBUTE.search(line)
        name  = attribScraper.group('name')
        if name is None:
            raise InvalidAttributeRematcher()
        self.name = name # type: str
        typeFetcher = RE_ATTRIBUTE_TYPE.search(
            RE_HTML_REPLACER.sub('', attribScraper.group('type')))
        self.luaType = LuaType(typeFetcher) # type: LuaType
        self.comment = '' # type: str


class LuaFunction:
    """A structure to hold information about lua functions."""
    name = None #type: str
    comment = None #type: str
    parameters = None #type: List[LuaParam]
    returnType = None #type: LuaType
    def __init__(self, arg: Union[Match, str]) -> None:
        if isinstance(arg, Match):
            self.__initMatch(arg)
        elif isinstance(arg, str):
            self.__initLine(arg)
        else:
            raise TypeError("Wrong argument type to LuaFunction.__init__")

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
        self.comment = '' # type: str

    def _findParameters(self, paramMatchedVals: str):
        """Finds the parameters and adds them to instance.

        The type for paramMatchedVals is what I could interpolate from the
        Python doc."""
        self.parameters = [] # type: List[LuaParam]
        if not paramMatchedVals: #NOTE:not sure what this is checking for
            return
        paramScraper = RE_HTML_REPLACER.sub('', paramMatchedVals).split(', ')
        for param in paramScraper:
            paramMatcher = RE_FUNCTION_PARAMETER.search(param)
            paramName = paramMatcher.group('name')
            self.parameters += [LuaParam(paramName, LuaType(paramMatcher))]

    def _findReturnval(self, retMatchval: str):
        """Finds the return value found from that retMatchval thingy."""
        if not retMatchval: #NOTE: not sure what this is for
            self.returnType = LuaType() # type: LuaType
        else:
            returnMatcher = RE_FUNCTION_RETURNS.search(
                RE_HTML_REPLACER.sub('', retMatchval))
            self.returnType = LuaType(returnMatcher) # type: LuaType

    @staticmethod
    def liveFunctionGen(line: str) -> Optional[LuaFunction]:
        """Reads lines as a stream and returns a LuaFunction when it knows
        the function definition has been completed. Otherwise returns None."""
        pass


def _parseDescription(line: str) -> Optional[str]:
    """Returns a string if it parsed a description in line.

    Returns None otherwise."""
    description = RE_HTML_REPLACER.sub(
        '', RE_DESCRIPTION.search(line).group(1).strip() )
    return description if len(description) > 0 else None


class LuaClass:
    """Describes a lua class."""
    parents = None #type: List[LuaClass]
    name = None #type: str
    description = None #type: str
    methods = None #type: List[LuaFunction]
    attributes = None #type: List[LuaAttribute]
    def __init__(self, classPath: str) -> None:
        """Initializes the class based on infos gathered in the class file.

        NOTE: the parent cannot be a reference to LuaClass, because those
        are not written in the doc (obviously), however, it is possible to
        set it afterward with the referenceClasses() method.
        The scraper will take from the lua doc the name of the parent
        classes and store it into a private variable untill the call to
        referenceClasses()."""
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
            for curLine in classFile:
                try: #try to find a function, if unsuccessful
                    self.methods += [LuaFunction(curLine)]
                except InvalidFunctionRematcher: pass
                try: #try to find an attribute, if unsuccessful
                    self.attributes += [LuaAttribute(curLine)]
                except InvalidAttributeRematcher: pass
                lineDescr = _parseDescription(curLine)
                if lineDescr is None:
                    continue
                self.methods[-1].comment = lineDescr
                self.attributes[-1].comment = lineDescr

                #It seems in the original code that the description
                #is associated with a previously found function or attribute
                #I'm not sure how to handle that yet...


class LuaNamespace:
    """Describes a lua namespace."""
    name = None #type: str
    functions = None #type: List[LuaFunction]
    def __init__(self, namespacePath: str) -> None:
        """Initializes namespace descibed in the file namespacePath."""
        with open(namespacePath, 'r') as namespaceFile:
            content = namespaceFile.read()
            self.name = RE_NAMESPACE_NAME.search(content).group(1) # type: str
            self.functions = [] # type: List[LuaFunction]
            del content

            namespaceFile.seek(0)
            for curLine in namespaceFile:
                try: #try to find a function, if unsuccessful
                    self.functions += [LuaFunction(curLine)]
                except InvalidFunctionRematcher: pass
                lineDescr = _parseDescription(curLine)
                if lineDescr is not None:
                    self.functions[-1].comment = lineDescr


EnumTag = NamedTuple('EnumTag', [
    ('name', str),
    ('value', int),
    ('description', str)
])


class LuaEnumerator:
    name = None # type: str
    members = None # type: List[EnumTag]
    def __init__(self, name: str, members: List[EnumTag]) -> None:
        """Initializes the class like a dummy."""
        self.name = name
        self.members = members

    @staticmethod
    def streamInit(openFile: IO) -> Optional[LuaEnumerator]:
        """Reads the text stream for a lua enumerator.

        It will reads the stream untill it completed a LuaEnumerator,
        it will then return it. Note that the IO pointer will
        be modified by this function."""
        curMemberList = [] # type: List[EnumTag]
        curEnumName = None # type: str
        oldPointerPosition = openFile.tell()
        for curLine in openFile:
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
                    curMemberList += [EnumTag(
                        memberScraper.group('name'),
                        0,
                        RE_HTML_REPLACER.sub('',memberScraper.group('desc'))
                    )]
            oldPointerPosition = openFile.tell()
        # reached end of file
        if curEnumName is not None:
            return LuaEnumerator(curEnumName, curMemberList)
        else:
            return None


def allDocFiles(docPath: str) -> Iterator[Tuple[str, str]]:
    """List all files in the docPath.

    Returns their file name and associated directory paths"""
    for fileData in os.walk(docPath):
        for __, dirName, fileName in fileData:
            yield fileName, dirName

def categorizeFiles(docPath: str) -> Tuple[List[str], List[str], List[str]]:
    """Lists all pertinent files in the documentation.

    Returns: class-files, namespace-files, enumerator-files"""
    def isClassFile(name: str) -> bool:
        """Returns True if name matches a class description file."""
        return re.fullmatch(r'class_.*(?!-members)\.html', name) != None
    classFiles = [pth.join(f,d) for f,d in allDocFiles(docPath)
                                if isClassFile(f)] # type: List[str]
    namespaceFiles = [pth.join(docPath, 'namespace_isaac.html')]
    enumFiles = [pth.join(docPath, 'group___enumerations.html')]
    return classFiles, namespaceFiles, enumFiles


class AfterbirthApi:
    """Describes the API as it is presented in the doc files."""
    classes = [] # type: List[LuaClass]
    enumerators = [] # type: List[LuaEnumerator]
    namespaces = [] # type: List[LuaNamespace]
    def __init__(self, docPath: str) -> None:
        classFiles, nsFiles, enumFiles = categorizeFiles(docPath)
        for curFile in classFiles:
            self.classes += [LuaClass(curFile)]
        for curFile in nsFiles:
            self.namespaces += [LuaNamespace(curFile)]
        for curFile in enumFiles:
            with open(curFile, 'r') as enumStream:
                while True: #do while, breaks when reached end of stream
                    curEnum = LuaEnumerator.streamInit(enumStream)
                    if curEnum is None:
                        break
                    self.enumerators += [curEnum]


if __name__ == '__main__':
    argDocPath = sys.argv[1]
    abpApi = AfterbirthApi(argDocPath)
    print(abpApi)
