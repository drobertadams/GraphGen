import logging
import re
import sys

from Production import Production
from Lexer import Lexer
from Token import TokenTypes
from Token import Token
from YapyGraph.Graph import Graph
from YapyGraph.Vertex import Vertex
   
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class Parser(object):
    """
    Graph productions parser.
    """

    #--------------------------------------------------------------------------
    def __init__(self, lexer):
        """
        Constructor.
        Inputs: lexer -- instance of the Lexer class
        Outputs: N/A
        """
        self.lexer = lexer
        self.lookahead = self.lexer.nextToken() # next token
        self.config = {} # configuration section of the input
        self.productions = [] # array of Production objects
        self.startGraph = None # starting graph

        # As we are parsing a graph, we keep track of the number
        # of vertices parsed so far.
        self._numVerticesParsed = 0
         
    #--------------------------------------------------------------------------
    def parse(self):
        """grammar_file -> configuration productions."""
        self._parseConfiguration()
        self._parseProductions()

    #--------------------------------------------------------------------------
    # PRIVATE METHODS - These aren't the methods you're looking for.
    #--------------------------------------------------------------------------
    def _consume(self):
        """
        Consumes the current token and advances to the next.
        """
        self.lookahead = self.lexer.nextToken()
        
    #--------------------------------------------------------------------------
    def _error(self, str):
        """
        Raises an error message about expecting str but found current token
        on the current line number.
        """
        raise SyntaxError("Expecting %s found %s on line %d" % \
            (str, self.lookahead, self.lexer.lineNum))

    #--------------------------------------------------------------------------
    def _match(self, tokenType):
        """
        If the type of the current token type matches the given tokenType,
        advance to the next token, otherwise, raise an error.
        Inputs: tokenType is an integer from lexer.TokenTypes
        Outputs: current token (the one just consumed)
        """
        if self.lookahead.type == tokenType:
            oldToken = self.lookahead
            self._consume()
            return oldToken
        else:
            self._error(TokenTypes.names[tokenType])

    #--------------------------------------------------------------------------
    def _parseConfig(self):
        """
        config -> ID '=' (ID | NUMBER)
        
        
        A config is a simple name/value pair.
        """
        key = self._match(TokenTypes.ID)
        self._match(TokenTypes.EQUALS)
        if self.lookahead.type == TokenTypes.ID:
            value = self._match(TokenTypes.ID)
        elif self.lookahead.type == TokenTypes.NUMBER:
            value = self._match(TokenTypes.NUMBER)
        else:
            self._error("ID or NUMBER")

        # Store the <key,value> pair in the configuration.
        self.config[key.text] = value.text

    #--------------------------------------------------------------------------
    def _parseConfigList(self):
        """
        config_list -> config ';' config_list | nil
        
        A list of zero or more configuration statements.
        """
        while self.lookahead.type == TokenTypes.ID:
            self._parseConfig()
            self._match(TokenTypes.SEMICOLON)

    #--------------------------------------------------------------------------
    def _parseConfiguration(self):
        """
        configuration -> 'configuration' '{' config_list '}'
        
        The configuration section of the input file. Consists of a
        'configuration' keyword, and then a list of configuration statements
        surrounded by curly braces.
        """
        self._match(TokenTypes.CONFIGURATION)
        self._match(TokenTypes.LBRACE)
        self._parseConfigList()
        self._match(TokenTypes.RBRACE)

    #--------------------------------------------------------------------------
    def _parseEdgeList(self, graph):
        """
        edgeList -> ID | ID '->' edgeList

        An edgeList represents a set of graph nodes connected with directed
        edges. In an edgeList ID is actually the label to be applied to
        a given vertex. So A->B represents two vertices with labels "A" and
        "B" respectively, connected by an edge from A to B.

        This method reads a list of labels (ID) and edges and adds them to
        the given graph. If the graph already has a vertex with the given
        label, the existing vertex is used intead.

        If new vertices are added they are given a unique id of "vN" where
        N is the next available vertex number (starting with 0).

        Inputs: graph - Graph to add vertices to
        Outputs: none
        """

        currentVertexToken = self._match(TokenTypes.ID)
        currentVertex = self._parseVertexID(currentVertexToken, graph)

        while self.lookahead.type == TokenTypes.ARROW:
            self._match(TokenTypes.ARROW)

            # Parse the next vertex in the input, creating a new vertex
            # if needed.
            nextVertexToken = self._match(TokenTypes.ID)
            nextVertex = self._parseVertexID(nextVertexToken, graph)

            # Connect the first vertex we read with the second one.
            graph.addEdge(currentVertex, nextVertex)

            currentVertex = nextVertex

    #--------------------------------------------------------------------------
    def _parseGraph(self):
        """
        graph -> edgeList | edgeList ',' graph

        An edgeList represents a connected path of vertices. A "graph" is
        a comma-separated list of such paths. This method builds a graph
        from the given representation.
        Input: none
        Output: Graph build from the incoming list of edgeLists
        """
        #logging.debug('parsing new graph')
        g = Graph()
        self._parseEdgeList(g)
        while self.lookahead.type == TokenTypes.COMMA:
            self._match(TokenTypes.COMMA)
            self._parseEdgeList(g)
        return g

    #--------------------------------------------------------------------------
    def _parseProduction(self):
        """
        prod -> graph '==>' graph

        A production defines a transformation taking one graph (on the LHS)
        and transforming it to a different graph (RHS).
        """
        lhs = self._parseGraph()
        self._match(TokenTypes.DOUBLEARROW)
        rhs = self._parseGraph()
        self.productions.append( Production(lhs, rhs) )
       
    #--------------------------------------------------------------------------
    def _parseProductionList(self):
        """
        prod_list -> prod ';' prod_list | nil
        
        A list of zero or more productions separated by semicolons.
        """
        while self.lookahead.type == TokenTypes.ID:
            self._parseProduction()
            self._match(TokenTypes.SEMICOLON)

    #--------------------------------------------------------------------------
    def _parseProductions(self):
        """
        productions -> 'productions' '{' start_graph prod_list '}'

        The productions section of the input file. Consists of a
        'productions' keyword, and then a start graph and list of production 
        statements surrounded by curly braces.
        """
        self._match(TokenTypes.PRODUCTIONS)
        self._match(TokenTypes.LBRACE)
        self._parseStartGraph()
        self._parseProductionList()
        self._match(TokenTypes.RBRACE)

    #--------------------------------------------------------------------------
    def _parseStartGraph(self):
        """
        start_graph -> graph ';'

        A simple graph that the generator will use to initialize the
        starting graphs.
        """
        self.startGraph = self._parseGraph()
        self._match(TokenTypes.SEMICOLON)

    #--------------------------------------------------------------------------
    def _parseVertexID(self, token, graph):
        """
        Parses the given token (ID) into a text label and optional
        vertex number (e.g., "A1"). If a vertex with these two data don't 
        exist in the given graph, it is added. Otherwise, the existing 
        vertex from the graph is returned.
        """
        label = re.match('[A-z]+', token.text).group(0)
        match = re.search('[0-9]+$', token.text)
        number = match.group(0) if match is not None else None
        name = Vertex.makeName(label, number)
        vertex = graph.findVertex(name)
        if vertex == None:
            # graph doesn't contain a vertex with the label.
            vertex = Vertex(
                'v%d' % graph.numVertices, # vertex id
                label, number
            )
            graph.addVertex(vertex)
        return vertex
 
