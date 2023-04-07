# GraphGen : Procedurally Generated Graphs

# Current Progress

- Refactoring Generator and its unit test
  
# Overview

GraphGen allows you to define and execute a _generative graph grammar_. Its purpose is to programmatically generate a graph. 

The process usually starts with a small graph, perhaps just a single vertex `A`. Then we apply _productions_ (remember your compiler class?) of the form `LHS ==> RHS` to transform a subgraph of the current graph into a new graph. For example, the production `A ==> A->B` says to find a subgraph that consists of a single vertex `A`, and transform it by adding a new vertex `B` and connecting the two with an edge. So if we start with `A`, we would end up with $A \rightarrow B$. Doing this again would result in $A \rightarrow B_1,B_2$ (`A` points to two vertices with label `B`). We repeat this process until the graph is as big as you want.

The implementation is "context-sensitive", which means you can have more than one vertex on the LHS. So you could have the following production `A->B ==> A->C`. This would find a subgraph $A \rightarrow B$, remove `B` and all edges connected to it, add a new vertex `C`, and connect it to `A`.

# Graph Transformation Semantics

It is important to understand how transformations are applied, as expressed by the productions. This is done in two parts: determining _vertex equivalence_ between the LHS and RHS, and then applying transformations to convert the LHS subgraph into the RHS.

## Vertex Equivalence

Given a production with a LHS graph and a RHS graph, the first step is to determine which vertices appear on both sides, and which appear on only one. 

Vertices can be identified in three ways. First, a vertex can have an alphabetic _label_ (e.g., `A`). Second, a vertex can have a _number_ (e.g., 
`1`). Third, both the label and number can be concatenated to form a vertex's _name_ (e.g., `A1`).

We say that two vertex identifiers are _equivalent_ if they refer to the same vertex. We define vertex equivalence by the following logic: If any vertex in the LHS or RHS has a number, then the vertex *names* are used to determine vertex equivalence, otherwise only the vertex *label* is used. For example...

1. `A ==> A`  : no vertex numbers; both A's are equivalent
2. `A1 ==> A` : vertex numbers are used; the `A` on the LHS is different than the `A` on the RHS
3. `A ==> A1` : vertex numbers are used; the `A` on the LHS is different than the `A` on the RHS
4. `A1 ==> A1` : vertex numbers are used, and the vertex names are the same, so both vertices are equivalent

## Graph Transformations

With the above definition of equivalence, we can then describe our model of graph transformation. 

1. Given a graph _G_ and a production _P_, determine if the LHS of _P_ can be found in _G_. If the LHS can't be found, no transformation takes place.
2. Delete from _G_ any vertex or edge that appears on the LHS that does not appear on the RHS.
	* E.g., Given the production `A->B ==> A`, vertex `B` would be deleted from _G_.
	* E.g., Given the production `A->B ==> A,B`, the edge between `A` and `B` would be deleted from _G_.
3. Add to _G_ any vertex or edge that appears on the RHS that does not appear on the LHS
	* E.g., Given the production `A ==> A,B`, vertex `B` would be added to _G_ without an edge between them.
	* E.g., Given the production `A ==> A->B`, vertex `B` and the edge between `A` and `B` would be added to _G_.

As a more complex example, consider the following production `A1->A2 ==> A1->A->A2`. This would find an occurrence of `A->A` in _G_ 
and insert a new vertex with label `A` between them.

## Grammar Specification

Graph transformations are specified in a graph grammar file. A simple grammar might be:

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

The `configuration` section currently supports one mandatory parameter `min_vertices`. This specifies when the transformation engine stops applying productions: when the resulting graph has at least the number of vertices given. In the example above, transformations are applied until the graph has at least 10 vertices. Be aware that it is generally assumed that productions add vertices, otherwise the transformation engine could enter an infinite loop.

The `productions` section specifies the starting graph and the set of productions to apply. The first graph in the `productions` section is the starting graph. All other lines should be of the form `LHS ==> RHS` where `LHS` gives the subgraph to search for and `RHS` gives the resulting subgraph.

## Graph Language 

The starting graph and the production graphs are specified using a language based roughly on the [dot language](http://www.graphviz.org/content/dot-language) that is part of [Graphviz](http://www.graphviz.org/).

Graph vertices are specified by a text label followed by an optional number. Edges are specified by a single arrow `->`. Chains of vertices can be described by linking vertices with arrows like this: `A->B->C->D->...`. Commas separate "clauses" or separate chains of vertices. So `A->B,A->C` says that vertex `A` points to both vertex `B` and `C`.

# Usage

You can use GraphGen either on the command line or programmatically. On the command line you may simply type `python Generator.py GRAMMAR_FILE`. This will generate a graph based on the information from the given grammar file. Alternatively, you may use GraphGen by instantiating `Generator` in your own Python program and then invoking its methods.

# Implementation

GraphGen consists of a parser that reads the grammar input file, and a "generator" that actually applies the productions to generate a graph. Underlying everything is the [YapyGraph](https://github.com/drobertadams/YapyGraph) project that represents a directed graph and can perform subgraph (isomorphic) searches.

## Parser Implementation

The grammar parser is implemented as a traditional top-down recursive descent parser and associated lexer. Classes include:

- `Token` - a simple representation of a token with type and lexeme
- `Lexer` - converts the input character stream into a stream of Tokens
- `Parser` - reads the input `Token` stream from the `Lexer` and builds a dictionary of configuration options, and a list of `Production` objects
- `Production` - provides a simple representation of a graph transformation production (e.g., `A->B ==> A->C`) with member variables `lhs` and `rhs`  to represent the graph on the left-hand side and right-hand side, respectively.

## Generator  Implementation

`Generator` is the generation engine. Given a list of `Production` objects, and a starting graph `G`, uses graph isomorphic searching to find an instance of a LHS in `G` and transforms the LHS with the RHS.  The engine continues to randomly apply these transformations until `G` contains a given number of vertices. This assumes that the productions generally increase the number of vertices.

# Unit Tests

`nosetests --with-path=YapyGraph/src tests/FILENAME`

`nosetest tests/FILENAME` to run a test.

# Setup

1. `git clone` this repo
2. Create a virtual environment: `python3 -m venv PATH_TO_GRAPHGEN`
3. `cd PATH_TO_GRAPHGEN`
4. "Activate" the venv: `source bin/activate`
5. Install nose: `pip install nose`