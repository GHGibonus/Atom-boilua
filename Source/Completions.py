import sublime, sublime_plugin, os, sys, json
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
	COLON = 1
	COMMA = 2
	DOT = 3
	DOUBLE_COLON = 4
	KW_AND = 5
	KW_BREAK = 6
	KW_DO = 7
	KW_ELSE = 8
	KW_ELSEIF = 9
	KW_END = 10
	KW_FALSE = 11
	KW_FOR = 12
	KW_FUNCTION = 13
	KW_GOTO = 14
	KW_IF = 15
	KW_IN = 16
	KW_LOCAL = 17
	KW_NIL = 18
	KW_NOT = 19
	KW_OR = 20
	KW_REPEAT = 21
	KW_RETURN = 22
	KW_THEN = 23
	KW_TRUE = 24
	KW_UNTIL = 25
	KW_WHILE = 26
	LEFT_BRACKET = 27
	LEFT_CURLY_BRACE = 28
	LEFT_PARENTHESIS = 29
	NAME = 30
	NUMBER = 31
	OP_ADD = 32
	OP_ASSIGN = 33
	OP_BIT_AND = 34
	OP_BIT_LSHIFT = 35
	OP_BIT_NOT_XOR = 36
	OP_BIT_OR = 37
	OP_BIT_RSHIFT = 38
	OP_CONCAT = 39
	OP_DIV = 40
	OP_EQUAL = 41
	OP_GREATER = 42
	OP_GREATER_THAN_OR_EQUAL = 43
	OP_IDIV = 44
	OP_LEN = 45
	OP_LESS = 46
	OP_LESS_THAN_OR_EQUAL = 47
	OP_MOD = 48
	OP_MUL = 49
	OP_NOT_EQUAL = 50
	OP_POW = 51
	OP_SUB = 52
	RIGHT_BRACKET = 53
	RIGHT_CURLY_BRACE = 54
	RIGHT_PARENTHESIS = 55
	SEMICOLON = 56
	STRING = 57
	TRIPLE_DOT = 58
	NEWLINE = 59
	UNMATCHED = 60
	EOF = 61

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
	"EOF"
]

class Token(object):
	"""Token objects."""
	__slots__ = ["type", "line", "column", "value"]
	def __init__(self, aType, aValue, aLine, aColumn):
	# aType: TokenEnum
	# aValue: string
	# aLine: int
	# aColumn: int
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
""" % (
		TokenDescription[self.type],
		self.value,
		self.line,
		self.column
	)

class LexicalError(Exception):
	"""Lexical error."""
	def __init__(self, aMessage, aLine, aColumn):
	# aMessage: string
	# aLine: int
	# aColumn: int
		self.message = aMessage
		self.line = aLine
		self.column = aColumn

class ParsingError(Exception):
	def __init__(self):
		pass

class Parser(object):
# Grammar from https://www.lua.org/manual/5.3/manual.html#9
	__slots__ = [
		"token_regex",
		"keyword_regex"
	]
	def __init__(self):
		token_specifications = [
			(TokenEnum.NUMBER, r"0[xX][0-9a-fA-F]+[pP][+-]?[0-9]+|0[xX]\.[0-9a-fA-F]+(?:[pP][+-]?[0-9]+)?|0[xX][0-9a-fA-F]+(?:\.[0-9a-fA-F]*(?:[pP][+-]?[0-9]+)?)?|[0-9]+(?:[eE][+-]?[0-9]+)|\.[0-9]+(?:[eE][+-]?[0-9]+)?|[0-9]+(?:\.[0-9]*(?:[eE][+-]?[0-9]+)?)?"),
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
			(TokenEnum.OP_BIT_OR, r"|"),
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
		"""Generates tokens from a string."""
		assert isinstance(a_source_code, str) #Prune
	# a_source_code: string (contains source code to tokenize)
		line = 1
		column = -1
		for match in self.token_regex.finditer(a_source_code):
			type_ = match.lastgroup
			value_ = match.group(type_)
			type_ = int(match.lastgroup[1:])
			if type_ == TokenEnum.WHITESPACE:
				continue
			elif type_ == TokenEnum.IDENTIFIER:
				keyword = self.keyword_regex.match(value_)
				if keyword:
					type_ = int(keyword.lastgroup[1:])
#				yield Token(type_, value_, line, match.start()-column)
#				continue
#			elif type_ == TokenEnum.LINE_COMMENT:
#				yield Token(TokenEnum.COMMENTLINE, None, line, match.start()-column)
#				continue
			elif type_ == TokenEnum.COMMENTBLOCK:
				i = value_.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
#				yield Token(TokenEnum.COMMENTBLOCK, None, line, match.start()-column)
#				continue
#			elif type_ == TokenEnum.MULTILINE:
#				line += 1
#				column = match.end()-1
#				continue
#			elif type_ == TokenEnum.DOCSTRING or type_ == TokenEnum.STRING:
			elif type_ == TokenEnum.STRING:
#				if type_ == TokenEnum.DOCSTRING:
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
#			if type_ == TokenEnum.NEWLINE:
#				line += 1
#				column = match.end()-1
		yield Token(TokenEnum.EOF, "\n", line, 1)

	def parse(self, a_source_code):
		for token in self.tokenize(a_source_code):
			print(token)

	def chunk(self):
		if self.block():
			return True
		return False

	def block(self):
		while self.stat():
			pass
		self.retstat()
		return True

	def stat(self):
		if self.accept(TokenEnum.SEMICOLON):
			return True
		elif self.varlist():
			self.expect(TokenEnum.OP_ASSIGN)
			if not self.explist():
				raise ParsingError()
				return False
			return True
		elif self.functioncall():
			return True
		elif self.label():
			return True
		elif self.accept(TokenEnum.KW_BREAK):
			return True
		elif self.accept(TokenEnum.KW_GOTO):
			self.expect(TokenEnum.NAME)
			return True
		elif self.accept(TokenEnum.KW_DO):
			if not self.block():
				raise ParsingError()
				return False
			self.expect(TokenEnum.KW_END)
			return True
		elif self.accept(TokenEnum.KW_WHILE):
			if not self.exp():
				raise ParsingError()
				return False
			self.expect(TokenEnum.KW_DO)
			if not self.block():
				raise ParsingError()
				return False
			self.expect(TokenEnum.KW_END)
			return True
		elif self.accept(TokenEnum.KW_REPEAT):
			if not self.block():
				raise ParsingError()
				return False
			self.expect(TokenEnum.KW_UNTIL)
			if not self.exp():
				raise ParsingError()
				return False
			return True
		elif self.accept(TokenEnum.KW_IF):
			if not self.exp():
				raise ParsingError()
				return False
			self.expect(TokenEnum.KW_THEN)
			if not self.block():
				raise ParsingError()
				return False
			while self.accept(TokenEnum.KW_ELSEIF):
				if not self.exp():
					raise ParsingError()
					return False
				self.expect(TokenEnum.KW_THEN)
				if not self.block():
					raise ParsingError()
					return False
			if self.accept(TokenEnum.KW_ELSE):
				if not self.block():
					raise ParsingError()
					return False
			return True
		elif self.accept(TokenEnum.KW_FOR):
			if self.peek(TokenEnum.OP_ASSIGN, 1):
				self.expect(TokenEnum.NAME)
				self.expect(TokenEnum.OP_ASSIGN)
				if not self.exp():
					raise ParsingError()
					return False
				self.expect(TokenEnum.COMMA)
				if not self.exp():
					raise ParsingError()
					return False
				if self.accept(TokenEnum.COMMA):
					if not self.exp():
						raise ParsingError()
						return False
				self.expect(TokenEnum.KW_DO)
				if not self.block():
					raise ParsingError()
					return False
				self.expect(TokenEnum.KW_END)
				return True
			elif self.namelist():
				self.expect(TokenEnum.KW_IN)
				if not self.explist():
					raise ParsingError()
					return False
				self.expect(TokenEnum.KW_DO)
				if not self.block():
					raise ParsingError()
					return False
				self.expect(TokenEnum.KW_END)
				return True
		elif self.accept(TokenEnum.KW_FUNCTION):
			if not self.funcname():
				raise ParsingError()
				return False
			if not self.funcbody():
				raise ParsingError()
				return False
			return True
		elif self.accept(TokenEnum.KW_LOCAL):
			if self.accept(TokenEnum.KW_FUNCTION):
				self.expect(TokenEnum.NAME)
				if not self.funcbody():
					raise ParsingError()
					return False
				return True
			elif self.namelist():
				if self.accept(TokenEnum.OP_ASSIGN):
					if not self.explist():
						raise ParsingError()
						return False
				return True
		return False

	def retstat(self):
		if self.accept(TokenEnum.KW_RETURN):
			self.explist()
			self.accept(TokenEnum.SEMICOLON)
			return True
		return False

	def label(self):
		if self.accept(TokenEnum.DOUBLE_COLON):
			self.expect(TokenEnum.NAME)
			self.expect(TokenEnum.DOUBLE_COLON)
			return True
		return False

	def funcname(self):
		if self.accept(TokenEnum.NAME):
			while self.accept(TokenEnum.DOT):
				self.expect(TokenEnum.NAME)
			if self.accept(TokenEnum.COLON):
				self.expect(TokenEnum.NAME)
			return True
		return False

	def varlist(self):
		if self.var():
			while self.accept(TokenEnum.COMMA):
				if not self.var():
					raise ParsingError()
					return False
			return True
		return False

	def var(self):
		if self.accept(TokenEnum.NAME):
			return True
		elif self.prefixexp():
			if self.accept(TokenEnum.LEFT_BRACKET):
				if not self.exp():
					raise ParsingError()
					return False
				self.expect(TokenEnum.RIGHT_BRACKET)
				return True
			elif self.accept(TokenEnum.DOT):
				self.expect(TokenEnum.NAME)
				return True
			return False
		return False

	def namelist(self):
		if self.accept(TokenEnum.NAME):
			while self.accept(TokenEnum.COMMA):
				self.expect(TokenEnum.NAME)
			return True
		return False

	def explist(self):
		if self.exp():
			while self.accept(TokenEnum.COMMA):
				if not self.exp():
					raise ParsingError()
					return False
			return True
		return False

	def exp(self):
		if self.accept(TokenEnum.KW_NIL):
			return True
		elif self.accept(TokenEnum.KW_FALSE):
			return True
		elif self.accept(TokenEnum.KW_TRUE):
			return True
		elif self.accept(TokenEnum.NUMBER):
			return True
		elif self.accept(TokenEnum.TRIPLE_DOT):
			return True
		elif self.functiondef():
			return True
		elif self.prefixexp():
			return True
		elif self.tableconstructor():
			return True	
		elif self.exp():
			if not self.binop():
				raise ParsingError()
				return False
			if not self.exp():
				raise ParsingError()
				return False
			return True
		elif self.unop():
			return True
		return False

	def prefixexp(self):
		if self.var():
			return True
		elif self.functioncall():
			return True
		elif self.accept(TokenEnum.LEFT_PARENTHESIS):
			if not self.exp():
				raise ParsingError()
				return False
			self.expect(TokenEnum.RIGHT_PARENTHESIS)
			return True
		return False

	def functioncall(self):
		if self.prefixexp():
			if self.accept(TokenEnum.COLON):
				self.expect(TokenEnum.NAME)
				if not self.args():
					raise ParsingError()
					return False
				return True
			elif self.args():
				return True
		return False


	def args(self):
		if self.accept(TokenEnum.LEFT_PARENTHESIS):
			self.explist()
			self.expect(TokenEnum.RIGHT_PARENTHESIS)
			return True
		elif self.tableconstructor():
			return True
		elif self.accept(TokenEnum.STRING):
			return True
		return False

	def functiondef(self):
		if self.accept(TokenEnum.KW_FUNCTION):
			if not self.funcbody():
				raise ParsingError()
				return False
			return True
		return False

	def funcbody(self):
		if self.accept(TokenEnum.LEFT_PARENTHESIS):
			self.parlist()
			self.expect(TokenEnum.RIGHT_PARENTHESIS)
			if not self.block():
				raise ParsingError()
				return False
			self.expect(TokenEnum.KW_END)
			return True
		return False

	def parlist(self):
		if self.namelist():
			if self.accept(TokenEnum.COMMA):
				self.expect(TokenEnum.TRIPLE_DOT)
			return True
		elif self.accept(TokenEnum.TRIPLE_DOT)
			return True
		return False

	def tableconstructor(self):
		if self.accept(TokenEnum.LEFT_CURLY_BRACE):
			self.fieldlist()
			self.expect(TokenEnum.RIGHT_CURLY_BRACE)
			return True
		return False

	def fieldlist(self):
		if self.field():
			while self.fieldsep():
				if not self.field():
					raise ParsingError()
					return False
			self.fieldsep()
			return True
		return False

	def field(self):
		if self.accept(TokenEnum.LEFT_BRACKET):
			if not self.exp():
				raise ParsingError()
				return False
			self.expect(TokenEnum.RIGHT_BRACKET):
			self.expect(TokenEnum.OP_ASSIGN)
			if not self.exp():
				raise ParsingError()
				return False
			return True
		elif self.accept(TokenEnum.NAME):
			self.expect(TokenEnum.OP_ASSIGN)
			if not self.exp():
				raise ParsingError()
				return False
			return True
		elif self.exp():
			return True
		return False

	def fieldsep(self):
		if self.accept(TokenEnum.COMMA):
			return True
		elif self.accept(TokenEnum.SEMICOLON):
			return True
		return False

	def binop(self):
		if self.accept(TokenEnum.OP_ADD):
			return True
		elif self.accept(TokenEnum.OP_SUB):
			return True
		elif self.accept(TokenEnum.OP_MUL):
			return True
		elif self.accept(TokenEnum.OP_DIV):
			return True
		elif self.accept(TokenEnum.OP_IDIV):
			return True
		elif self.accept(TokenEnum.OP_POW):
			return True
		elif self.accept(TokenEnum.OP_MOD):
			return True
		elif self.accept(TokenEnum.OP_BIT_AND):
			return True
		elif self.accept(TokenEnum.OP_BIT_NOT_XOR):
			return True
		elif self.accept(TokenEnum.OP_BIT_OR):
			return True
		elif self.accept(TokenEnum.OP_BIT_LSHIFT):
			return True
		elif self.accept(TokenEnum.OP_BIT_RSHIFT):
			return True
		elif self.accept(TokenEnum.OP_CONCAT):
			return True
		elif self.accept(TokenEnum.OP_LESS):
			return True
		elif self.accept(TokenEnum.OP_LESS_THAN_OR_EQUAL):
			return True
		elif self.accept(TokenEnum.OP_GREATER):
			return True
		elif self.accept(TokenEnum.OP_GREATER_THAN_OR_EQUAL):
			return True
		elif self.accept(TokenEnum.OP_EQUAL):
			return True
		elif self.accept(TokenEnum.OP_NOT_EQUAL):
			return True
		elif self.accept(TokenEnum.KW_AND):
			return True
		elif self.accept(TokenEnum.KW_OR):
			return True
		return False

	def unop(self):
		if self.accept(TokenEnum.OP_SUB):
			return True
		elif self.accept(TokenEnum.KW_NOT):
			return True
		elif self.accept(TokenEnum.OP_LEN):
			return True
		elif self.accept(TokenEnum.OP_BIT_NOT_XOR):
			return True
		return False