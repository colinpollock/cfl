#!/usr/bin/env python

""" Tests for the cnf module, which converts a CFG to Chomsky Normal Form.

The individual tests are methods test_method_%d where %d is the index of a 
list of grammars. Look at the list `grammars` to figure out which one
caused the failure.

Note: the tests fail when using nose because the main test class, 
TestConversion, has its test methods added at runtime.
"""

import copy
import nose

import nltk
from nltk.grammar import Nonterminal, parse_cfg

from .. import cnf
from .. import cfl


def check_is_cnf(grammar_str):
    """Assert that the converted grammar is_cnf."""
    grammar = nltk.grammar.parse_cfg(grammar_str)
    converted = cnf.convert_to_cnf(grammar)
    assert converted.is_chomsky_normal_form()

def check_generates_same(grammar_str):
    """Checks that the original and converted grammars are the same."""
    grammar = nltk.grammar.parse_cfg(grammar_str)
    converted = cnf.convert_to_cnf(copy.deepcopy(grammar))
    #TODO: Maybe generate some strings using `grammar` then try to parse them
    # using the second grammar.
    generator = cfl.CFLGenerator(converted)
    strings = set()
    for length in range(15):
        try:
            s = generator.generate(length)
        except cfl.GenerationFailure:
            continue
        finally:
            length += 1
            
        strings.add(''.join(s))



#def test_other():
#    grammars = [ """ S -> A S A | 'a' B \n A -> B | S \n B -> 'b' | """, ]
#    for grammar in grammars:
#        yield (check_is_cnf, grammar)
#        yield (check_generates_same, grammar)

#
# Tests for whether a grammar is successfully
#
def test_already_cnf():
    grammar = """S -> A B
                 A -> 'a'
                 B -> 'b'
              """
    check_is_cnf(grammar)
    check_generates_same(grammar)

def test_not_binary():
    grammar = """S -> A B C \n A -> 'a' \n B -> 'b' \n C -> 'c' """
    check_is_cnf(grammar) 
    check_generates_same(grammar)

def test_unit_rules():
    grammars = ["""S -> A | B | C \n A -> 'a' \n B -> 'b' \n C -> 'c' """,
               ]
                """S -> A B \n A -> 'a' \n B -> """
    for grammar in grammars:
        check_is_cnf(grammar)
#        yield (check_is_cnf, grammar)
#        yield (check_generates_same, grammar)

def test_mixed_terminals():
    grammars = ["""S -> 'b' A \n A -> 'a' """,]
    for grammar in grammars:
        check_is_cnf(grammar)
#        yield (check_is_cnf, grammar)
#        yield (check_generates_same, grammar)
