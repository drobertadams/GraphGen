# Procedurally Generated Content

## Overview

The goal is to procedurally build a Petri Net (or just "Net") that describes
the objectives/level in an "adventure game". A Net contains a starting state
and a set of transitions that describe actions that need to be taken to
complete the level. For example, a Net might indicate that the hero needs to
find a sword, slay the troll, and pick up the gem in order to exit the level.

The process of building a Net is to use a grammar to describe transformations
that change a starting Net (typically a simple one) into a more complex one.
The grammar allows the user to describe the starting Net, along with a set of 
productions that show how to transform a Net into a different Net. The grammar
also specifies when the transformation process should end (when the Net has
grown to a given size).

## Implementation

The tool consists of a parser that reads the grammar input file, and a 
"generator" that actually applies the productions/transformations to
"generate" a Net. Underlying everything is a Graph object that represents a 
directed graph and can perform subgraph (isomorphic) searches.

### Parser Tool Implementation

The grammar parser is implemented as a traditional top-down recursive descent
parser and associated lexer. Classes include:

- Token - a simple representation of a token with type and lexeme
- Lexer - converts the input character stream into a stream of Tokens
- Parser - reads the input Token stream from the Lexer and builds a dictionary
  of configuration options guide the Generator, and a list of Productions for
  the Generator to use. A sample grammar is given below:

		# Sample Grammar File

		configuration {
			max_states = 10;
		}

		productions {
			A;	# start graph

			# Productions
			A ==> A -> B;
			A -> B ==> A -> B, A -> C;
			A -> C ==> C -> A;
		}
		
- Production - this class provides a simple representation of a graph
  transformation production (e.g., `A->B ==> A->C`). The stores the graph on
  the left-hand side in Production.lhs, and the graph on the right-hand side
  in Production.rhs.

### Generator Tool Implementation

Generator - Generator is a transformation engine for graphs. Given a list of
Productions of the form lhs ==> rhs, and using a starting graph G, uses graph
isomorphic searching to find instances of a lhs in G and replaces the lhs with
the rhs.  The engine continues to apply these transformations until G contains
a given number of vertices. This assumes that the productions generally
increase the number of vertices.

### Graph Implementation

Graph/ contains straight-forward labeled graph implementation. In the current
implementation, only vertices are labeled. It allows adding and removing
vertices and edges, as well as searching for a given subgraph.





- Need to consider numbering nodes. Otherwise how to interpret 
  `A->B ==> A->B->B` ? But this is clear: `A1->B2 ==> A1->B3->B2`
