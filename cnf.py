#!/usr/bin/env python

"""
to_chomsky_normal_form()
binarise()

"""

from collections import defaultdict
from copy import deepcopy
import sys
import string
from pprint import pprint

import nltk
from nltk.grammar import Nonterminal, parse_cfg, ContextFreeGrammar, Production

def _letter_gen(avoid_strings):
    """Yield 'A', 'B', ..., 'Z', 'AA', ..., 'ZZZ', ...."""

    i = 26
    while True:
        reps, index = divmod(i, 26)
        if string.ascii_uppercase[index] not in avoid_strings:
            yield string.ascii_uppercase[index] * reps
        i += 1

def _get_nonterminals(grammar):
    """Return the Nonterminal strings in `grammar` as a set."""
    nonterminals = [prod.lhs().symbol() for prod in grammar.productions()] + \
                   [tok for prod in grammar.productions() for tok in prod.rhs()
                    if isinstance(tok, Nonterminal)]
    return set(nonterminals)



def replace_rhs_terminals(input_productions, letters):
    """Return new productions "A -> B ... 'z'" to "A -> B ... Z ; Z -> 'z'"."""
    productions = deepcopy(input_productions)
    new_prods = []
    delete_prods = []
    # TODO: do a listcomp first then act on all the results
    for prod in productions:
        # We don't care about rules like "A -> B", "A -> 'b'", "A -> B C D".
        if all([isinstance(token, Nonterminal) for token in prod.rhs()]) or  \
                len(prod.rhs()) < 2: 
            continue

        # Add rule U -> 'a' and replace rule B -> A..'a' with B -> A..U for each
        # nonterminal 'a' on a RHS.
        lhs = prod.lhs()
        rhs = []
        for token in prod.rhs():
            if isinstance(token, str):
                nonterm = Nonterminal(letters.next())
                new_prod = Production(nonterm, [token])
                new_prods.append(new_prod)
                rhs.append(nonterm)
            else:
                rhs.append(token)
        delete_prods.append(prod)
        new_prods.append(Production(lhs, rhs))

    remove_all(productions, *delete_prods)
    productions += new_prods
    return productions

#### STEP 2 ####
def _binarize(input_productions, letters):
    """Convert "A -> B C D" to "A -> B X ; X -> C D

    For each production with more than two nonterminals on its rhs, replace
    it with a set of binary rules.
    """
    productions = deepcopy(input_productions)

    #TODO: what about duplicate productions?
    new_prods = []
    too_long = [prod for prod in productions if len(prod.rhs()) > 2]
    for prod in too_long:
        lhs = prod.lhs()
        for token in prod.rhs()[:-2]:
            new = Nonterminal(letters.next())
            new_prods.append(Production(lhs, [token, new]))
            lhs = new

        new_prods.append(Production(lhs, [prod.rhs()[-2], prod.rhs()[-1]]))

    productions += new_prods
    remove_all(productions, *too_long)
    return productions


# STEP 3 #
def _replace_start(productions, letters):
    """Replace start symbol S with S0 and add "S0 -> S."""
    pass

# STEP 4 #
def _remove_empty_productions(input_productions, letters):
    """Remove productions with empty right hand sides."""
    copied_prods = deepcopy(input_productions)
    

    #
    # Find all nonterminals that generate the emptry string.
    #
    # Basis: A nonterminal generates the empty string if it is the LHS of a
    # production thats RHS is empty.
    gen_empty = [prod.lhs() for prod in copied_prods
                 if len(prod.rhs()) == 0]
    N = len(gen_empty)

    # Induction:
    while True:
        for nonterm in gen_empty:
            for prod in copied_prods:
                if nonterm in prod.rhs():
                    better = list(prod.rhs())
                    better.remove(nonterm)
                    prod._rhs = tuple(better)

        gen_empty[:] = [prod.lhs() for prod in copied_prods 
                     if len(prod.rhs()) == 0]
        new_len = len(gen_empty)
        if new_len == N:
            break
        N = new_len

    print 'gen_empty', gen_empty
    # ADD NEW RULES
    new_prods = []
    productions = deepcopy(input_productions)
    for nonterm in gen_empty: 
        prods = [prod for prod in productions
                 if len(prod.rhs()) == 2 and nonterm in prod.rhs()]
        for prod in prods:
            rhs = list(prod.rhs())
            while nonterm in rhs:
                lhs = prod.lhs()
                rhs.remove(nonterm)
                p = Production(lhs, tuple(rhs))
                new_prods.append(p)
            
        
    productions += new_prods
    productions[:] = [p for p in productions if p.rhs()]
    return productions


def _get_unit_productions(productions):
    return [p for p in productions if len(p.rhs()) == 1 and isinstance(p.rhs()[0], Nonterminal)]


# STEP 5 #
def _remove_unit_productions(input_productions, letters):
    """Return a list of Productions without unit productions. TODO"""
    # Basis step. Add (A, A) for all nonterminals A
    #TODO: is it ok to ignore NTs on RHS?
    productions = deepcopy(input_productions)
    unit_pairs = defaultdict(set)
    nonterminals = [p.lhs() for p in productions]
    for nt in nonterminals:
        unit_pairs[nt].add(nt)

    # Induction
    #TODO: keep doing this until no more are added?
    for prod in _get_unit_productions(productions):
        first = prod.lhs()
        (second,) = prod.rhs()
        As = unit_pairs[first]
        for A in As:
            unit_pairs[second].add(A)

    NEW = set()
    for (RHS, LHSides) in unit_pairs.iteritems():
        for LHS in LHSides:
            for prod in productions:
                if prod.lhs() == RHS:
                    if isinstance(prod.rhs()[0], basestring) or len(prod.rhs()) > 1:
                        P = Production(LHS, prod.rhs())
                        NEW.add(P)
    return NEW

def convert_to_cnf(input_grammar):
    """Return a new CNF grammar that accepts the same language as `grammar`."""

    if input_grammar.is_chomsky_normal_form():
        print >> sys.stderr, "Already CNF"
        return deepcopy(input_grammar)

    productions = deepcopy(input_grammar.productions())
    letters = _letter_gen(_get_nonterminals(input_grammar)) 

    # Replace RHS Terminals
    productions = replace_rhs_terminals(productions, letters)
    for prod in productions:
        assert all([isinstance(token, Nonterminal) for token in prod.rhs() 
                    if len(prod.rhs()) > 1])

    # Binarize rules
    productions = _binarize(productions, letters)
    for prod in productions:
        assert len(prod.rhs()) <= 2

    # Remove empty productions
    productions = _remove_empty_productions(productions, letters)
    print "POST EMPTY"
    print productions
    print

    # Remove unit productions
    new_prods = _remove_unit_productions(productions, letters)

    gram = ContextFreeGrammar(input_grammar.start(), new_prods)
    return gram




def convert(filename):
    grammar = nltk.data.load('file:%s' % filename)
    print '*' * 10,
    print 'INITIALLY'
    print grammar
    print "CNF:", grammar.is_chomsky_normal_form()
    print '*' * 10
    converted = convert_to_cnf(grammar)
    print 'CONVERTED:', converted
    print "CNF:", converted.is_chomsky_normal_form()


def remove_all(the_list, *args):
    for arg in args:
        while arg in the_list:
            the_list.remove(arg)

if __name__ == '__main__':
    convert(sys.argv[1])
