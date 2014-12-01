import unittest

from PGC.Graph.Graph import Graph
from PGC.Graph.Vertex import Vertex

#------------------------------------------------------------------------------
# Functions to test graph isomorphism searching. The first few functions are
# overall solution finding. The last few methods test specific methods in
# Graph.
class TestGraphSearch(unittest.TestCase):

	def testSearchEmptyQueryGraph(self):
		# Using an empty query graph should result in no solution.
		q = Graph()
		g = Graph()
		solutions = g.search(q)
		self.assertEquals(len(solutions), 0)

 	def testSearchEmptyDataGraph(self):
 		# Using an empty data graph should result in no solution.
 		q = Graph()
 		q.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
 		q.addEdge('u1', Vertex('u3', 'C'))

 		g = Graph()
 		solutions = g.search(q)
 		self.assertEquals(len(solutions), 0)

	def testOneSimpleSolution(self):
		q = Graph()
		q.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
		q.addEdge('u1', Vertex('u3', 'C'))

		# Create an exact replica of the query graph as the data graph. This
		# should result in a solution.
		g = Graph()
		g.addEdge(Vertex('v1', 'A'), Vertex('v2', 'B'))
		g.addEdge('v1', Vertex('v3', 'C'))

		solutions = g.search(q)

		self.assertEquals(len(solutions), 1)
		self.assertEquals(solutions[0]['u1'], 'v1')
		self.assertEquals(solutions[0]['u2'], 'v2')
		self.assertEquals(solutions[0]['u3'], 'v3')

	def testTwoSolutions(self):

		q = Graph()
		q.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
		q.addEdge('u1', Vertex('u3', 'C'))

		# Create an exact replica of the query graph as the data graph. Then
		# create another instance of the A->B,A->C query graph inside the
		# data graph. This should result in two solutions found.
		g = Graph()
		g.addEdge(Vertex('v1', 'A'), Vertex('v2', 'B'))
		g.addEdge('v1', Vertex('v3', 'C'))
		g.addEdge(Vertex('v4', 'A'), 'v3')
		g.addEdge('v4', Vertex('v5', 'B'))

		solutions = g.search(q)

		self.assertEquals(len(solutions), 2)
		self.assertEquals(solutions[1]['u1'], 'v4')
		self.assertEquals(solutions[1]['u2'], 'v5')
		self.assertEquals(solutions[1]['u3'], 'v3')

	def testThreeSolutions(self):

		q = Graph()
		q.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
		q.addEdge('u1', Vertex('u3', 'C'))

		# Create an exact replica of the query graph as the data graph. Then
		# create another instance of the A->B,A->C query graph inside the
		# data graph. Finally, connect v3(C) and v5(B) with a new v6(A). 
		# This should result in three solutions.
		g = Graph()
		g.addEdge(Vertex('v1', 'A'), Vertex('v2', 'B'))
		g.addEdge('v1', Vertex('v3', 'C'))
		g.addEdge(Vertex('v4', 'A'), 'v3')
		g.addEdge('v4', Vertex('v5', 'B'))
		g.addEdge(Vertex('v6', 'A'), 'v3')
		g.addEdge('v6', 'v5')

		solutions = g.search(q)

		self.assertEquals(len(solutions), 3)

	def testFilterCandidates(self):
	    # Filtering an empty graph should return an empty array.
	    g = Graph()
	    v = Vertex('x', 'x')
	    c = g._filterCandidates(v)
	    self.assertTrue(isinstance(c, list))
	    self.assertEquals(len(c), 0)

	    # Build a little graph with two 'A' labeled vertices.
	    g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
	    g.addEdge('u1', Vertex('u3', 'A'))

	    # Search the graph for all 'X' vertices (should return an empty array.)
	    v = Vertex('x', 'X')
	    c = g._filterCandidates(v)
	    self.assertTrue(len(c) == 0)

	    # Search for 'A' vertices. Should return two of them.
	    v = Vertex('x', 'A')
	    c = g._filterCandidates(v)
	    self.assertTrue(len(c) == 2)
	    self.assertTrue(c[0].label == 'A')
	    self.assertTrue(c[1].label == 'A')

	def testFindCandidates(self):
		# Create a query graph.
		q = Graph()
		q.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
		q.addEdge('u1', Vertex('u3', 'C'))

		# Create an empty data graph and make sure we don't find any matches.
		g = Graph()
		self.assertFalse(g._findCandidates(q))

		# Add an vertex for all but C. The test should still fail.
		g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
		self.assertFalse(g._findCandidates(q))

		# Add a vertex for C, and now the test should succeeed.
		g.addEdge('u1', Vertex('u3', 'C'))
		self.assertTrue(g._findCandidates(q))

	def testFindMatchedNeighbors(self): 
		q = Graph()
		# No data should return an empty list.
		n = q._findMatchedNeighbors(None, None)
		self.assertEquals(len(n), 0)

		# No matching neighbors should return an empty list.
		q.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
		q.addEdge('u1', Vertex('u3', 'C'))
		u = q.vertices['u2']
		n = q._findMatchedNeighbors(u, [])
		self.assertEquals(len(n), 0)

		# Make a matching neighbor and make sure it is returned.
		matches = { 'u2':'v1', 'v1':'u2' }
		u = q.vertices['u1']
		n = q._findMatchedNeighbors(u, matches)
		self.assertEquals(len(n), 1)

	def testIsJoinable(self):
		# If u or v is None, then IsJoinable() should return False.
		g = Graph()
		self.assertFalse(g._isJoinable(None, None, None, None))

		# If there are no matched vertices yet (we just started the matching
		# process), then IsJoinable() should return True.
		g = Graph()
		q = Graph()
		u = Vertex('u1')
		v = Vertex('v1')
		self.assertTrue(g._isJoinable(u, v, q, []))

		# Create a query and data graph for some tests.
		q.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
		q.addEdge('u1', Vertex('u3', 'C'))

		g.addEdge(Vertex('v1', 'A'), Vertex('v2', 'B'))
		g.addEdge('v1', Vertex('v3', 'C'))
		g.addEdge('v3', 'v2')
		g.addEdge('v3', Vertex('v4', 'B'))
		g.addEdge('v3', Vertex('v5', 'C'))

		# Match u1 with v1. Then check to see if u2 and v4 are joinable.
		# They are not because there is no edge between v4 and v1 (draw out
		# the graphs on paper and this will make sense).
		matches = { 'u1':'v1', 'v1':'u1' }
		u = q.vertices['u2']
		v = g.vertices['v4']
		self.assertFalse(g._isJoinable(u, v, q, matches))

		# Test if u2 can be matched to v2. It can.
		u = q.vertices['u2']
		v = g.vertices['v2']
		self.assertTrue(g._isJoinable(u, v, q, matches))	    

	def testNextQueryVertex(self):
		matches = {}

		# Build a little graph with three nodes.
		q = Graph()
		q.addEdge(Vertex('u1'), Vertex('u2'))
		q.addEdge('u1', Vertex('u3'))

		# NextQueryVertex() should return either u1, u2, or u3.
		for i in range(3):
		    v = q._nextUnmatchedVertex(matches)
		    self.assertTrue(v.id in ['u1', 'u2', 'u3'])
		    matches[v.id] = 'label'

		# Now that all of the vertices are labeled, NextQueryVertex() should
		# return None.
		v = q._nextUnmatchedVertex(matches)
		self.assertEquals(v, None)

	def testRefineCandidates(self):
		g = Graph()
		# An empty candidate list should return an empty list.
		c = g._refineCandidates([], None, {})
		self.assertEquals(len(c), 0)

		# Test with no matching candidates.
		# Candidates have 0 degree, query vertex has degree > 0.
		c = [ Vertex('u1'), Vertex('u2'), Vertex('u3') ]
		v = Vertex('test')
		v.degree = 2
		c = g._refineCandidates(c, v, {})
		self.assertEquals(len(c), 0)

		# Test where one candidate is removed (u2).
		u1 = Vertex('u1')
		u1.degree = 1
		u2 = Vertex('u2')
		u2.degree = 0
		c = [u1, u2]
		v = Vertex('v')
		v.degree = 1
		c = g._refineCandidates(c, v, {})
		self.assertEquals(len(c), 1)

		# Test that already matching candidate is removed (u2).
		u1 = Vertex('u1')
		u1.degree = 1
		u2 = Vertex('u2')
		u2.degree = 1
		c = [u1, u2]
		v = Vertex('v')
		v.degree = 1
		c = g._refineCandidates(c, v, {'u2':'v1'})
		self.assertEquals(len(c), 1)

	def testRestoreState(self):
		g = Graph()

		matches = {}
		u1 = Vertex('u1')
		v1 = Vertex('v1')
		g._updateState(u1, v1, matches)
		u2 = Vertex('u2')
		v2 = Vertex('v2')
		g._updateState(u2, v2, matches)
		self.assertEquals(len(matches), 2)

		matches = g._restoreState(matches)
		# RestoreState should have removed the last two matches.
		self.assertEquals(len(matches), 1)

		matches = g._restoreState(matches)
		# Now we should have nothing left.
		self.assertEquals(len(matches), 0)

	def testUpdateState(self):
		matches = {}
		u = Vertex('u1')
		v = Vertex('v1')
		g = Graph()
		g._updateState(u, v, matches)
		self.assertEquals(len(matches), 1)
		self.assertEquals(matches[u.id], 'v1')

#------------------------------------------------------------------------------
# Basic Vertex building methods.
class TestVertexClass(unittest.TestCase):

    def testConstructor(self):
        # Make sure the basic constructor works.
        v = Vertex('v1')
        self.assertTrue(v.id == 'v1')
        self.assertTrue(v.label is None)

        v = Vertex('v2', 'label')
        self.assertTrue(v.id == 'v2')
        self.assertTrue(v.label == 'label')

#------------------------------------------------------------------------------
# Basic Graph building methods.
class TestGraphClass(unittest.TestCase):

    def setUp(self):
        self.g = Graph();

    def testAddVertex(self):
        # Build a single vertex graph.
        a = self.g.addVertex(Vertex('u1'))
        a.label = 'A'
        self.assertTrue('u1' in self.g.vertices)

        # Called with something other than a list or string should raise an
        # exception.
        self.assertRaises(TypeError, self.g.addVertex, None)

        # Adding an existing vertex id should raise an exception.
        self.assertRaises(IndexError, self.g.addVertex, Vertex('u1'))

    def testAddEdge(self):
        # Add a vertex "A".
        a = self.g.addVertex(Vertex('u1'))

        # "Manually" add a vertex 'B', then connect it with 'A'.
        b = self.g.addVertex(Vertex('u2', 'B'))
        self.g.addEdge('u1', 'u2')
        self.assertTrue(b in self.g._edges['u1'])

        # Make sure the vertex degrees were updated.
        self.assertEquals(self.g.vertices['u1'].degree, 1)
        self.assertEquals(self.g.vertices['u2'].degree, 1)

        # Add an edge from u1 to a new vertex 'C'
        c = Vertex('u3', 'C')
        self.g.addEdge('u1', c)
        self.assertTrue(c in self.g._edges['u1'])
        self.assertTrue(self.g._edges['u1'][1].label == 'C')

        # Make sure the vertex degrees were updated.
        self.assertEquals(self.g.vertices['u1'].degree, 2)
        self.assertEquals(self.g.vertices['u3'].degree, 1)

    def testConstructor(self):
        # New graphs should be empty.
        self.assertTrue(len(self.g.vertices) == 0)
        self.assertTrue(len(self.g._edges) == 0)
        
    def testDeleteEdge(self):
        self.assertRaises(KeyError, self.g.deleteVertex, 'X')

        self.g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
        self.assertTrue(len(self.g._edges), 1)
        self.assertEquals(self.g.vertices['u1'].degree, 1)
        self.assertEquals(self.g.vertices['u2'].degree, 1)

        self.g.deleteEdge('u1', 'u2')
        self.assertEquals(len(self.g._edges), 0)
        self.assertEquals(self.g.vertices['u1'].degree, 0)
        self.assertEquals(self.g.vertices['u2'].degree, 0)
       
    def testDeleteVertex(self):
    	self.assertRaises(KeyError, self.g.deleteVertex, 'X')

        a = self.g.addVertex(Vertex('u1', 'A'))
        b = self.g.addVertex(Vertex('u2', 'B'))
        self.g.addEdge('u1', 'u2')
        self.g.addEdge('u2', 'u1')
        self.g.addEdge('u2', Vertex('u3', 'C'))
        self.g.deleteVertex('u1')
        self.assertEquals(len(self.g.vertices), 2)
        self.assertEquals(len(self.g._edges), 1)

    def testEdgeExistsBewtweenLabels(self):
         # Add a vertex "A".
        a = self.g.addVertex(Vertex('u1', 'A'))

        # "Manually" add a vertex 'B', then connect it with 'A'.
        b = self.g.addVertex(Vertex('u2', 'B'))
        self.g.addEdge('u1', 'u2')

        self.assertFalse(self.g.edgeExistsBetweenLabels('X', 'Y'))
        self.assertTrue(self.g.edgeExistsBetweenLabels('A', 'B'))

    def testEdgesProperty(self):
         # Add a vertex "A".
        a = self.g.addVertex(Vertex('u1'))

        # "Manually" add a vertex 'B', then connect it with 'A'.
        b = self.g.addVertex(Vertex('u2', 'B'))
        self.g.addEdge('u1', 'u2')

        # Add an edge from u1 to a new vertex 'C'
        c = Vertex('u3', 'C')
        self.g.addEdge('u2', c)

        for e in self.g.edges:
        	if e[0].id == 'u1':
	        	self.assertEquals(e[1].id, 'u2')
	        elif e[0].id == 'u2':
	        	self.assertEquals(e[1].id, 'u3')
	        else:
	        	self.assertFalse(True)

    def testHasEdgeBetween(self):
        # Build a little graph: A->B,A->C.
        self.g.addEdge(Vertex('u0', 'A'), Vertex('u1', 'B'))
        self.g.addEdge('u0', Vertex('u2', 'C'))

        self.assertTrue(self.g.hasEdgeBetween('u0','u1'))
        self.assertTrue(self.g.hasEdgeBetween('u0','u2'))
        self.assertFalse(self.g.hasEdgeBetween('u1','u2'))
        self.assertFalse(self.g.hasEdgeBetween('u99','u2'))
        

    def testLabelsProperty(self):
        self.g.addVertex(Vertex('u1', 'A'))
        self.g.addVertex(Vertex('u2', 'B'))
        self.g.addVertex(Vertex('u3', 'C'))
        self.assertEquals(len(self.g.labels), 3)
        self.assertTrue('A' in self.g.labels)		
        self.assertTrue('B' in self.g.labels)		
        self.assertTrue('C' in self.g.labels)		

    def testNumVertices(self):
        # Empty graph.
        self.assertEquals(self.g.numVertices, 0)

        # One vertex.
        a = self.g.addVertex(Vertex('u1'))
        self.assertEquals(self.g.numVertices, 1)

if __name__ == '__main__':
    unittest.main()
