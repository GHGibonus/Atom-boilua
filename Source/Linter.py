import sublime, sublime_plugin, os, sys, json, re
PYTHON_VERSION = sys.version_info

AFTERBIRTH_API = None

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

class TokenEnum(object):
	COLON = 0
	COMMA = 1
	DOT = 2
	DOUBLE_COLON = 3
	KW_AND = 4
	KW_BREAK = 5
	KW_DO = 6
	KW_ELSE = 7
	KW_ELSEIF = 8
	KW_END = 9
	KW_FALSE = 10
	KW_FOR = 11
	KW_FUNCTION = 12
	KW_GOTO = 13
	KW_IF = 14
	KW_IN = 15
	KW_LOCAL = 16
	KW_NIL = 17
	KW_NOT = 18
	KW_OR = 19
	KW_REPEAT = 20
	KW_RETURN = 21
	KW_THEN = 22
	KW_TRUE = 23
	KW_UNTIL = 24
	KW_WHILE = 25
	LEFT_BRACKET = 26
	LEFT_CURLY_BRACE = 27
	LEFT_PARENTHESIS = 28
	NAME = 29
	NUMBER = 30
	OP_ADD = 31
	OP_ASSIGN = 32
	OP_BIT_AND = 33
	OP_BIT_LSHIFT = 34
	OP_BIT_NOT_XOR = 35
	OP_BIT_OR = 36
	OP_BIT_RSHIFT = 37
	OP_CONCAT = 38
	OP_DIV = 39
	OP_EQUAL = 40
	OP_GREATER = 41
	OP_GREATER_THAN_OR_EQUAL = 42
	OP_IDIV = 43
	OP_LEN = 44
	OP_LESS = 45
	OP_LESS_THAN_OR_EQUAL = 46
	OP_MOD = 47
	OP_MUL = 48
	OP_NOT_EQUAL = 49
	OP_POW = 50
	OP_SUB = 51
	RIGHT_BRACKET = 52
	RIGHT_CURLY_BRACE = 53
	RIGHT_PARENTHESIS = 54
	SEMICOLON = 55
	STRING = 56
	TRIPLE_DOT = 57
	NEWLINE = 58
	UNMATCHED = 59
	EOF = 60
	LINE_COMMENT = 61
	BLOCK_COMMENT = 62
	WHITESPACE = 63

TOKEN_DESCRIPTION = [
	"COLON",
	"COMMA",
	"DOT",
	"DOUBLE_COLON",
	"KW_AND",
	"KW_BREAK",
	"KW_DO",
	"KW_ELSE",
	"KW_ELSEIF",
	"KW_END",
	"KW_FALSE",
	"KW_FOR",
	"KW_FUNCTION",
	"KW_GOTO",
	"KW_IF",
	"KW_IN",
	"KW_LOCAL",
	"KW_NIL",
	"KW_NOT",
	"KW_OR",
	"KW_REPEAT",
	"KW_RETURN",
	"KW_THEN",
	"KW_TRUE",
	"KW_UNTIL",
	"KW_WHILE",
	"LEFT_BRACKET",
	"LEFT_CURLY_BRACE",
	"LEFT_PARENTHESIS",
	"NAME",
	"NUMBER",
	"OP_ADD",
	"OP_ASSIGN",
	"OP_BIT_AND",
	"OP_BIT_LSHIFT",
	"OP_BIT_NOT_XOR",
	"OP_BIT_OR",
	"OP_BIT_RSHIFT",
	"OP_CONCAT",
	"OP_DIV",
	"OP_EQUAL",
	"OP_GREATER",
	"OP_GREATER_THAN_OR_EQUAL",
	"OP_IDIV",
	"OP_LEN",
	"OP_LESS",
	"OP_LESS_THAN_OR_EQUAL",
	"OP_MOD",
	"OP_MUL",
	"OP_NOT_EQUAL",
	"OP_POW",
	"OP_SUB",
	"RIGHT_BRACKET",
	"RIGHT_CURLY_BRACE",
	"RIGHT_PARENTHESIS",
	"SEMICOLON",
	"STRING",
	"TRIPLE_DOT",
	"NEWLINE",
	"UNMATCHED",
	"EOF",
	"LINE_COMMENT",
	"BLOCK_COMMENT",
	"WHITESPACE"
]

class Token(object):
	__slots__ = [
		"type", # TokenEnum
		"line", # str
		"column", # int
		"value" # int
	]
	def __init__(self, aType, aValue, aLine, aColumn):
		self.type = aType
		self.line = aLine
		self.column = aColumn
		self.value = aValue

	def __str__(self):
		return """
===== Token =====
Type: %s
Value: '%s'
Line: %d
Column: %d
""" % (TOKEN_DESCRIPTION[self.type], self.value, self.line, self.column)

class LexingError(Exception):
	__slots__ = [
		"message", # str
		"line", # int
		"column" # int
	]
	def __init__(self, a_message, a_line, a_column):
		self.message = a_message
		self.line = a_line
		self.column = a_column

class ParsingError(Exception):
	__slots__ = [
		"message", # str
		"line", # int
		"column" # int
	]
	def __init__(self, a_message, a_line, a_column):
		self.message = a_message
		self.line = a_line
		self.column = a_column

class Parser(object):
	__slots__ = [
		"token_regex",
		"keyword_regex",
		"tokens"
	]
	def __init__(self):
		token_specifications = [
			(TokenEnum.NUMBER, r"0[xX][0-9a-fA-F]+[pP][+-]?[0-9]+|0[xX]\.[0-9a-fA-F]+(?:[pP][+-]?[0-9]+)?|0[xX][0-9a-fA-F]+(?:\.[0-9a-fA-F]*(?:[pP][+-]?[0-9]+)?)?|[0-9]+(?:[eE][+-]?[0-9]+)|\.[0-9]+(?:[eE][+-]?[0-9]+)?|[0-9]+(?:\.[0-9]*(?:[eE][+-]?[0-9]+)?)?"),
			(TokenEnum.BLOCK_COMMENT, r"\-\-\[\[[^\]]*\]\]\-\-[^\n\r]*"),
			(TokenEnum.LINE_COMMENT, r"\-\-[^\n\r]*"),
			(TokenEnum.DOUBLE_COLON, r"::"),
			(TokenEnum.COLON, r":"),
			(TokenEnum.COMMA, r","),
			(TokenEnum.LEFT_BRACKET, r"\["),
			(TokenEnum.LEFT_CURLY_BRACE, r"\{"),
			(TokenEnum.LEFT_PARENTHESIS, r"\("),
			(TokenEnum.RIGHT_BRACKET, r"\]"),
			(TokenEnum.RIGHT_CURLY_BRACE, r"\}"),
			(TokenEnum.RIGHT_PARENTHESIS, r"\)"),
			(TokenEnum.NAME, r"[_a-zA-Z][_a-zA-Z0-9]*"),
			(TokenEnum.OP_ADD, r"\+"),
			(TokenEnum.OP_BIT_AND, r"&"),
			(TokenEnum.OP_BIT_LSHIFT, r"<<"),
			(TokenEnum.OP_BIT_NOT_XOR, r"~"),
			(TokenEnum.OP_BIT_OR, r"\|"),
			(TokenEnum.OP_BIT_RSHIFT, r">>"),
			(TokenEnum.OP_EQUAL, r"=="),
			(TokenEnum.OP_ASSIGN, r"="),
			(TokenEnum.OP_GREATER_THAN_OR_EQUAL, r">="),
			(TokenEnum.OP_GREATER, r">"),
			(TokenEnum.OP_IDIV, r"//"),
			(TokenEnum.OP_DIV, r"/"),
			(TokenEnum.OP_LEN, r"#"),
			(TokenEnum.OP_LESS_THAN_OR_EQUAL, r"<="),
			(TokenEnum.OP_LESS, r"<"),
			(TokenEnum.OP_MOD, r"\%"),
			(TokenEnum.OP_MUL, r"\*"),
			(TokenEnum.OP_NOT_EQUAL, r"~="),
			(TokenEnum.OP_POW, r"\^"),
			(TokenEnum.OP_SUB, r"\-"),
			(TokenEnum.SEMICOLON, r";"),
			(TokenEnum.STRING, r"\"([^\"]*)\"|\'[^\'']*\'"),
			(TokenEnum.TRIPLE_DOT, r"\.\.\."),
			(TokenEnum.OP_CONCAT, r"\.\."),
			(TokenEnum.DOT, r"\."),
			(TokenEnum.NEWLINE, r"[\n\r]"),
			(TokenEnum.WHITESPACE, r"[ \t]"),
			(TokenEnum.UNMATCHED, r"."),
		]
		self.token_regex = re.compile("|".join("(?P<t%s>%s)" % pair for pair in token_specifications))
		keyword_specifications = [
			(TokenEnum.KW_AND, r"and"),
			(TokenEnum.KW_BREAK, r"break"),
			(TokenEnum.KW_DO, r"do"),
			(TokenEnum.KW_ELSE, r"else"),
			(TokenEnum.KW_ELSEIF, r"elseif"),
			(TokenEnum.KW_END, r"end"),
			(TokenEnum.KW_FALSE, r"false"),
			(TokenEnum.KW_FOR, r"for"),
			(TokenEnum.KW_FUNCTION, r"function"),
			(TokenEnum.KW_GOTO, r"goto"),
			(TokenEnum.KW_IF, r"if"),
			(TokenEnum.KW_IN, r"in"),
			(TokenEnum.KW_LOCAL, r"local"),
			(TokenEnum.KW_NIL, r"nil"),
			(TokenEnum.KW_NOT, r"not"),
			(TokenEnum.KW_OR, r"or"),
			(TokenEnum.KW_REPEAT, r"repeat"),
			(TokenEnum.KW_RETURN, r"return"),
			(TokenEnum.KW_THEN, r"then"),
			(TokenEnum.KW_TRUE, r"true"),
			(TokenEnum.KW_UNTIL, r"until"),
			(TokenEnum.KW_WHILE, r"while"),
		]
		self.keyword_regex = re.compile("|".join("(?P<t%s>%s)" % pair for pair in keyword_specifications))

	def tokenize(self, a_source_code):
		line = 1
		column = -1
		for match in self.token_regex.finditer(a_source_code):
			type_ = match.lastgroup
			value_ = match.group(type_)
			type_ = int(match.lastgroup[1:])
			if type_ == TokenEnum.WHITESPACE:
				continue
			elif type_ == TokenEnum.NAME:
				keyword = self.keyword_regex.match(value_)
				if keyword:
					type_ = int(keyword.lastgroup[1:])
			elif type_ == TokenEnum.BLOCK_COMMENT:
				i = value_.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
				continue
			elif type_ == TokenEnum.LINE_COMMENT:
				continue
			elif type_ == TokenEnum.STRING:
				value_ = value_[1:-1]
				yield Token(type_, value_, line, match.start()-column)
				i = value_.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
				continue
			elif type_ == TokenEnum.NEWLINE:
				line += 1
				column = match.end()-1
			elif type_ == TokenEnum.UNMATCHED:
				raise LexicalError("Encountered an unexpected character ('%s')." % value_, line, match.start()-column)
			yield Token(type_, value_, line, match.start()-column)
		yield Token(TokenEnum.EOF, "\n", line, 1)

	def parse(self, a_source_code, a_symbol_table = []):
		lines = []
		self.tokens = []
		for token in self.tokenize(a_source_code):
			if token.type == TokenEnum.EOF:
				break
			elif token.type == TokenEnum.NEWLINE:
				if self.tokens:
					lines.append(self.tokens)
				self.tokens = []
				continue
			self.tokens.append(token)
			print(token)
		[print(line) for line in lines]

class EventListener(sublime_plugin.EventListener):
	__slots__ = [
		"parser",
		"parsing",
		"queue",
		"view"
	]
	def __init__(self):
		self.parser = Parser()
		self.parsing = False
		self.queue = 0

	def on_query_completions(self, a_view, a_prefix, a_locations):
		if "source.lua" in a_view.scope_name(0):
			if self.parsing:
				return
			self.parsing = True
			# Build symbol table here from cached statements
			caret_point = a_view.sel()[0].begin()
			script_to_cursor = a_view.substr(sublime.Region(a_view.line(caret_point).begin(), caret_point))
			if len(a_prefix) > 0:
				script_to_cursor = script_to_cursor[:-len(a_prefix)]
			print("\nLinting line: %s" % script_to_cursor)
			self.parser.parse(script_to_cursor)#, symbol_table)
			self.parsing = False

	def on_modified(self, a_view):
		if "source.lua" in a_view.scope_name(0):
			self.view = a_view
			self.queue += 1
			sublime.set_timeout_async(self.lint, 500)

	def lint(self):
		self.queue -= 1
		if self.queue > 0:
			return
		if self.parsing:
			return
		self.parsing = True
		
		script_to_cursor = self.view.substr(sublime.Region(0, self.view.size()))
		print("\nLinting script:\n%s\nEnd of script" % script_to_cursor)
		self.parser.parse(script_to_cursor)
		self.parsing = False