import logging
import sys

from Configuration import Configuration
from Production import Production
from Lexer import Lexer
from Token import TokenTypes
from Token import Token
from Graph.Graph import Graph
from Graph.Vertex import Vertex
   
class Parser(object):
    """Graph productions parser."""

    def __init__(self, lexer):
        """
        Constructor.
        Inputs: lexer -- instance of the Lexer class
        Outputs: N/A
        """

        self.lexer = lexer
        self.lookahead = self.lexer.nextToken()
        self.config = {}
        self.productions = [] # array of Production objects
        self.startGraph = None

        self._numVerticesParsed = 0
         
    def parse(self):
        """grammar_file -> configuration productions."""
        self._parseConfiguration()
        self._parseProductionuctions()

    def _consume(self):
        """Moves to the next token."""
        self.lookahead = self.lexer.nextToken()
        
    def _error(self, str):
        """Raises an error message about expecting <str> but found current token
           on the current line number."""
        raise SyntaxError("Expecting %s found %s on line %d" % \
            (str, self.lookahead, self.lexer.lineNum))

    def _match(self, token):
        """Ensures the current token is of type token. token should be an
           integer from lexer.TokenTypes. If it is, advances to the next token
           and returns the token just previously matched.
        """
        if self.lookahead.type == token:
            oldToken = self.lookahead
            self._consume()
            return oldToken
        else:
            self._error(TokenTypes.names[token])

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

    def _parseConfigList(self):
        """config_list -> config ';' config_list | nil"""
        while self.lookahead.type == TokenTypes.ID:
            self._parseConfig()
            self._match(TokenTypes.SEMICOLON)

    def _parseConfiguration(self):
        """configuration -> 'configuration' '{' config_list '}'"""
        self._match(TokenTypes.CONFIGURATION)
        self._match(TokenTypes.LBRACE)
        self._parseConfigList()
        self._match(TokenTypes.RBRACE)

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

    def _parseProduction(self):
        """prod -> graph '==>' graph"""
        lhs = self._parseGraph()
        self._match(TokenTypes.DOUBLEARROW)
        rhs = self._parseGraph()
        self.productions.append( Production(lhs, rhs) )
       
    def _parseProductionList(self):
        """prod_list -> prod ';' prod_list | nil"""
        while self.lookahead.type == TokenTypes.ID:
            self._parseProduction()
            self._match(TokenTypes.SEMICOLON)

    def _parseProductionuctions(self):
        """productions -> 'productions' '{' start_graph prod_list '}'"""
        self._match(TokenTypes.PRODUCTIONS)
        self._match(TokenTypes.LBRACE)
        self._parseStartGraph()
        self._parseProductionList()
        self._match(TokenTypes.RBRACE)

    def _parseStartGraph(self):
        """start_graph -> state_list ';'"""
        self.startGraph = self._parseGraph()
        self._match(TokenTypes.SEMICOLON)

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
