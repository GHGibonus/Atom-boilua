#!/bin/usr/python3
#pylint: disable=C0301,C0103
"""Scraps data from the isaac API doc and copies it in the target file.

    The module must be called directly, the arguments are as following:
    1. the doc directory
    2. the luacompleterc output file."""

import re
import os
import sys
import json

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
RE_HTML_TAG_REPLACER = re.compile(r"<.*?>")

KEY_CONST = "Const"
KEY_STATIC = "Static"
KEY_ATTRIBUTES = "Attributes"
KEY_CLASSES = "Classes"
KEY_DESCRIPTION = "Description"
KEY_ENUMS = "Enums"
KEY_FUNCTIONS = "Functions"
KEY_MEMBERS = "Members"
KEY_NAME = "Name"
KEY_NAMESPACES = "Namespaces"
KEY_PARAMETERS = "Parameters"
KEY_RETURNS = "Returns"
KEY_TYPE = "Type"
KEY_INHERITS_FROM = "Inherits from"
# From that point onward, you get clean documented code

def scrapAll(docPath: str):
    """Scraps the Afterbirth+ API into digestible information."""
    pass

if __name__ == '__main__':
    docPath = sys.argv[1]
    completercPath = sys.argv[2]
    scrapAll(docPath)
