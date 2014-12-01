#!/usr/bin/env python

#------------------------------------------------------------------------------
#    _____     _            _____                      
#   |_   _|__ | | _____ _ _|_   _|   _ _ __   ___  ___ 
#     | |/ _ \| |/ / _ \ '_ \| || | | | '_ \ / _ \/ __|
#     | | (_) |   <  __/ | | | || |_| | |_) |  __/\__ \
#     |_|\___/|_|\_\___|_| |_|_| \__, | .__/ \___||___/
#                                |___/|_|              
class TokenTypes(object):
    """A singleton to represent all token types."""

    (EOF, SEMICOLON, EQUALS, CONFIGURATION, PRODUCTIONS, LBRACE, RBRACE, \
    	DOUBLEARROW, ARROW, ID, NUMBER, COMMA) = range(12)

    names = [ 'EOF', 'SEMICOLON', 'EQUALS', 'CONFIGURATION', 'PRODUCTIONS', 
    	'LBRACE', 'RBRACE', 'DOUBLEARROW', 'ARROW', 'ID', 'NUMBER', 'COMMA' ]
        
#------------------------------------------------------------------------------
#    _____     _              
#   |_   _|__ | | _____ _ __  
#     | |/ _ \| |/ / _ \ '_ \ 
#     | | (_) |   <  __/ | | |
#     |_|\___/|_|\_\___|_| |_|
#                             
class Token(object):
    """An abstract token."""
    
    def __init__(self, type, text):
        """Constructor.
           type is a numeric token type from TokenTypes
           text is the lexeme
        """
        self.type = type
        self.text = text
        
    def __str__(self):
    	"""Converts a token to string."""
        return "<'%s', %s>" % (self.text, TokenTypes.names[self.type])