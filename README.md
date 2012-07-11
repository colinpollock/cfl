Context Free Language Projects
==============================

CFLGenerator
----------------
  cfl.CFLGenerator is initialized with a grammar (in the form required by NLTK's
  grammar module). Its method generate(length) returns a string of the requested
  length that is derivable from the grammar.

  If the input grammar is unambiguous then all strings in the grammar have an
  equal probability of being generated. This is accomplished by using the
  algorithm described in Mairson 1994.

Related Projects
----------------
* A regular expression tester. Present the user with a set of positive examples
  and a set of negative examples of some RE and ask the user for an RE that
  matches the former but not the latter. 

  I'm generating a random (traditional) regular expression by generating random
  strings from a grammar for regular expressions (an example of a production is
  "X -> ATOM '*'"). Then I'm modifying the syntax tree of the first regular 
  expression to get a second RE. Then I can convert the REs to CFGs, and then 
  generate strings from them.

* Generate random strings matching a non-traditional RE (e.g. a Perl or Python
  RE). Perl has a module for this, and I found a C program that does it. The 
  challenge will basically be converting Python REs to CFGs so I can use
  the generator.

* Generate random Python programs. I can convert Python's official grammar to
  a CFG usable by NLTK and use the generator to get a random abstract syntax
  tree. The main problem is making sure the program is valid (e.g. not calling
  functions when none have been defined, making sure identifiers are valid).
  This might not go anywhere.

* Grammar ambiguity tester. The generator generates all strings in the input 
  grammar's language with the same probability. So, I can generate a bunch of
  random strings and see if each string occurs with roughly the same frequency.
  I just have to find a way to know when the probabilities have converged enough
  to make the judgment.
  See checkambi.py for a beginning.
  
