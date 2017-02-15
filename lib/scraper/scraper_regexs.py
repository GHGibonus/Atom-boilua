#pylint: disable=all

import re


_reic = re.IGNORECASE

#Regular expression patterns defined by Kapiainen
RE_CLASS_NAME =re.compile(
r"<div class=\"title\">(.+?) class reference</div>",
_reic)


RE_NAMESPACE_NAME =re.compile(
r"<div class=\"title\">(.+?) namespace reference</div>",
_reic)


RE_INHERITS_FROM =re.compile(
r"inherited from <a.+?>(.+?)</a>",
_reic)


RE_FUNCTION_SIGNATURE =re.compile(
r"(?:<td class=\"memitemleft\".+?>(?P<returns>.+?))?&#.+?;</td><td class=\"memitemright\".+?><a.+?>(?P<name>.+?)</a>\s+\((?P<parameters>.+?)?\)",
_reic)


RE_FUNCTION_RETURNS =re.compile(
r"(?:(?:(?P<const>const)\s*)?(?:(?P<static>static)\s*)?)*(?:(?P<type>[_a-z][_a-z0-9]*(?:::[_a-z][_a-z0-9]*)*))(?:\s+&amp;)?",
_reic)


RE_FUNCTION_PARAMETER =re.compile(
r"(?P<type>([_a-z][_a-z0-9]*(?:::[_a-z][_a-z0-9]*)*))(?:\s+(?P<name>[_a-z][_a-z0-9]*))?",
_reic)


RE_ATTRIBUTE =re.compile(
r"<td class=\"memitemleft\".+?>(?P<type>.+?)&#.+?;</td><td class=\"memitemright\".+?><a.+?>(?P<name>.+?)</a>",
_reic)


RE_ATTRIBUTE_TYPE =re.compile(
r"(?:(?:(?P<const>const)\s*)?(?:(?P<static>static)\s*)?)*(?:(?P<type>[_a-z][_a-z0-9]*(?:::[_a-z][_a-z0-9]*)*))(?:\s+&amp;)?",
_reic)


RE_ENUM_NAME =re.compile(
r"<h2 class=\"memtitle\"><span class=\"permalink\">\s*<a href=\"#(?P<link>\w+?)\">.+?</span>(?P<name>.+?)</h2>",
_reic)


RE_ENUM_MEMBER =re.compile(
r"<td class=\"fieldname\"><a.+?</a>(?P<name>.+?)&#.+?<td class=\"fielddoc\">(?:<p>(?P<desc>.+?)</p>)?",
_reic)


RE_DESCRIPTION = re.compile(r"<td class=\"mdescright\">(.+?)<a.+?</td>",
_reic)

RE_HTML_REPLACER = re.compile(r"<.*?>")


def subHtmlFlags(toReplace: str) -> str:
    """Returns a version of the string where html tags are replaced
    by their plaintext equivalent."""
    ret = RE_HTML_REPLACER.sub('', toReplace)
    return ret.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;','>')
