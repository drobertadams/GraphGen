import copy
import logging
import sys
import unittest

from Generator import Generator
from YapyGraph.Graph import Graph
from Production import Production
from YapyGraph.Vertex import Vertex

class TestGenerator(unittest.TestCase):

    #--------------------------------------------------------------------------
    def testAddNewEdges(self):
        # rhs has no edges, so nothing changes.
        g = Graph()
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs,rhs)
        rhsMapping = {}
        gen = Generator()
        self.assertEqual(len(g._edges), 0)
        gen._addNewEdges(g, p, rhsMapping)
        self.assertEqual(len(g._edges), 0)

        # rhs has an edge, but it already exists in the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A', 1), Vertex('r1', 'B', 1))
        p = Production(lhs,rhs)
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._addNewEdges(g, p, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)

        # rhs has a new edge not in graph.
        g = Graph()
        g.addVertex(Vertex('g0', 'A'))
        g.addVertex(Vertex('g1', 'B'))
        lhs = Graph()
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A', 1), Vertex('r1', 'B', 1))
        p = Production(lhs,rhs)
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 0)
        gen._addNewEdges(g, p, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)
        self.assertEqual(g._edges['g0'][0].id, 'g1')

    #--------------------------------------------------------------------------
    def testAddNewVertices(self):
        # Production rhs has no vertices, so nothing done.
        g = Graph()
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs, rhs)
        gen = Generator()
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, {})
        self.assertEqual(len(g._vertices), 0)
        
        # Production rhs has vertices, but they all appear in the LHS. Hence
        # they aren't new and nothing is done.
        lhs.addVertex(Vertex('l1', 'A', 1))
        rhs.addVertex(Vertex('r1', 'A', 1))
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, {})
        self.assertEqual(len(g._vertices), 0)

        # rhs has one new vertex not in the lhs.
        rhsMapping = {}
        rhs.addVertex(Vertex('r2', 'B', 2))
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, rhsMapping)
        self.assertEqual(len(g._vertices), 1)
        self.assertIn('v0', g._vertices)               # new vertex is v0
        self.assertEqual(g._vertices['v0'].label, 'B') # with label B
        self.assertEqual(g._vertices['v0'].number, 2)  # with number 2
        self.assertIn('r2', rhsMapping)                # now appears in rhsMapping
        self.assertEqual(rhsMapping['r2'], 'v0')       # r2 mapped to v0 (the newly added vertex) in graph

    #--------------------------------------------------------------------------
    def testApplyProduction(self):
        # A basic test that tests all four cases: add and remove vertex,
        # and add and remove edge.

        # Graph starts with A->B
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        g1 = g._vertices['g1']

        # Production lhs matches A->B
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A', 1), Vertex('l1', 'B', 1))

        # Production rhs transforms that to A->C
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A', 1), Vertex('r1', 'C'))
        p = Production(lhs,rhs)

        gen = Generator()
        gen._applyProduction(g, p, {'l0':'g0','l1':'g1'})

        # g has a new vertex, <v2,C>.
        self.assertEqual(len(g._vertices), 2)
        self.assertEqual(g._vertices['v1'].label, 'C')

        # <g0,A> points to <v2,C>
        self.assertEqual(len(g._edges['g0']), 1)
        self.assertEqual(g._edges['g0'][0].id, 'v1')
        self.assertEqual(g._vertices['v1'].label, 'C')

        # <g0,A> no longer points to <g1,B>
        self.assertNotIn(g1, g._edges['g0'])

        # Vertex <g1,B> has been deleted.
        self.assertNotIn('g1', g._vertices)

    #--------------------------------------------------------------------------
    def testApplyProduction_Blackbox(self):
        # Black-box test of _applyProduction.

        # Graph is A->C,D
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'C'))
        g.addVertex(Vertex('g2', 'D'))

        # Production is A->C,D ==> A->B,C.
        # This adds vertex B, adds edge from A->B, deletes edge from A->C,
        # and deletes vertex D.
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'C'))
        lhs.addVertex(Vertex('l2', 'D'))
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
        rhs.addVertex(Vertex('r2', 'C'))
        p = Production(lhs, rhs)

        gen = Generator()
        gen._applyProduction(g, p, {'l0':'g0','l1':'g1','l2':'g2'})

        self.assertEqual(len(g._vertices), 3)

        # <g0,A> is still in the graph.
        self.assertIn('g0', g._vertices)
        self.assertEqual(g._vertices['g0'].label, 'A')
        # <v3,B> has been added.
        self.assertIn('v2', g._vertices)
        self.assertEqual(g._vertices['v2'].label, 'B')
        # A->B
        self.assertIn(g._vertices['v2'], g._edges['g0'])
        # <g1,C> is still in the graph.
        self.assertIn('g1', g._vertices)
        self.assertEqual(g._vertices['g1'].label, 'C')
        # A->C has been removed.
        self.assertNotIn(g._vertices['g1'], g._edges['g0'])
        # <g2,D> has been removed.
        self.assertNotIn('g2', g._vertices)

        # Output looks fine.
        self.assertEqual(str(g), 'digraph {\nA_g0->B_v2;\n\n}')

#--------------------------------------------------------------------------
    def testApplyProduction_Blackbox2(self):
        # Another black-box test of _applyProduction this time with
        # numbered vertices.

        # Graph is A0->A1,A0->D
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'A'))
        g.addEdge('g0', Vertex('g2', 'D'))

        # Production is A1->A2 ==> A1->A->A2.
        # This production adds a new vertex "A" between the existing As,
        # leaving the first A still pointing to D.
        # Resulting graph: A1->A3->A2; A1->D
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A', 1), Vertex('l1', 'A', 2))
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A', 1), Vertex('r1', 'A'))
        rhs.addEdge('r1', Vertex('r2', 'A', 2))
        p = Production(lhs, rhs)

        gen = Generator()
        gen._applyProduction(g, p, {'l0':'g0','l1':'g1'})

        # Result has 4 vertices.
        self.assertEqual(len(g._vertices), 4)

        # <g0,A> is still in the graph.
        self.assertIn('g0', g._vertices)
        self.assertEqual(g._vertices['g0'].label, 'A')

        # <v3,A> has been added.
        self.assertIn('v3', g._vertices)
        self.assertEqual(g._vertices['v3'].label, 'A')
        
        # g0->v3
        self.assertIn(g._vertices['v3'], g._edges['g0'])

        # <g1,A> is still in the graph.
        self.assertIn('g1', g._vertices)
        self.assertEqual(g._vertices['g1'].label, 'A')

        # <g2,D> is still in the graph.
        self.assertIn('g2', g._vertices)
        self.assertEqual(g._vertices['g2'].label, 'D')

        # <g0,A>-><g2,D>
        self.assertIn(g._vertices['g2'], g._edges['g0'])

        # g0->v3
        self.assertIn(g._vertices['v3'], g._edges['g0'])

        # Output looks fine: A1->A->A, A1->D
        self.assertEqual(str(g), 'digraph {\nA_v3->A_g1;\nA_g0->D_g2;\nA_g0->A_v3;\n\n}')

#--------------------------------------------------------------------------
    def testApplyProduction_Blackbox3(self):
        # Another black-box test. This time with a split LHS: A->B,A->C

        input = """
        # Grammar file for testing.

        configuration {
            min_vertices = 4;
        }

        productions {
            # Start graph
            A->B, A->C;

            # Productions
            A->C, A->B ==> A->D->C, A->B;
        }
"""

        gen = Generator()
        f = gen._parseGrammarFile(input)
        logging.debug('start graph is...')
        logging.debug(f.startGraph)

        gen.applyProductions(f.startGraph, f.productions, f.config)

        self.assertEqual(f.startGraph.numVertices, 4)

#--------------------------------------------------------------------------
    def testApplyProduction_Blackbox4(self):
        # More complex black-box test. This time we have several productions
        # in various configurations, and we build a big graph (50 vertices).

        input = """
        configuration {
            min_vertices = 50;
        }

        productions {
            # Start graph
            A->B, A->C;

            # Productions
            A->C, A->B ==> A->D->C, A->B;
            A->D ==> A->D->E;
            D->E ==> D->F->E, D->G;
            G ==> G->A->D;
        }
"""

        gen = Generator()
        f = gen._parseGrammarFile(input)
        logging.debug('start graph is...')
        logging.debug(f.startGraph)

        gen.applyProductions(f.startGraph, f.productions, f.config)

        logging.info(f.startGraph)
        self.assertEqual(f.startGraph.numVertices, 50)

    #--------------------------------------------------------------------------
    def testApplyProductions(self):
        # Start graph already has the minimum number of vertices. Nothing done.
        g = Graph()
        c = {'min_vertices':0}
        gen = Generator()
        gen.applyProductions(g, None, c)
        self.assertEqual(len(g._vertices), 0)

        # No matching productions raises an error.
        c = {'min_vertices':1}
        self.assertRaises(RuntimeError, gen.applyProductions, g, [], c)

        # When we're done, g has more at least min_vertices.
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'A'))
        c = {'min_vertices':10}
        # Production is A1->A2 ==> A1->A->A2
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A', 1), Vertex('l1', 'A', 2))
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A', 1), Vertex('r1', 'A'))
        rhs.addEdge('r1', Vertex('r2', 'A', 2))
        p = Production(lhs, rhs)
        gen.applyProductions(g, [p], c)
        logging.debug(g)
        self.assertEqual(len(g._vertices), 10)

    #--------------------------------------------------------------------------
    def testDeleteMissingEdges(self):
        # If lhs has no edges, then there's nothing missing from the rhs.
        # Nothing is done to the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A', 1), Vertex('g1', 'B', 1))
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs,rhs)
        lhsMapping = {}
        rhsMapping = {}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)

        # lhs has an edge, but it also appears on the rhs. Nothing done.
        g = Graph()
        g.addEdge(Vertex('g0', 'A', 1), Vertex('g1', 'B', 1))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A', 1), Vertex('l1', 'B', 1))
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A', 1), Vertex('r1', 'B', 1))
        p = Production(lhs,rhs)
        lhsMapping = {'l0':'g0', 'l1':'g1'}
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)

        # lhs has an edge, but the starting vertex doesn't appear in the RHS.
        # The edge should be deleted from the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A', 1), Vertex('g1', 'B', 1))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A', 1), Vertex('l1', 'B', 1))
        rhs = Graph()
        rhs.addVertex(Vertex('r0', 'A', 2))
        rhs.addVertex(Vertex('r1', 'B', 1))
        p = Production(lhs,rhs)
        lhsMapping = {'l0':'g0', 'l1':'g1'}
        rhsMapping = {'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 0)

        # lhs has an edge, but the ending vertex doesn't appear in the RHS.
        # The edge should be deleted from the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A', 1), Vertex('g1', 'B', 1))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A', 1), Vertex('l1', 'B', 1))
        rhs = Graph()
        rhs.addVertex(Vertex('r0', 'A', 1))
        rhs.addVertex(Vertex('r1', 'B', 2))
        p = Production(lhs,rhs)
        lhsMapping = {'l0':'g0', 'l1':'g1'}
        rhsMapping = {'r0':'g0'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 0)

        # lhs has an edge, but it's gone from the rhs. It should be deleted
        # from the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A', 1), Vertex('g1', 'B', 1))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A', 1), Vertex('l1', 'B', 1))
        rhs = Graph()
        rhs.addVertex(Vertex('r0', 'A', 1))
        rhs.addVertex(Vertex('r1', 'B', 1))
        p = Production(lhs,rhs)
        lhsMapping = {'l0':'g0', 'l1':'g1'}
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 0)

    #--------------------------------------------------------------------------
    def testDeleteMissingVertices(self):
        # lhs has no vertices(!). Nothing done.
        g = Graph()
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs, rhs)
        gen = Generator()
        gen._deleteMissingVertices(g, p, {})
        self.assertEqual(len(g._vertices), 0)

        # lhs has vertices, but they all appear in the rhs. Nothing done.
        g.addVertex(Vertex('g0', 'A', 1))
        lhs.addVertex(Vertex('l0', 'A', 1))
        rhs.addVertex(Vertex('r0', 'A', 1))
        p = Production(lhs, rhs)
        gen._deleteMissingVertices(g, p, {'l0':'g0'})
        self.assertEqual(len(g._vertices), 1)

        # lhs has a vertex (A2) that don't appear in the rhs. It should be
        # deleted from g.
        g.addVertex(Vertex('g1', 'A', 2))
        lhs.addVertex(Vertex('l1', 'A', 2))
        p = Production(lhs, rhs)
        self.assertEqual(len(g._vertices), 2)
        gen._deleteMissingVertices(g, p, {'l0':'g0', 'l1':'g1'})
        self.assertEqual(len(g._vertices), 1)

    #--------------------------------------------------------------------------
    def testFindMatchingProductions(self):
        # Providing no productions should result in no matches.
        gen = Generator()
        g = Graph()
        self.assertEquals( len(gen._findMatchingProductions(g, [])), 0)        
        
        # We have a production, but the LHS can't be found in the graph.
        # No solutions.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('g0', 'C'), Vertex('g1', 'D'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        gen = Generator()
        self.assertEquals( len(gen._findMatchingProductions(g, [p1])), 0)        

        # One matching production, a simple vertex "A".
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addVertex(Vertex('g0', 'A', '1'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        self.assertEquals( len(gen._findMatchingProductions(g, [p1])), 1)

        # Two matching productions.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addVertex(Vertex('g0', 'A', '2'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        p2 = Production(lhs, rhs)
        self.assertEquals( len(gen._findMatchingProductions(g, [p1, p2])), 2)
        
    #--------------------------------------------------------------------------
    def testGenerateFromFile(self):
        gen = Generator()
        g = gen.generateFromFile("tests/sample.txt")
        self.assertEqual(g.numVertices, 10)

    #--------------------------------------------------------------------------
    def testMapRHSToGraph(self):
        # No vertices in rhs. Mapping returned is empty.
        g = Graph()
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs, rhs)
        gen = Generator()
        rhsMapping = gen._mapRHSToGraph(g, p, {})
        self.assertEqual(len(rhsMapping), 0)

        # rhs has vertex r1, but it doesn't appear in the lhs. Mapping returned
        # is empty.
        rhs.addVertex(Vertex('r1', 'A', '1'))
        rhsMapping = gen._mapRHSToGraph(g, p, {})
        self.assertEqual(len(rhsMapping), 0)

        # rhs vertex r1 also appears in lhs as l1, which is mapped to g1. 
        # r1 should appear in rhsMapping mapped to g1.
        lhs.addVertex(Vertex('l1', 'A', '1'))
        rhsMapping = gen._mapRHSToGraph(g, p, {'l1':'g1'})
        self.assertEqual(len(rhsMapping), 1)
        self.assertIn('r1', rhsMapping)
        self.assertEqual(rhsMapping['r1'], 'g1')

# debug, info, warning, error and critical
if __name__ == '__main__':
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
	unittest.main()
# vim:nowrap
