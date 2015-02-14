import unittest

from Lexer import Lexer
from Token import Token
from Token import TokenTypes
from Parser import Parser
from YapyGraph.Graph import Graph
from YapyGraph.Graph import Vertex

#------------------------------------------------------------------------------
class TestParser(unittest.TestCase):

    def testConstructor(self):
        l = Lexer('')
        p = Parser(l)
        self.assertEqual(p.lexer, l)
        self.assertEqual(len(p.config), 0)
        self.assertEqual(len(p.productions), 0)
        self.assertIsNone(p.startGraph)
        self.assertEqual(p._numVerticesParsed, 0)

    def testConsume(self):
        p = Parser( Lexer('{ }') )
        p._consume()
        self.assertEqual(p.lookahead.type, TokenTypes.RBRACE)

    def testError(self):
        p = Parser( Lexer("") )
        self.assertRaises(SyntaxError, p._error, 'foo')

    def testMatch(self):
        p = Parser( Lexer('{ }') )

        # Matching a token returns it.
        token = p._match(TokenTypes.LBRACE)
        self.assertEqual(token.type, TokenTypes.LBRACE)
        self.assertEqual(p.lookahead.type, TokenTypes.RBRACE)
        
        # Not finding a match raises an error.
        self.assertRaises(SyntaxError, p._match, TokenTypes.SEMICOLON)

    def testParse(self):
        # An overall parser sanity check.
        p = Parser(Lexer("""
            # Sample Productions File

            configuration {
                max_states = 10;
                min_states = foo;
            }

            productions {
                A;  # start state

                # Productions
                A ==> A -> B;
                A -> B ==> A -> B, A -> C;
                A -> C ==> C -> A;
            }
"""))
        p.parse()
        self.assertEquals(len(p.config), 2)
        self.assertIsNotNone(p.startGraph)
        self.assertEquals(len(p.productions), 3)

    def testParseConfig(self):
        # config -> ID '=' (ID | NUMBER)

        # Missing first ID raises an error.
        l = Lexer('= 123;')
        p = Parser(l)
        self.assertRaises(SyntaxError, p._parseConfig)

        # Missing '=' raises an error.
        l = Lexer('A 123;')
        p = Parser(l)
        self.assertRaises(SyntaxError, p._parseConfig)

        # Missing right-hand side raises an error.
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
        # config_list -> config ';' config_list | nil

        # Empty input is valid.
        p = Parser( Lexer('') )
        p._parseConfigList()
        self.assertEqual(len(p.config), 0)

        # Simple valid example.
        l = Lexer('A = B; C = 123;')
        p = Parser(l)
        p._parseConfigList()
        self.assertEquals(len(p.config), 2)

        # Leaving off a semicolon raises an error.
        l = Lexer('A = B C = 123;')
        p = Parser(l)
        self.assertRaises(SyntaxError, p._parseConfigList)

    def testParseConfiguration(self):
        # configuration -> 'configuration' '{' config_list '}'

        # Missing 'configuration' raises an error.
        l = Lexer('{ A = B; }')
        p = Parser(l)
        self.assertRaises(SyntaxError, p._parseConfiguration)

        # Left off '{' raises an error.
        l = Lexer('configuration A = B; }')
        p = Parser(l)
        self.assertRaises(SyntaxError, p._parseConfiguration)

        # Left off '}' raises an error.
        l = Lexer('configuration { A = B;')
        p = Parser(l)
        self.assertRaises(SyntaxError, p._parseConfiguration)

        # Left off config list is completely valid.
        l = Lexer('configuration { }')
        p = Parser(l)
        p._parseConfiguration()
        self.assertEqual(len(p.config), 0)

        # Simple valid configuration.
        l = Lexer('configuration { A = B; }')
        p = Parser(l)
        p._parseConfiguration()
        self.assertEquals(p.config['A'], 'B')

    def testParseEdgeList(self):
        # edgeList -> ID | ID '->' edgeList

        # Left off first required ID.
        p = Parser(Lexer(''))
        g = Graph()
        self.assertRaises(SyntaxError, p._parseEdgeList, g)

        # Using non-existing label should create a new vertex.
        g = Graph()
        p = Parser( Lexer('A') )
        p._parseEdgeList(g)
        self.assertEqual(g._vertices['v0'].label, 'A')

        # Using an existing label should not create a new vertex.
        g = Graph()
        g.addVertex( Vertex('u0', 'A') )
        p = Parser( Lexer('A') )
        p._parseEdgeList(g)
        self.assertEqual(g._vertices['u0'].label, 'A')

        # Left off second ID.
        p = Parser(Lexer('A ->'))
        g = Graph()
        self.assertRaises(SyntaxError, p._parseEdgeList, g)

        # Simple transition should create two vertices and connect them.
        g = Graph()
        p = Parser(Lexer('A -> B'))
        p._parseEdgeList(g)
        self.assertEquals(len(g._vertices), 2)
        self.assertEquals(g._vertices['v0'].label, 'A')
        self.assertEquals(g._vertices['v1'].label, 'B')
        self.assertEquals(g._edges['v0'][0].label, 'B')

    def testParseGraph(self):
        # graph -> edge_list | edge_list ',' graph"""

        # Single edgeList.
        p = Parser( Lexer('A->B') )
        g = p._parseGraph()
        self.assertEquals(len(g._vertices), 2)

        # Two edgeLists.
        p = Parser( Lexer('A->B,A->C') )
        g = p._parseGraph()
        self.assertEquals(len(g._vertices), 3)
        # A will be v0, B will be v1, and C will be v2.
        self.assertEquals(g._edges['v0'][0].id, 'v1') # A points to B
        self.assertEquals(g._edges['v0'][1].id, 'v2') # A points to C

    def testParseProduction(self):
        # production -> graph '==>' graph

        # Forgot double arrow is an error.
        p = Parser( Lexer('A->B C->D') )
        self.assertRaises(SyntaxError, p._parseProduction)

        # Simple test.
        p = Parser( Lexer('A->B ==> C->D') )
        p._parseProduction()
        self.assertEquals(len(p.productions), 1)
        self.assertEquals(len(p.productions[0]._lhs._vertices), 2)
        self.assertEquals(len(p.productions[0]._rhs._vertices), 2)

    def testParseProductionList(self):
        # production_list -> production ';' production_list | nil

        # No production(ID) just doesn't do anything.
        p = Parser( Lexer('->B') )
        p._parseProductionList()
        self.assertEquals(len(p.productions), 0)

        # Forgot the ; is an error.
        p = Parser(Lexer('A->B ==> C->D'))
        self.assertRaises(SyntaxError, p._parseProductionList)

        # One production.
        p = Parser( Lexer('A->B ==> C->D;') )
        p._parseProductionList()
        self.assertEquals(len(p.productions), 1)

        # Multiple productions test.
        p = Parser( Lexer('A->B ==> C->D; E->F ==> G->H;') )
        p._parseProductionList()
        self.assertEquals(len(p.productions), 2)

    def testParseStartGraph(self):
        # start_graph -> graph ';'

        # Forgot the ; is an error.
        p = Parser( Lexer('A->B') )
        self.assertRaises(SyntaxError, p._parseStartGraph)

        # Valid test.
        p = Parser( Lexer('A->B;') )
        p._parseStartGraph()
        self.assertIsNotNone(p.startGraph)

    def testParseProductions(self):
        # 'productions' '{' start_graph prod_list '}'

        # Forgot 'productions'
        p = Parser(Lexer(' { A->B ==> C->D; }'))
        self.assertRaises(SyntaxError, p._parseProductions)

        # Forgot '{'
        p = Parser(Lexer('productions A->B ==> C->D; }'))
        self.assertRaises(SyntaxError, p._parseProductions)

        # Forgot start state.
        p = Parser(Lexer('productions { A->B ==> C->D; }'))
        self.assertRaises(SyntaxError, p._parseProductions)

        # Leaving off productions is not an error.
        p = Parser(Lexer('productions { A->B; }'))
        p._parseProductions()
        self.assertIsNotNone(p.startGraph)
        self.assertEqual(len(p.productions), 0)

        # Forgot '}'
        p = Parser(Lexer('productions { A->B ==> C->D;'))
        self.assertRaises(SyntaxError, p._parseProductions)

        # Basic test.
        p = Parser(Lexer('productions { A; A->B ==> C->D; }'))
        p._parseProductions()
        self.assertIsNotNone(p.startGraph)
        self.assertEquals(len(p.productions), 1)

    def testParseVertexID(self):
        p = Parser(Lexer(''))

        # No text label raises an error.
        g = Graph()
        t = Token(0, '123')
        self.assertRaises(AttributeError, p._parseVertexID, t, g)

        # Only a label - doesn't exist in the graph.
        g = Graph()
        t = Token(0, 'A')
        v = p._parseVertexID(t, g)
        self.assertEqual(v.label, 'A')
        self.assertIsNone(v.number)

        # Label and a number - not in the graph.
        g = Graph()
        t = Token(0, 'A1')
        v = p._parseVertexID(t, g)
        self.assertEqual(v.label, 'A')
        self.assertEqual(v.number, '1')

        # Only a label - already in the graph.
        g = Graph()
        u = Vertex('v1', 'A')
        g.addVertex(u)
        t = Token(0, 'A')
        v = p._parseVertexID(t, g)
        self.assertEqual(v, u)

        # Label and a number - already in the graph.
        g = Graph()
        u = Vertex('v1', 'A', '1')
        g.addVertex(u)
        t = Token(0, 'A1')
        v = p._parseVertexID(t, g)
        self.assertEqual(v, u)


if __name__ == '__main__':
    unittest.main()
