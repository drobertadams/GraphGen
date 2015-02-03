# Procedurally Generated Graphs

## Overview

This Python program allows you to define and execute a _generative graph  grammar_. Its purpose is to programmatically generate a graph. 

The process starts with a small graph, perhaps just a single vertex `A`. Then we apply _productions_ (remember your compiler class?) of the form `LHS ==> RHS` to transform a subgraph of the current graph into a new graph. For example, the production `A ==> A->B` says to find a subgraph that consists of a single vertex `A`, and transform it by adding a new vertex `B` and connecting the two with an edge. So if we start with `A`, we would end up with `A->B`. Doing this again would result in `A->B1, A->B2` (`A` points to two new vertices with label `B`). We repeat this process until the graph is as big as you want.

This particular implementation is "context-sensitive", which means you can have more than one vertex on the LHS. So you could have the following production `A->B ==> A->C`. This would find a subgraph `A->B`, remove `B` and all edges connected to it, adds a new vertex `C`, and connect it with `A`.

## Implementation

The tool consists of a parser that reads the grammar input file, and a 
"generator" that actually applies the productions to generate a graph. Underlying everything is the [YapyGraph](https://github.com/drobertadams/YapyGraph) project that represents a directed graph and can perform subgraph (isomorphic) searches.

### Parser  Implementation

The grammar parser is implemented as a traditional top-down recursive descent
parser and associated lexer. Classes include:

- `Token` - a simple representation of a token with type and lexeme
- `Lexer` - converts the input character stream into a stream of Tokens
- `Parser` - reads the input `Token` stream from the `Lexer` and builds a dictionary of configuration options, and a list of `Production` objects
- `Production` - provides a simple representation of a graph transformation production (e.g., `A->B ==> A->C`) with member variables `lhs` and `rhs`  to represent the graph on the left-hand side and right-hand side, respectively.
  
  A sample grammar might be:

		# Sample Grammar File

		configuration {
			min_vertices = 10;
		}

		productions {
			A;	# start graph

			# Productions
			A ==> A -> B;
			A -> B ==> A -> B, A -> C;
			A -> C ==> C -> A;
		}
		


### Generator  Implementation

`Generator` is the generation engine. Given a list of
`Production` objects, and a starting graph `G`, uses graph
isomorphic searching to find instances of a LHS in `G` and transforms the LHS with the RHS.  The engine continues to randomly apply these transformations until `G` contains a given number of vertices. This assumes that the productions generally increase the number of vertices.
