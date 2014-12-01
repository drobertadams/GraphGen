import unittest

from PGC.Lexer import Lexer
from PGC.Parser import Parser
from PGC.Graph import Graph

#------------------------------------------------------------------------------
class TestParser(unittest.TestCase):

	def testEmptyString(self):
		# An empty string shouldn't generate an error.
		l = Lexer("")
		p = Parser(l)
		self.assertTrue(True)

	def testParse(self):
		# An overall parser sanity check.
		p = Parser(Lexer("""
			# Sample Productions File

			configuration {
					max_states = 10;
					min_states = foo;
			}

			productions {
			    # Start state
			    A;     

			    # Productions
			    A ==> A -> B;
			    A -> B ==> A -> B, A -> C;
			    A -> C ==> C -> A;
			}
        """))
		p.parse()
		self.assertEquals(len(p.config), 2)
		self.assertTrue(p.startGraph is not None)
		self.assertEquals(len(p.productions), 3)

	def testParseConfig(self):
		"""config -> ID '=' (ID | NUMBER)"""

		# Left off first ID.
		l = Lexer('= 123;')
		p = Parser(l)
		self.assertRaises(SyntaxError, p._parseConfig)

		# Left off '='
		l = Lexer('A 123;')
		p = Parser(l)
		self.assertRaises(SyntaxError, p._parseConfig)

		# Left off right-hand side.
		l = Lexer('A = ;')
		p = Parser(l)
		self.assertRaises(SyntaxError, p._parseConfig)

		# Simple ID=ID.
		l = Lexer('A = B')
		p = Parser(l)
		p._parseConfig()
		self.assertTrue('A' in p.config)
		self.assertEquals(p.config['A'], 'B')

		# Simple ID=NUMBER.
		l = Lexer('C = 123')
		p = Parser(l)
		p._parseConfig()
		self.assertTrue('C' in p.config)
		self.assertEquals(p.config['C'], '123')

	def testParseConfigList(self):
		"""config_list -> config ';' config_list | nil"""

		# Leaving off a semicolon.
		l = Lexer('A = B C = 123;')
		p = Parser(l)
		self.assertRaises(SyntaxError, p._parseConfigList)

		# Simple valid example.
		l = Lexer('A = B; C = 123;')
		p = Parser(l)
		p._parseConfigList()
		self.assertEquals(len(p.config), 2)

	def testParseConfiguration(self):
		"""configuration -> 'configuration' '{' config_list '}'"""

		# Left off 'configuration'
		l = Lexer('{ A = B; }')
		p = Parser(l)
		self.assertRaises(SyntaxError, p._parseConfiguration)

		# Left off '{'
		l = Lexer('configuration A = B; }')
		p = Parser(l)
		self.assertRaises(SyntaxError, p._parseConfiguration)

		# Left off config list.
		l = Lexer('configuration { }')
		p = Parser(l)
		p._parseConfiguration()
		self.assertTrue(True)

		# Left off '}'
		l = Lexer('configuration { A = B;')
		p = Parser(l)
		self.assertRaises(SyntaxError, p._parseConfiguration)

		# Simple valid configuration.
		l = Lexer('configuration { A = B; }')
		p = Parser(l)
		self.assertTrue(True)

	def testParseProd(self):
		"""prod -> state_list '==>' state_list"""

		# Forgot double arrow.
		p = Parser(Lexer('A->B C->D'))
		self.assertRaises(SyntaxError, p._parseProduction)

		# Simple test.
		p = Parser(Lexer('A->B ==> C->D'))
		p._parseProduction()
		self.assertEquals(len(p.productions), 1)

	def testParseProdList(self):
		"""prod_list -> prod ';' prod_list | nil"""

		# Basic test.
		p = Parser(Lexer('A->B ==> C->D;'))
		p._parseProductionList()
		self.assertEquals(len(p.productions), 1)

		# Forgot the ;
		p = Parser(Lexer('A->B ==> C->D'))
		self.assertRaises(SyntaxError, p._parseProductionList)

		# Multiple productions test.
		p = Parser(Lexer('A->B ==> C->D; E->F ==> G->H;'))
		p._parseProductionList()
		self.assertEquals(len(p.productions), 2)

	def testParseProductions(self):
		"""'productions' '{' start_graph prod_list '}'"""

		# Basic test.
		p = Parser(Lexer('productions { A; A->B ==> C->D; }'))
		p._parseProductionuctions()
		self.assertTrue(p.startGraph is not None)
		self.assertEquals(len(p.productions), 1)

		# Forgot 'productions'
		p = Parser(Lexer(' { A->B ==> C->D; }'))
		self.assertRaises(SyntaxError, p._parseProductionuctions)

		# Forgot '{'
		p = Parser(Lexer('productions A->B ==> C->D; }'))
		self.assertRaises(SyntaxError, p._parseProductionuctions)

		# Forgot start state.
		p = Parser(Lexer('productions { A->B ==> C->D; }'))
		self.assertRaises(SyntaxError, p._parseProductionuctions)

		# Forgot '}'
		p = Parser(Lexer('productions { A->B ==> C->D;'))
		self.assertRaises(SyntaxError, p._parseProductionuctions)

	def testSimpleGraph(self):
		"""graph -> edge_list | edge_list ',' graph"""

		# Simple transition.
		p = Parser(Lexer('A->B'))
		p._parseGraph()
		self.assertTrue(True) # it didn't crash

	def testComplexGraph(self):
		"""graph -> edge_list | edge_list ',' graph"""

		p = Parser(Lexer('A->B,A->C'))
		g = p._parseGraph()

		a = g.findVertexWithLabel('A')
		b = g.findVertexWithLabel('B')
		c = g.findVertexWithLabel('C')
		self.assertTrue(a.id in g._edges)
		self.assertEquals(len(g._edges[a.id]), 2)
		self.assertEquals(g._edges[a.id][0].id, b.id)
		self.assertEquals(g._edges[a.id][1].id, c.id)

	def testParseEdgeList(self):
		"""edgeList -> ID | ID '->' edgeList."""

		# Left off first ID.
		p = Parser(Lexer('->'))
		g = Graph()
		self.assertRaises(SyntaxError, p._parseEdgeList, g)

		# Left off second ID.
		p = Parser(Lexer('A ->'))
		g = Graph()
		self.assertRaises(SyntaxError, p._parseEdgeList, g)

		# Simple label.
		p = Parser(Lexer('A'))
		g = Graph()
		p._parseEdgeList(g)
		self.assertEquals(len(g.vertices), 1)
		a = g.findVertexWithLabel('A')
		self.assertTrue(a is not None)

		# Simple transition.
		p = Parser(Lexer('A -> B'))
		g = Graph()
		p._parseEdgeList(g)
		self.assertEquals(len(g.vertices), 2)
		a = g.findVertexWithLabel('A')
		self.assertTrue(a is not None)
		b = g.findVertexWithLabel('B')
		self.assertTrue(b is not None)
		self.assertEquals('B', g._edges[a.id][0].label)

if __name__ == '__main__':
    unittest.main()
