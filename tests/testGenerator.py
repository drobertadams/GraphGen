import copy
import logging
import sys
import unittest

from PGC.Generator import Generator
from PGC.Graph.Graph import Graph
from PGC.Production import Production
from PGC.Graph.Vertex import Vertex

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
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
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
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
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
        lhs.addVertex(Vertex('l1', 'A'))
        rhs.addVertex(Vertex('r1', 'A'))
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, {})
        self.assertEqual(len(g._vertices), 0)

        # rhs has one new vertex not in the lhs.
        rhsMapping = {}
        rhs.addVertex(Vertex('r2', 'B'))
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, rhsMapping)
        self.assertEqual(len(g._vertices), 1)
        self.assertIn('v0', g._vertices)               # new vertex is v0
        self.assertEqual(g._vertices['v0'].label, 'B') # with label B
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
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'B'))

        # Production rhs transforma that to A->C.
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'C'))
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
        self.assertEqual(str(g), '[v2 g1 g0 ] <g0,A>-><v2,B>, ')

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
        g.addVertex(Vertex('g0', 'A'))
        c = {'min_vertices':3}
        # Production is A ==> A->B
        lhs = Graph()
        lhs.addVertex(Vertex('l0', 'A'))
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
        p = Production(lhs, rhs)
        gen.applyProductions(g, [p], c)
        logging.debug(g)
        self.assertEqual(len(g._vertices), 3)

    #--------------------------------------------------------------------------
    def testDeleteMissingEdges(self):
        # If lhs has no edges, then there's nothing missing from the rhs.
        # Nothing is done to the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
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
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'B'))
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
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
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'B'))
        rhs = Graph()
        rhs.addVertex(Vertex('r0', 'C'))
        rhs.addVertex(Vertex('r1', 'B'))
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
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'B'))
        rhs = Graph()
        rhs.addVertex(Vertex('r0', 'A'))
        rhs.addVertex(Vertex('r1', 'C'))
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
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'B'))
        rhs = Graph()
        rhs.addVertex(Vertex('r0', 'A'))
        rhs.addVertex(Vertex('r1', 'B'))
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
        gcopy = copy.deepcopy(g)
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs, rhs)
        gen = Generator()
        gen._deleteMissingVertices(g, p, {})
        self.assertEqual(g.__dict__, gcopy.__dict__)

        # lhs has vertices, but they all appear in the rhs. Nothing done.
        lhs.addVertex(Vertex('l0', 'A'))
        rhs.addVertex(Vertex('r0', 'A'))
        gen._deleteMissingVertices(g, p, {})
        self.assertEqual(g.__dict__, gcopy.__dict__)

        # lhs has vertices that don't appear in the rhs. They should be
        # deleted from g.
        g.addVertex(Vertex('g0', 'A'))
        rhs = Graph()
        p = Production(lhs, rhs)
        gen._deleteMissingVertices(g, p, {'l0':'g0'})
        self.assertEqual(len(g._vertices), 0)
        self.assertEqual(len(g._edges), 0)
        self.assertEqual(len(g._neighbors), 0)

    #--------------------------------------------------------------------------
    def testFindMatchingProductions(self):
        # Providing no productions should result in no matches.
        gen = Generator()
        g = Graph()
        self.assertEquals( len(gen._findMatchingProductions(g, [])), 0)        
        
        # We have a production, but the LHS can't be found in the graph.
        # No solutions.
        g = Graph()
        g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('v1', 'C'), Vertex('v1', 'D'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        gen = Generator()
        self.assertEquals( len(gen._findMatchingProductions(g, [p1])), 0)        

        # One matching production, a simple vertex "A".
        g = Graph()
        g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
        lhs = Graph()
        lhs.addVertex(Vertex('u1', 'A'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        self.assertEquals( len(gen._findMatchingProductions(g, [p1])), 1)

        # Two matching productions.
        g = Graph()
        g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
        lhs = Graph()
        lhs.addVertex(Vertex('u1', 'A'))
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
        rhs.addVertex(Vertex('r1', 'A'))
        rhsMapping = gen._mapRHSToGraph(g, p, {})
        self.assertEqual(len(rhsMapping), 0)

        # rhs vertex r1 also appears in lhs as l1, which is mapped to g1. 
        # r1 should appear in rhsMapping mapped to g1.
        lhs.addVertex(Vertex('l1', 'A'))
        rhsMapping = gen._mapRHSToGraph(g, p, {'l1':'g1'})
        self.assertEqual(len(rhsMapping), 1)
        self.assertIn('r1', rhsMapping)
        self.assertEqual(rhsMapping['r1'], 'g1')
 
# debug, info, warning, error and critical
if __name__ == '__main__':
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
	unittest.main()
# vim:nowrap
