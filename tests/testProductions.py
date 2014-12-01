#!/usr/bin/env python
#
# Tests for the Productions class.

import unittest
from PGC.Productions import Productions

class TestProductions(unittest.TestCase):

	def testAddProduction(self):
		p = Productions()
		p.addProduction('left', 'right')
		self.assertEquals(len(p.productions), 1)
		self.assertEquals(p.productions[0]['lhs'], 'left')
		self.assertEquals(p.productions[0]['rhs'], 'right')

	def testConstructor(self):
		# Constructor should create an empty productions.
		p = Productions()
		self.assertEquals(len(p.productions), 0)

if __name__ == '__main__':
    unittest.main()