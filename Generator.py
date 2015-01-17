#!/usr/bin/python
# :vim:nowrap

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
        while startGraph.numVertices < config['min_vertices']:

            # matchingProductions is a list of (Production, mapping) 
            # pairs where mapping is {vid->vid} dictionary of where 
            # the production's lhs vertices can be found in startGraph.
            matchingProductions = self._findMatchingProductions(startGraph, productions)
            
            if len(matchingProductions) == 0:
                raise RuntimeError('No productions match the given graph.')

            (prod, mapping) = random.choice(matchingProductions)
            logging.debug('Going to apply %s using mapping %s.' % (prod, mapping))

            self._applyProduction(startGraph, prod, mapping)

    #--------------------------------------------------------------------------
    def main(self):
        """
        To be called from the command line. Checks the command line arguments 
        for a filename, opens the file, and sends it to the parser.
        Inputs: None
        Outputs: None
        """
        if len(sys.argv) < 2:
            raise RuntimeError("Usage: %s FILENAME" % sys.argv[0])
        
        prodFile = open(sys.argv[1], 'r')
        p = self._parseGrammarFile(prodFile.read())
        prodFile.close()

        self.applyProductions(p.startGraph, p.productions, p.config)

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
        for rhsEdge in production.rhs.edges: # [startVertex,endVertex]
            graphStartVID = rhsMapping[rhsEdge[0].id]
            graphEndVID = rhsMapping[rhsEdge[1].id]
            if not graph.hasEdgeBetweenVertices(graphStartVID, graphEndVID):
                graph.addEdge(graphStartVID, graphEndVID)

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
        for rhsVertex in production.rhs.vertices:
            if rhsVertex.label not in production.lhs.labels:
                newVertexID = 'v%s' % graph.numVertices
                newVertex = graph.addVertex(Vertex(newVertexID, rhsVertex.label))
                rhsMapping[rhsVertex.id] = newVertexID

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
        self._addNewVertices(graph, production, lhsMapping, rhsMapping)
        self._addNewEdges(graph, production, rhsMapping)
        self._deleteMissingEdges(graph, production, lhsMapping, rhsMapping)
        self._deleteMissingVertices(graph, production, lhsMapping)

    #--------------------------------------------------------------------------
    def _deleteMissingEdges(self, graph, production, lhsMapping, rhsMapping):
        """
        Deletes edges from graph that appear in production.lhs but not in 
        production.rhs. Assumes the vertices between lhs and rhs have been
        added/removed.
        Inputs: 
            * graph - Graph to which to apply the production
            * production - Production to apply
            * lhsMapping - {vid->vid} mapping from production.lhs
              to graph
            * rhsMapping - {vid->vid} mapping from production.rhs
              to graph
        Outputs: None
        """
        for lhsEdge in production.lhs.edges:    # [startVertex,endVertex]
            graphStartVID = lhsMapping[lhsEdge[0].id]
            graphEndVID = lhsMapping[lhsEdge[1].id]
            
            # Figure out which rhs vertices are mapped to the starting and
            # ending graph vertices we just calculated.
            rhsStartVID = [rhsID for rhsID,graphID in rhsMapping.items() if graphID == graphStartVID][0]
            rhsEndVID = [rhsID for rhsID,graphID in rhsMapping.items() if graphID == graphEndVID][0]

            if not production.rhs.hasEdgeBetweenVertices(rhsStartVID, rhsEndVID):
                graph.deleteEdge(graphStartVID, graphEndVID)

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
