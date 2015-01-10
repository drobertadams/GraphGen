import logging
import sys
import unittest

from PGC.Generator import Generator
from PGC.Graph.Graph import Graph
from PGC.Production import Production
from PGC.Graph.Vertex import Vertex

# TODO: Test Call Graph
# applyProductions
#   findMatchingProductions
#   _applyProduction

class TestGenerator(unittest.TestCase):

    #--------------------------------------------------------------------------
    def XXXtestFindMatchingProductions(self):
        # Build a basic A->B, A->C graph.
        g = Graph()
        g.addEdge(Vertex('v1', 'A'), Vertex('v2', 'B'))
        g.addEdge('v1', Vertex('v3', 'C'))

        gen = Generator()

        # Providing no productions should result in no productions.
        self.assertEquals( len(gen._findMatchingProductions(g, [])), 0)

        # One matching production, a simple vertex "A".
        lhs = Graph()
        lhs.addVertex(Vertex('u1', 'A'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        matchingProductions = gen._findMatchingProductions(g, [p1])
        self.assertEquals( len(matchingProductions), 1 )

        # Two matching productions.
        p2 = Production(lhs, rhs)
        self.assertEquals( len(gen._findMatchingProductions(g, [p1, p2])), 2)
        
    #--------------------------------------------------------------------------
# TODO
    def XXXtestApplyProductions(self):
        # Test applyProductions(self, startGraph, productions, config):
        self.assertTrue(True)

   #--------------------------------------------------------------------------
    def XXXtestApplyProduction_NoChange(self):
        # Check that if no changes are specified, no changes are made.

        # Basic graph with one vertex A.
        graph = Graph()
        graph.addVertex(Vertex('v1', 'A'))

        # Simple production A ==> A.
        lhs = Graph()
        lhs.addVertex(Vertex('u1', 'A'))
        rhs = Graph()
        rhs.addVertex(Vertex('u1', 'A'))
        production = Production(lhs, rhs)
        
        lhsMapping = {'u1':'v1'}
        rhsMapping = {'u1':'v1'}

        # Applying the production should produce no change.
        gen = Generator()
        gen._applyProduction(graph, production, lhsMapping)
        self.assertEquals(graph.numVertices, 1)
        
    #--------------------------------------------------------------------------
# TODO
    def XXXtestApplyProduction(self):
        # Test complex change: add/delete edges, add/delete vertices.

        self.assertTrue(True)
 
    #--------------------------------------------------------------------------
    def XXXtestAddNewEdges(self):
        # Test that productions can add edges.

        # Basic graph with two unconnected vertices A and B.
        graph = Graph()
        graph.addVertex(Vertex('v0', 'A'))
        graph.addVertex(Vertex('v1', 'B'))
        self.assertEquals(graph.numVertices, 2)

        # Simple production A ==> A->B
        lhs = Graph()
        lhs.addVertex(Vertex('u0', 'A'))
        rhs = Graph()
        rhs.addEdge(Vertex('u0', 'A'), Vertex('u1', 'B'))
        production = Production(lhs, rhs)
        
        rhsMapping = {'u0':'v0', 'u1':'v1'} # normally created by Generator._mapRHSToGraph()

        # Production should have increased the number of edges.
        gen = Generator()
        rhsMapping = gen._addNewEdges(graph, production, rhsMapping)
        self.assertEquals(len(graph._edges), 1)
        self.assertEquals(graph._edges['v0'][0].id, 'v1') # new edge between A and B

    #--------------------------------------------------------------------------
    def XXXtestAddNewVertices(self):
        # Test that productions can add vertices.

        # Basic graph with one vertex A.
        graph = Graph()
        graph.addVertex(Vertex('v0', 'A'))
        self.assertEquals(graph.numVertices, 1)

        # Simple production A ==> A->B
        lhs = Graph()
        lhs.addVertex(Vertex('u0', 'A'))
        rhs = Graph()
        rhs.addEdge(Vertex('u0', 'A'), Vertex('u1', 'B'))
        production = Production(lhs, rhs)
        
        lhsMapping = {'u0':'v0'} # normally created by Graph.search()
        rhsMapping = {'u0':'v0'} # normally created by Generator._mapRHSToGraph()

        # Production should have increased the number of vertices.
        gen = Generator()
        gen._addNewVertices(graph, production, lhsMapping, rhsMapping)
        self.assertEquals(graph.numVertices, 2)
        self.assertEquals(rhsMapping['u0'], 'v0') # rhs u0 mapped to graph v0
        self.assertEquals(rhsMapping['u1'], 'v1') # rhs u1 mapped to graph v1

    #--------------------------------------------------------------------------
    def XXXtestDeleteMissingEdges(self):
        # Test deleteMissingEdges(graph, production, lhsMapping, rhsMapping)

        # Build a graph A->B, A->C.
        graph = Graph()
        graph.addEdge(Vertex('v0', 'A'), Vertex('v1', 'B'))
        graph.addEdge('v0', Vertex('v2', 'C'))
   
        # Simple production A->B ==> A,B (edge between A and B is missing)
        lhs = Graph()
        lhs.addEdge(Vertex('u0', 'A'), Vertex('u1', 'B'))
        rhs = Graph()
        rhs.addVertex(Vertex('u0', 'A'))
        rhs.addVertex(Vertex('u1', 'B'))
        production = Production(lhs, rhs)
        
        lhsMapping = {'u0':'v0','u1':'v1'} # normally created by Graph.search()
        rhsMapping = {'u0':'v0','u1':'v1'} # normally created by Generator._mapRHSToGraph()

        self.assertTrue(graph.hasEdgeBetween('v0','v1')) # A points to B
        gen = Generator()
        gen._deleteMissingEdges(graph, production, lhsMapping, rhsMapping)
        self.assertFalse(graph.hasEdgeBetween('v0','v1')) # A no longer points to B
        
    #--------------------------------------------------------------------------
    def XXXtestDeleteMissingVertices(self):
        # Test deleteMissingVertices(graph, production, lhsMapping)

        # Build a graph A->B
        graph = Graph()
        graph.addEdge(Vertex('v0', 'A'), Vertex('v1', 'B'))
   
        # Simple production A->B ==> A
        lhs = Graph()
        lhs.addEdge(Vertex('u0', 'A'), Vertex('u1', 'B'))
        rhs = Graph()
        rhs.addVertex(Vertex('u0', 'A'))
        production = Production(lhs, rhs)
        
        lhsMapping = {'u0':'v0','u1':'v1'}  # normally created by Graph.search()

        self.assertEqual(len(graph.vertices), 2)
        gen = Generator()
        gen._deleteMissingVertices(graph, production, lhsMapping)
        self.assertEqual(len(graph.vertices), 1)
        self.assertTrue('v1' not in graph.vertices)

    #--------------------------------------------------------------------------
    def XXXtestMapRHSToGraph(self):
        # Test def _mapRHSToGraph(self, graph, production, lhsMapping):

        # Basic graph with one vertex A.
        graph = Graph()
        graph.addVertex(Vertex('v0', 'A'))
        self.assertEquals(graph.numVertices, 1)

        # Simple production A ==> A->B
        lhs = Graph()
        lhs.addVertex(Vertex('u0', 'A'))
        rhs = Graph()
        rhs.addEdge(Vertex('u0', 'A'), Vertex('u1', 'B'))
        production = Production(lhs, rhs)
        
        lhsMapping = {'u0':'v0'} # normally created by Graph.search()

        # Production should have increased the number of vertices.
        gen = Generator()
        rhsMapping = gen._mapRHSToGraph(graph, production, lhsMapping)
        self.assertEquals(len(rhsMapping), 1)
        self.assertEquals(rhsMapping['u0'], 'v0') # rhs u0 mapped to graph v0

# debug, info, warning, error and critical
if __name__ == '__main__':
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
	unittest.main()
