#!/usr/bin/python
#
# Tests for the Lexer class.

import unittest
from Lexer import Lexer
from Token import TokenTypes

class TestLexer(unittest.TestCase):

    def testConstructorEmptyInput(self):
        lex = Lexer("")
        self.assertEqual(lex.c, TokenTypes.EOF)

    def testConstructorNonEmptyInput(self):
        lex = Lexer("hello")
        self.assertEqual(lex.c, 'h')

    def testConsumeLineEnding(self):
        lex = Lexer("\nhello")
        lex._consume() # consume the newline
        self.assertEqual(lex.lineNum, 2) # line has increased
        self.assertEqual(lex.charNum, 1) # charNum as been reset
        self.assertEqual(lex.p, 1) # p has advanced
        self.assertEqual(lex.c, 'h') # c is the next character

    def testConsumeNormal(self):
        lex = Lexer('hello')
        lex._consume() # consume the 'h'
        self.assertEqual(lex.charNum, 2) # charNum has increased
        self.assertEqual(lex.p, 1) # p has advanced
        self.assertEqual(lex.c, 'e') # c is the next character

    def testConsumeNoCharactersLeft(self):
        lex = Lexer('h')
        lex._consume() # consume the 'h'
        self.assertEqual(lex.charNum, 2) # charNum has increased
        self.assertEqual(lex.p, 1) # p has advanced
        self.assertEqual(lex.c, TokenTypes.EOF)

    def testNextTokenEOF(self):
        t = Lexer('').nextToken()
        self.assertEqual(t.type, TokenTypes.EOF)

    def testNextTokenInvalidToken(self):
        lex = Lexer('$')
        self.assertRaises(SyntaxError, lex.nextToken)

    def testNextToken(self):
        # Test all the acceptable tokens.
        lex = Lexer('; , { } -> ==> = 123 configuration productions abc123')
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

        # Test comments
        lex = Lexer("""
            #comment
            abc #comment
            def
            # comment
        """)
        self.assertEquals(lex.nextToken().type, TokenTypes.ID)
        self.assertEquals(lex.nextToken().type, TokenTypes.ID)
        self.assertEquals(lex.nextToken().type, TokenTypes.EOF)


if __name__ == '__main__':
    unittest.main()
