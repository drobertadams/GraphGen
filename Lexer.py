from Token import TokenTypes
from Token import Token
                         
class Lexer(object):
    """
    Lexer for the graph productions parser.
    """
    
    def __init__(self, str):
        """Constructor.
           str is the input to the lexer
        """
        self.input = str    # input string
        self.p = 0          # index of current character within self.input
        self.lineNum = 1    # current line number
        self.charNum = 1    # current character number within the line
 
        # Initialize the current character (self.c)
        if len(str) != 0:
            self.c = self.input[self.p]
        else:
            self.c = TokenTypes.EOF
               
    def nextToken(self):
        """Return the next Token in the input stream, ignoring whitespace."""
        while self.c != TokenTypes.EOF:
            if self.c in [' ', '\t', '\n', '\r']:
                self._consume()
            elif self.c == ';':
                self._consume()
                return Token(TokenTypes.SEMICOLON, ';')
            elif self.c == ',':
                self._consume()
                return Token(TokenTypes.COMMA, ',')
            elif self.c == '{':
                self._consume()
                return Token(TokenTypes.LBRACE, '{')
            elif self.c == '}':
                self._consume()
                return Token(TokenTypes.RBRACE, '}')
            elif self.c == '-':
                # '->'' is an ARROW, '-' followed by anything else is invalid.
                self._consume()
                if self.c == '>':
                    self._consume()
                    return Token(TokenTypes.ARROW, '->')
                else:
                    self._error()
            elif self.c == '=':
                # '==>' is a DOUBLEARROW, '==' followed by anything else is
                # invalid. '=' followed by anything but a '=' is simply an
                # EQUALS.
                self._consume()
                if self.c == '=':
                    self._consume()
                    if self.c == '>':
                        self._consume()
                        return Token(TokenTypes.DOUBLEARROW, '==>')
                    else:
                        self._error()
                else:
                    return Token(TokenTypes.EQUALS, '=')
            elif self.c == '#':
                # Consume everything until the end-of-line.
                lexeme = ""
                while self.c != TokenTypes.EOF and self.c != '\n':
                    self._consume()
            elif self.c.isdigit():
                # Consume all contiguous digits and turn them into a NUMBER.
                lexeme = ""
                while self.c != TokenTypes.EOF and self.c.isdigit():
                    lexeme += self.c
                    self._consume()
                return Token(TokenTypes.NUMBER, lexeme)
            elif self.c.isalpha():
                # Consume all contiguous alpha, digits, or _ characters, then check to
                # see if we recognize it as a reserved word.
                lexeme = ""
                while self.c != TokenTypes.EOF and (self.c.isalpha() or self.c.isdigit() or self.c == '_'):
                    lexeme += self.c
                    self._consume()
                if lexeme == 'configuration':
                    t = Token(TokenTypes.CONFIGURATION, lexeme)
                elif lexeme == 'productions':
                    t = Token(TokenTypes.PRODUCTIONS, lexeme)
                else:
                    t = Token(TokenTypes.ID, lexeme)
                return t
            else:
                # Every other character is invalid.
                self._error()
        return Token(TokenTypes.EOF, "<EOF>")

    def _consume(self):
        """Advance to the next character of input, or EOF."""
        # Update line number and character number.
        if self.c in ['\n', '\r']:
            self.lineNum = self.lineNum + 1
            self.charNum = 1
        else:
            self.charNum = self.charNum + 1

        # To to the next character.
        self.p += 1
        if self.p >= len(self.input):
            self.c = TokenTypes.EOF
        else:
            self.c = self.input[self.p]

    def _error(self):
        """Raises an exception indicating that the current character is
           invalid.
        """
        raise SyntaxError("Invalid character %c at [%d,%d]." % \
            (self.c, self.lineNum, self.charNum))
