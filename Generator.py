#!/usr/bin/python
# vim:nowrap

import logging
import random
import sys

from PGC.Parser import Parser
from PGC.Lexer import Lexer
from PGC.Graph.Vertex import Vertex

class Generator(object):
    """

    Transformation engine for graphs. Given a set of Productions of the form
    lhs ==> rhs, and using a starting graph G, uses graph isomorphic searching
    to find instances of a lhs in G and replaces the lhs vertices with the rhs.
    The engine continues to apply these transformations until G contains a
    given number of vertices. This assumes that the productions generally
    increase the number of vertices.

    Usage: Either use the all-inclusive main() method which checks the 
    command-line arguments, or call applyProductions() yourself which
    takes a starting graph, list of productions, and a dictionary of
    configuration options.
    """

    #--------------------------------------------------------------------------
    def applyProductions(self, startGraph, productions, config):
        """
        Randomly applies a Production from the given list of Productions to the
        specified starting graph until the graph contains at least the number
        of vertices specified by the config option "min_vertices". This assumes
        that the productions generally increase the number of vertices.
        Inputs: 
            * startGraph - Graph to begin applying transformations
            * productions - list of Production objects
            * config - dictionary of options
        Outputs: None
        """ 
        while startGraph.numVertices < int(config['min_vertices']):
            # matchingProductions is a list of (Production, mapping) 
            # pairs where mapping is {vid->vid} dictionary of where 
            # the production's lhs vertices can be found in startGraph.
            matchingProductions = self._findMatchingProductions(startGraph, productions)
            
            if len(matchingProductions) == 0:
                raise RuntimeError('No productions match the given graph.')

            (prod, mapping) = random.choice(matchingProductions)

            self._applyProduction(startGraph, prod, mapping)

    #--------------------------------------------------------------------------
    def generateFromFile(self, filename):
        """
        Opens the given grammar file, parses it, then applies its productions
        to its start graph.
        Inputs: filename is the name of a graph grammar file
        Outputs: resulting graph
        """
        grammarFile = open(filename, 'r')
        f = self._parseGrammarFile(grammarFile.read())
        grammarFile.close()

        self.applyProductions(f.startGraph, f.productions, f.config)
        return f.startGraph

    #--------------------------------------------------------------------------
    # PRIVATE METHODS - These aren't the methods you're looking for.
    #--------------------------------------------------------------------------
    def _addNewEdges(self, graph, production, rhsMapping):
        """
        Adds edges to graph that appear in production.rhs but not in 
        production.lhs. Assumes that all the new vertices in the production.rhs
        have been added to graph, and rhsMapping has been updated accordingly.
        Inputs:
            * graph - Graph to which to apply the production
            * production - Production to apply
            * rhsMapping - {vid->vid} mapping between production.rhs
              and graph
        Outputs: None
        """	
        logging.debug('>>> _addNewEdges <<<')
        for rhsEdge in production.rhs.edges: # [startVertex,endVertex]
            graphStartVID = rhsMapping[rhsEdge[0].id]
            graphEndVID = rhsMapping[rhsEdge[1].id]
            if not graph.hasEdgeBetweenVertices(graphStartVID, graphEndVID):
                graph.addEdge(graphStartVID, graphEndVID)
        logging.debug('graph is now %s' % graph)


    #--------------------------------------------------------------------------
    def _addNewVertices(self, graph, production, rhsMapping):
        """
        Adds vertices to graph that appear in production.rhs but not in 
        production.lhs. New vertices are given a vid of the form 'vN' where
        N is the number of vertices currently in the graph. New graph vertices
        are also added to rhsMapping.
        Inputs:
            * graph - Graph to which to apply the production
            * production - Production to apply
            * rhshMapping - {vid->vid} mapping from production.rhs to graph.
              This is typically created by _mapRHSToGraph().
        Outputs: nothing
        """
        logging.debug('>>> _addNewVertices <<<')
        for rhsVertex in production.rhs.vertices:
            if rhsVertex.label not in production.lhs.labels:
                logging.debug('label %s in rhs but not lhs' % rhsVertex.label)
                newVertexID = 'v%s' % graph.numVertices
                newVertex = graph.addVertex(Vertex(newVertexID, rhsVertex.label))
                logging.debug('added vertex %s' % newVertex)
                rhsMapping[rhsVertex.id] = newVertexID
        logging.debug('graph is now %s' % graph)

    #--------------------------------------------------------------------------
    def _applyProduction(self, graph, production, lhsMapping):
        """
        Applies the given production to the given graph. The general idea is to
        transform the portion of the graph identified by mapping (which 
        corresponds to the production's LHS) to look like the RHS of the
        production, by adding and/or removing vertices and edges.
        Inputs:
            graph - Graph to which to apply the production
            production - Production to apply
            lhsMapping - {vid->vid} mapping from production.lhs
                to graph
        Outputs: None
        """
        rhsMapping = self._mapRHSToGraph(graph, production, lhsMapping)
        self._deleteMissingVertices(graph, production, lhsMapping)
        self._deleteMissingEdges(graph, production, lhsMapping, rhsMapping)
        self._addNewVertices(graph, production, rhsMapping)
        self._addNewEdges(graph, production, rhsMapping)

    #--------------------------------------------------------------------------
    def _deleteMissingEdges(self, graph, production, lhsMapping, rhsMapping):
        """
        Deletes edges from graph that appear in production.lhs but not in 
        production.rhs. Assumes new vertices on rhs have been added to
        graph.
        Inputs: 
            * graph - Graph to which to apply the production
            * production - Production to apply
            * lhsMapping - {vid->vid} mapping from production.lhs
              to graph
            * rhsMapping - {vid->vid} mapping from production.rhs
              to graph
        Outputs: None
        """
        logging.debug('>>> _deleteMissingEdges <<<')
        for lhsEdge in production.lhs.edges:    # [startVertex,endVertex]

            # Starting and ending vertices of the corresponding edge in graph.
            graphStartVID = lhsMapping[lhsEdge[0].id]
            graphEndVID = lhsMapping[lhsEdge[1].id]
            
            # Try to find the corresponding starting vertex in the rhs (if it
            # it exists at all). If it doesn't even exist, then the edge
            # doesn't exist either, so delete it from graph.
            rhsStart = [rhsID for rhsID,graphID in rhsMapping.items() if graphID == graphStartVID]
            if len(rhsStart) == 0:
                logging.debug('edge start from %s to %s does not appear in rhs' % (lhsEdge[0], lhsEdge[1]))
                graph.deleteEdge(graphStartVID, graphEndVID)
                continue

            # Try to find the corresponding ending vertex in the rhs (if it
            # it exists at all). If it doesn't even exist, then the edge
            # doesn't exist either, so delete it from graph.
            rhsEnd = [rhsID for rhsID,graphID in rhsMapping.items() if graphID == graphEndVID]
            if len(rhsEnd) == 0:
                logging.debug('edge end from %s to %s does not appear in rhs' % (lhsEdge[0], lhsEdge[1]))
                graph.deleteEdge(graphStartVID, graphEndVID)
                continue

            # We found both rhs vertices, but are they connected with an
            # edge? If not, the delete the edge from graph.
            if not production.rhs.hasEdgeBetweenVertices(rhsStart[0], rhsEnd[0]):
                graph.deleteEdge(graphStartVID, graphEndVID)

        logging.debug('graph is now %s' % graph)

    #--------------------------------------------------------------------------
    def _deleteMissingVertices(self, graph, production, lhsMapping):
        """
        Deletes vertices from graph that appear in production.lhs but not in 
        production.rhs. It also deletes all edges to lead to or from the
        deleted vertex.
        Inputs:
            * graph - Graph to which to apply the production
            * production - Production to apply
            * lhsMapping - {vid->vid} mapping between production.lhs
                    and graph
        Outputs: None
        """
        for lhsVertex in production.lhs.vertices:
            if not production.rhs.findVertexWithLabel(lhsVertex.label):
                graphVertexID = lhsMapping[lhsVertex.id]
                graph.deleteVertex(graphVertexID)

    #--------------------------------------------------------------------------
    def _findMatchingProductions(self, graph, productions):
        """
        Finds all the productions whose LHS graph can be found in graph.
        Inputs: 
            * graph - Graph to search
            * productions - list of Production objects to search
        Outputs: list of (Production, mapping) tuples where Production
            is a Production whose LHS can be found in graph, and mapping is
            a {vid->vid} dictionary (LHS->graph) of where the LHS can be found.
        """
        solutions = []
        for prod in productions:
            logging.debug('Checking production %s ' % prod.lhs)

            # Find all places where prod.lhs can be found in graph.
            listOfMatches = graph.search(prod.lhs)
            if len(listOfMatches) > 0:
                for match in listOfMatches:
                    solutions.append( (prod, match) )
                    logging.debug('Production %s matches' % prod.lhs)
            else:
                    logging.debug('Production %s does not match' % prod.lhs)
        return solutions

    #--------------------------------------------------------------------------
    def _mapRHSToGraph(self, graph, production, lhsMapping):
        """
        Maps to production's rhs vertices to graph. For rhs vertices that
        appear in the lhs, we use the lhsMapping to determine which graph
        vertex the rhs vertex maps to. For rhs vertices that are new (i.e.,
        don't exist in the lhs), we ignore them for now and update the
        rhs mapping when we add the new vertices to graph.
        Inputs:
            * graph - Graph to which to apply the production
            * production - Production to apply
            * lhs2GraphMapping - {vid->vid} mapping from production.lhs
              vertices to graph
        Outputs: {vid->vid} mapping from production.rhs vertices to graph
        """
        rhsMapping = {}

        for rhsVertex in production.rhs.vertices:
            if rhsVertex.label in production.lhs.labels:
                lhsVertex = production.lhs.findVertexWithLabel(rhsVertex.label)
                rhsMapping[rhsVertex.id] = lhsMapping[lhsVertex.id] 
        return rhsMapping

    #--------------------------------------------------------------------------
    def _parseGrammarFile(self, grammarFile):
        """
        Parses the given grammar file contents, returning the parser.
        Inputs: grammarFile - string contents of a graph grammar file
        Outputs: Parser after it has parsed the given input
        """

        p = Parser(Lexer(grammarFile))
        p.parse()
        return p

# debug, info, warning, error and critical
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
if __name__ == '__main__':
    e = Generator()
    e.main()
