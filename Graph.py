import copy
import logging
import pickle
import sys

from Vertex import Vertex

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class Graph(object):
    """
    Represents a directional graph of Vertex objects. The graph can search for
    matching subgraphs.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Builds an empty graph.
        """
        # A dictionary (key is vertex id) of Vertex objects.
        self.vertices = {}

        # A dictionary (key is vertex id) of a list of edges to Vertex objects.
        self._edges = {}

        # A dictionary (key is vertex id) of a list of neighbor Vertex objects.
        # This is different than _edges in that neighbors stores all adjancent
        # vertices, regardless of edge direction.
        self.neighbors = {}

        # A list of solutions as used by the seach() method. Since that method
        # is recursive, we need a single spot to store all the solutions found.
        self.solutions = []

        # A stack of match dictionaries as used by _updateState().
        self.matchHistory = []

    #--------------------------------------------------------------------------
    def addEdge(self, n, m):
        """
        Adds a directional edge from vertex n to vertex m. If 
        neither vertex exists, they are created.
        Inputs: n, m - endpoints of the edge; can be either new Vertex objects
            vid(str) of existing vertices.
        Outputs: none
        """

        if isinstance(n, str):
            n = self.vertices[n]
        else:
            self.addVertex(n)

        if isinstance(m, str):
            m = self.vertices[m]
        else:
            self.addVertex(m)

        if n.id not in self._edges:
            self._edges[n.id] = []
        self._edges[n.id].append(m)

        self.neighbors[n.id].append(m)
        self.neighbors[m.id].append(n)

        n.degree = n.degree + 1
        m.degree = m.degree + 1

    #--------------------------------------------------------------------------
    def addVertex(self, vertex):
        """
        Adds a new vertex to the graph.
        Input: vertex - Vertex object to add
        Output: The vertex that was just created
        """

        if not isinstance(vertex, Vertex):
            raise TypeError('addVertex requires a Vertex object')

        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex
            self.neighbors[vertex.id] = []
        else:
            raise IndexError("Vertex %s already exists in the graph" % vertex.id)

        return vertex

    #--------------------------------------------------------------------------
# TODO : Write a test for this.
    def deleteEdge(self, startVID, endVID):
        """
        Removes the edge from the given vertices. Does nothing if the edge
        doesn't exist.
        Inputs: startVID, endVID - vertex IDs
        Outputs: none
        """

        if startVID not in self._edges:
            # startVID has no edges from it
            return

        startVertex = self.vertices[startVID]
        endVertex = self.vertices[endVID]

        self._edges[startVID].remove(endVertex)
        if len(self._edges[startVID]) == 0: # just deleted the last edge from n.id
            logging.debug('removed last edge from %s' % startVID)
            self._edges.pop(startVID)    # remove n.id from the list of edges

        self.neighbors[startVID].remove(endVertex)
        self.neighbors[endVID].remove(startVertex)

        startVertex.degree = startVertex.degree - 1
        endVertex.degree = endVertex.degree - 1

    #--------------------------------------------------------------------------
    def deleteVertex(self, vid):
            """
            Deletes the vertex with the given vid along with all edges to and from it.
            Inputs: vertex ID (string) vid
            Outputs: nothing
            Raises: KeyError if vid is not a valid vertex id
            """
            if vid not in self.vertices:
                    raise KeyError('vertex id %s does not appear in this graph' % vid)

            self.vertices.pop(vid, None)
            if vid in self._edges:
                    self._edges.pop(vid)

            for vectorID,edgeList in self._edges.items():
                    edgeList[:] = (vertex for vertex in edgeList if vertex.id != vid)
                    if len(edgeList) == 0:
                            self._edges.pop(vectorID)

    #--------------------------------------------------------------------------
    @property
    def edges(self):
            """
            Iterator that returns all (Vertex,Vertex) tuples from this graph.
            """
            for startVID in self._edges:
                    for endVertex in self._edges[startVID]:
                            startVertex = self.vertices[startVID]
                            yield ( startVertex, endVertex )
    
    #--------------------------------------------------------------------------
    def edgeExistsBetweenLabels(self, startLabel, endLabel):
            """
            Returns whether or not an edge exists from a vertex with label 
            startLabel to a vertex with label endLabel.
            Inputs:
                    * startLabel - starting vertex label
                    * endLabel - ending vertex label
            Outputs: True if edge exists, False otherwise
            """
            for edge in self.edges:
                    if edge[0].label == startLabel and edge[1].label == endLabel:
                            return True
            return False

    #--------------------------------------------------------------------------
    def findVertexWithLabel(self, label):
            """
            Returns the Vertex in this graph that has the given label.
            Inputs: label(string) to find
            Outputs: Reference to the Vertex or None
            """

            for id,vertex in self.vertices.items():
                    if vertex.label == label:
                            return vertex
            return None

    #--------------------------------------------------------------------------
    def hasEdgeBetween(self, startVID, endVID):
        """
        Checks to see if an edge exists between the given start and end vid.
        Inputs: startVID, endVID - vertex id's
        Outputs: Boolean
        """
        if startVID in self._edges:
            for neighbor in self._edges[startVID]:
                if neighbor.id == endVID:
                    return True

        return False

    #--------------------------------------------------------------------------
    @property
    def labels(self):
            """
            Returns a list of all the labels in this graph (there may be duplicates).
            Outputs: list of label strings
            """
            return [ v.label for id,v in self.vertices.items() ]
    
    #--------------------------------------------------------------------------
    @property
    def numVertices(self):
        return len(self.vertices)

    #--------------------------------------------------------------------------
    def search(self, q):
            """
            Search for every instance of q in self. Based on _An In-depth 
            Comparison of Subgraph Isomorphism Algorithms in Graph Databases_, 
            Lee et al., 2013.
        Inputs: q - Graph to search for in self.
        Outputs: a list of solutions (list of "matches"). matches is a
        list of [Vertex.id, Vertex.id] mappings.
        """

            logging.debug('self has %d vertices' % self.numVertices)
            logging.debug(">>> Searching for %s in %s" % (q, self))


            # matches is a dict of vid(query)->vid(data) mappings of which query
        # vertex is matched to which data graph vertex. 
            matches = {}

            # Find candidates for each query vertex. If at least one query vertex
            # have a candidate, then quit.
            if not self._findCandidates(q):
                    logging.debug('there are no candidate vertices!')
                    return self.solutions

            # From the list of possible candidates, try to find all isomorphisms.
            self._subgraphSearch(matches, q)

            return self.solutions

    #--------------------------------------------------------------------------
    def _filterCandidates(self, u):
            # Returns an array of vertices from self that have the same
            # label as u. The array is empty if no vertices match.
            # Input: Query vertex u.
            # Output: Array of vertices from self.
            candidates = []
            for id,vertex in self.vertices.items():
                    if vertex.label == u.label:
                            candidates.append(vertex)
            return candidates

    #--------------------------------------------------------------------------
    def _findCandidates(self, q):
            # For each query vertex, create a list of possible data vertices. If there
            # are none, then return False
            # Input: query graph q
            # Output: False if at least one query vertex doesn't have a match, True
            # otherwise.

            # If the query graph is empty, there are no candidates.
            if len(q.vertices) == 0:
                    return False

            for id,u in q.vertices.items():
                    u.candidates = self._filterCandidates(u)
                    if len(u.candidates) == 0:
                            return False
            return True

    #--------------------------------------------------------------------------
    def _findMatchedNeighbors(self, u, matches):
            # Find the matched vertices adjacent to query vertex u. This method
            # should be called on the query graph.
            # Input: Vertex u, dict of matches
            # Output: List of neighbors of u that appear in matches.
            if u is None or matches is None or len(matches) == 0:
                    return []

            neighbors = []
            # logging.debug('%s has neighbors %s' % (u, str(self.neighbors[u.id])))
            for neighborVertex in self.neighbors[u.id]:
                    if neighborVertex.id in matches:
                            neighbors.append(neighborVertex)
            return neighbors

    #--------------------------------------------------------------------------
    def _isJoinable(self, u, v, q, matches):		
            """
            See if u and v are joinable this data graph. 
            Iterates through all adjacent matched query vertices of u. 
            If an adjacent query vertex, n, is already matched with a data 
            vertex, w, then it checks whether there is a corresponding edge 
            (v, w) in this data graph going in the same direction as the edge
            between (u, n).
            Inputs: 
                    * query vertex u
                    * data vertex v
                    * query graph q, 
                    * list of matched query/data vertices
            Outputs: True if u and v can be matched, False otherwise
            """

            if u is None or v is None or q is None:
                    return False

            if len(matches) == 0:
                    return True

            neighbors = q._findMatchedNeighbors(u, matches)
            for n in neighbors:
                    w = self.vertices[matches[n.id]]
                    if u.id in q._edges and n in q._edges[u.id] and w in self._edges[v.id]:
                            return True
                    elif u in q._edges[n.id] and v in self._edges[w.id]:
                            return True
                    else:
                            return False

            return False

    #--------------------------------------------------------------------------
    def _nextUnmatchedVertex(self, matches):
            # Returns the next unmatched vertex from a query (so this method should
            # be called on the query graph, not the data graph).
            # Input: previous matches dict matches
            # Output: The next unlabeled query vertex in self.
            for id,vertex in self.vertices.items():
                    if id not in matches:
                            return vertex
            return None

    #--------------------------------------------------------------------------
    def _refineCandidates(self, candidates, u, matches):
            # Given a query vertex u, removes candidate vertices from the original
            # candidate list (candidates) created by _filterCandidates() that are no longer 
            # obvious matches because they have a degree smaller than u. It also
            # removes vertices that have already been matched.
            # Input: list of candidate graph vertices candidates, a query vertex
            # u, and the mapping of already mapped vertices.
            # Output: the revised list of candidate vertices.
            candidates = [v for v in candidates if (v.degree >= u.degree) and 
                    (v.id not in matches)]
            return candidates

    #--------------------------------------------------------------------------
    def _restoreState(self, matches):
            # Input: dict matches.
            # Output: Updated matches without the last set of matches.
            # Undoes the last vertex mapping by removing the last mapping pair
            # _(u, v)_ from _matches_.
            return pickle.loads(self.matchHistory.pop())

    #--------------------------------------------------------------------------
    def __repr__(self):
            if len(self.vertices) == 1:
                    for vertexID,vertex in self.vertices.items():
                            return str(vertex)
            else:
                    # With multiple vertices, print an adjacency list.
                    s = ''
                    for vertexID,neighbors in self._edges.items():
                            for neighbor in neighbors:
                                    s += '%s->%s, ' % (self.vertices[vertexID], neighbor)
                    return s

    #--------------------------------------------------------------------------
    def _subgraphSearch(self, matches, q):
            """
            Searches self for an instance of q. Calls itself recursively to find
            all such instances. Solutions are stored in self.solutions.
            Inputs: 
                    * matches - dictionary of vertex mappings
                    * q - query Graph
            Outputs: nothing
            """

            # If every query vertex has been matched, then we're done. Store the
            # solution we found and return. matches is twice the number of query
            # vertices because both the source and destination vertices are stored.
#		if len(matches) == 2*len(q.vertices):
            if len(matches) == len(q.vertices):
                    logging.debug('found a solution %s' % matches)
                    self.solutions.append(copy.deepcopy(matches))
                    return 
            
            # Get the next query vertex that needs a match.
            u = q._nextUnmatchedVertex(matches)

            # Test the degenerate case...there are no query vertices that need a match.
            if u is None:
                    return

            logging.debug('checking for a match with data vertex %s' % u)

            # Refine the list of candidate vertices from that obviously aren't
            # good candidates.
            u.candidates = self._refineCandidates(u.candidates, u, matches)

            # Check each candidate for a possible match.
            for v in u.candidates:

                    logging.debug('checking query vertex candidate %s' % v)

                    # Check to see _u_ and _v_ are joinable in _g_.
                    if self._isJoinable(u, v, q, matches):

                            logging.debug("oh yea, that's a match")

                            # Yes they are, so store the mapping and try the next vertex.
                            self._updateState(u, v, matches)
                            logging.debug('matches is now %s' % matches)
                            self._subgraphSearch(matches, q)

                            # Undo the last mapping.
                            matches = self._restoreState(matches)

    #--------------------------------------------------------------------------
    def _updateState(self, u, v, matches):
            """
            Stores the current mapping of Vertex u to Vertex v.
            Each call to _updateState() stores the previous set of matches to
            a stack of matches, so that _restoreState() can undo it.
            Inputs: 
                    * u - query Vertex
                    * v - data Vertex
                    * matches - dictionary of Vertex.id -> Vertex.id mappings 
            Outputs: nothing
            """

            self.matchHistory.append(pickle.dumps(matches))
            matches[u.id] = v.id
            #matches[v.id] = u.id
