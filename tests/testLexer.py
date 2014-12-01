#!/usr/bin/python
#
# Tests for the Lexer class.

import unittest
from PGC.Lexer import Lexer
from PGC.Token import TokenTypes

class TestLexer(unittest.TestCase):

	def testErrorCase(self):
		# Invalid token should raise a SyntaxError.
		lex = Lexer('$')
		self.assertRaises(SyntaxError, lex.nextToken)

	def testBasicTest(self):
		# Test all the acceptable tokens.
		lex = Lexer('; , { } -> ==> = 123 configuration productions abc')
		self.assertEquals(lex.nextToken().type, TokenTypes.SEMICOLON)
		self.assertEquals(lex.nextToken().type, TokenTypes.COMMA)
		self.assertEquals(lex.nextToken().type, TokenTypes.LBRACE)
		self.assertEquals(lex.nextToken().type, TokenTypes.RBRACE)
		self.assertEquals(lex.nextToken().type, TokenTypes.ARROW)
		self.assertEquals(lex.nextToken().type, TokenTypes.DOUBLEARROW)
		self.assertEquals(lex.nextToken().type, TokenTypes.EQUALS)
		self.assertEquals(lex.nextToken().type, TokenTypes.NUMBER)
		self.assertEquals(lex.nextToken().type, TokenTypes.CONFIGURATION)
		self.assertEquals(lex.nextToken().type, TokenTypes.PRODUCTIONS)
		self.assertEquals(lex.nextToken().type, TokenTypes.ID)
		self.assertEquals(lex.nextToken().type, TokenTypes.EOF)

		# Test with comments
		lex = Lexer("""
			#comment
			abc #comment
			def
			# comment
		""")
		self.assertEquals(lex.nextToken().type, TokenTypes.ID)
		self.assertEquals(lex.nextToken().type, TokenTypes.ID)
		self.assertEquals(lex.nextToken().type, TokenTypes.EOF)

	def testEmptyString(self):
		l = Lexer('')
		t = l.nextToken()
		self.assertEquals(t.type, TokenTypes.EOF)

if __name__ == '__main__':
    unittest.main()