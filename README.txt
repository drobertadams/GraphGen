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
- Parser
- Production
- Productions
- Configuration

### Generator Tool Implementation

Generator

Graph/ contains an implementation
