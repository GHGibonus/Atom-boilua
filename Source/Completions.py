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
	pass

TOKEN_DESCRIPTION = [

]

class ParsingError(Exception):
	def __init__(self):
		pass

class Parser(object):
# Grammar from https://www.lua.org/manual/5.3/manual.html#9
	__slots__ = [
		""
	]
	def __init__(self):
		pass

	def tokenize(self, a_source_code):
		pass

	def parse(self, a_source_code):
		pass

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
		elif self.accept(TokenEnum.TRUE):
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
		elif self.accept(TokenEnum.OP_BIT_NOT):
			return True
		return False