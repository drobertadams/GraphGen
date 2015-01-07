import logging
import sys

from Configuration import Configuration
from Production import Production
from Lexer import Lexer
from Token import TokenTypes
from Token import Token
from Graph.Graph import Graph
from Graph.Vertex import Vertex
   
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
        self._parseProductionuctions()

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
        """config -> ID '=' (ID | NUMBER)"""
        key = self._match(TokenTypes.ID)
        self._match(TokenTypes.EQUALS)
        if self.lookahead.type == TokenTypes.ID:
            value = self._match(TokenTypes.ID)
        elif self.lookahead.type == TokenTypes.NUMBER:
            value = self._match(TokenTypes.NUMBER)
        else:
            self._error("ID or NUMBER")

        # Store the <key,value> pair in the Configuration.
        self.config[key.text] = value.text

    #--------------------------------------------------------------------------
    def _parseConfigList(self):
        """config_list -> config ';' config_list | nil"""
        while self.lookahead.type == TokenTypes.ID:
            self._parseConfig()
            self._match(TokenTypes.SEMICOLON)

    #--------------------------------------------------------------------------
    def _parseConfiguration(self):
        """configuration -> 'configuration' '{' config_list '}'"""
        self._match(TokenTypes.CONFIGURATION)
        self._match(TokenTypes.LBRACE)
        self._parseConfigList()
        self._match(TokenTypes.RBRACE)

    #--------------------------------------------------------------------------
    def _parseEdgeList(self, graph):
        """edgeList -> ID | ID '->' edgeList
           Parses the list of vertex IDs and adds them as nodes to the given
           graph. This parses sentences of the form A->B->C->... The list of 
           IDs in the input are assumed to be vertex labels, not unique
           vertex IDs.
           Inputs: graph(Graph) - graph to add vertices to
           Outputs: none
        """

        currentVertexToken = self._match(TokenTypes.ID)
        currentVertex = graph.findVertexWithLabel(currentVertexToken.text)
        if currentVertex == None:
            currentVertex = Vertex(
                'v%d' % graph.numVertices, # vertex id
#                'v%d' % self._numVerticesParsed, # vertex id
                currentVertexToken.text          # vertex label
            )
            #self._numVerticesParsed = self._numVerticesParsed + 1
            graph.addVertex(currentVertex)
            logging.debug('Created vertex %s' % str(currentVertex))
            logging.debug('graph now has %d vertices' % graph.numVertices)

        while self.lookahead.type == TokenTypes.ARROW:
            self._match(TokenTypes.ARROW)

            nextVertexToken = self._match(TokenTypes.ID)
            nextVertex = graph.findVertexWithLabel(nextVertexToken.text)
            if nextVertex == None:
                nextVertex = Vertex(
                    'v%d' % graph.numVertices, # vertex id
#                    'v%d' % self._numVerticesParsed, # vertex id
                    nextVertexToken.text             # vertex label
                )
                #self._numVerticesParsed = self._numVerticesParsed + 1
                graph.addVertex(nextVertex)
                logging.debug('Created vertex %s' % str(nextVertex))

            graph.addEdge(currentVertex, nextVertex)
            logging.debug('Linked %s and %s' % (currentVertex, nextVertex))

            currentVertex = nextVertex

    #--------------------------------------------------------------------------
    def _parseGraph(self):
        """graph -> edgeList | edgeList ',' graph
           Parses, builds, and returns a Graph object.
        """
        logging.debug('parsing new graph')
        g = Graph()
        self._parseEdgeList(g)
        while self.lookahead.type == TokenTypes.COMMA:
            self._match(TokenTypes.COMMA)
            self._parseEdgeList(g)
        return g

    #--------------------------------------------------------------------------
    def _parseProduction(self):
        """prod -> graph '==>' graph"""
        lhs = self._parseGraph()
        self._match(TokenTypes.DOUBLEARROW)
        rhs = self._parseGraph()
        self.productions.append( Production(lhs, rhs) )
       
    #--------------------------------------------------------------------------
    def _parseProductionList(self):
        """prod_list -> prod ';' prod_list | nil"""
        while self.lookahead.type == TokenTypes.ID:
            self._parseProduction()
            self._match(TokenTypes.SEMICOLON)

    #--------------------------------------------------------------------------
    def _parseProductionuctions(self):
        """productions -> 'productions' '{' start_graph prod_list '}'"""
        self._match(TokenTypes.PRODUCTIONS)
        self._match(TokenTypes.LBRACE)
        self._parseStartGraph()
        self._parseProductionList()
        self._match(TokenTypes.RBRACE)

    #--------------------------------------------------------------------------
    def _parseStartGraph(self):
        """start_graph -> state_list ';'"""
        self.startGraph = self._parseGraph()
        self._match(TokenTypes.SEMICOLON)
