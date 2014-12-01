#!/usr/bin/env python
#
# Represents all of the productions in the input file.

#------------------------------------------------------------------------------
#    ____                _            _   _                 
#   |  _ \ _ __ ___   __| |_   _  ___| |_(_) ___  _ __  ___ 
#   | |_) | '__/ _ \ / _` | | | |/ __| __| |/ _ \| '_ \/ __|
#   |  __/| | | (_) | (_| | |_| | (__| |_| | (_) | | | \__ \
#   |_|   |_|  \___/ \__,_|\__,_|\___|\__|_|\___/|_| |_|___/
#                                                                                               
#                                                           
class Productions(object):

    def __init__(self):
        self.productions = [] # an array of {'lhs', 'rhs'} dictionaries

    def __str__(self):
        """Returns string representation of self."""
        s = ""
        for p in self.productions:
            s = s + str(p['lhs']) + ' ==> ' + str(p['rhs']) + '\n'
        return s

    def addProduction(self, lhs, rhs):
        """Adds the given lhs and rhs to the list of productions. lhs and rhs
           should be PetriNet objects."""
        self.productions.append( {'lhs' : lhs, 'rhs' : rhs } )