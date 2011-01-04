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

def _letter_gen(grammar):
    """Yield 'A', 'B', ..., 'Z', 'AA', ..., 'ZZZ', ...."""
    nonterminals = [prod.lhs().symbol() for prod in grammar.productions()] + \
                   [tok for prod in grammar.productions() for tok in prod.rhs()
                    if isinstance(tok, Nonterminal)]
    nonterminals = set(nonterminals)

    i = 26
    while True:
        reps, index = divmod(i, 26)
        if string.ascii_uppercase[index] not in nonterminals:
            yield string.ascii_uppercase[index] * reps
        i += 1


def replace_rhs_terminals(productions, letters):
    """Change productions "A -> B ... 'z'" to "A -> B ... Z ; Z -> 'z'"."""
    new_prods = []
    delete_prods = []
    # TODO: do a listcomp first then act on all the results
    for prod in productions:
        if all([isinstance(token, Nonterminal) for token in prod.rhs()]) or  \
                len(prod.rhs()) < 2: #TODO: how should I indent here?
            continue

        # Add rule U -> 'a' and replace rule B -> A..'a' with B -> A..U
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

#### STEP 2 ####
def _binarize(productions, letters):
    """Convert "A -> B C D" to "A -> B X ; X -> C D

    For each production with more than two nonterminals on its rhs, replace
    it with a set of binary rules."""

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


# STEP 3 #
def _replace_start(productions, letters):
    """Replace start symbol S with S0 and add "S0 -> S."""
    pass

# STEP 4 #
def _remove_empty_productions(productions, letters):
    """Remove productions with empty right hand sides."""
    copied_prods = deepcopy(productions)

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

        gen_empty = [prod.lhs() for prod in copied_prods if len(prod.rhs()) == 0]
        new_len = len(gen_empty)
        if new_len == N:
            break
        N = new_len

    # ADD NEW RULES
    #print '\n\nADDING NEW RULES'
    new_prods = []

    #productions[:] = input_productions
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


def _unit_productions(productions):
    return [p for p in productions if len(p.rhs()) == 1 and isinstance(p.rhs()[0], Nonterminal)]


# STEP 5 #
def _remove_unit_productions(productions, letters):
    """Return a list of Productions without unit productions. TODO"""
    # Basis step. Add (A, A) for all nonterminals A
    #TODO: is it ok to ignore NTs on RHS?
    #print "REMOVE UNIT PRODUCTIONS"
    #print productions
    unit_pairs = defaultdict(set)
    nonterminals = [p.lhs() for p in productions]
    for nt in nonterminals:
        unit_pairs[nt].add(nt)

    # Induction
    #TODO: keep doing this until no more are added?
    for prod in _unit_productions(productions):
        first = prod.lhs()
        (second,) = prod.rhs()
        As = unit_pairs[first]
        for A in As:
            unit_pairs[second].add(A)
    #print unit_pairs
    #
    # Remove Unit Pairs
    #
    NEW = set()
    #for rhs, lhsides in unit_pairs.iteritems():
    #    for lhs in lhsides:
    #        new_prods = [prod for prod in productions
    #                    if len(prod.rhs()) > 1 and prod.lhs() == rhs]
    #        #print "%s -> %s" % (lhs, rhs),
    #        #print new_prods
    #        for prod in new_prods:
    #            p = Production(lhs, prod.rhs())
    #            NEW.append(p)
    #print unit_pairs
    #print
    for (RHS, LHSides) in unit_pairs.iteritems():
        for LHS in LHSides:
            #print
            #print '(%s, %s)' % (LHS, RHS)
            #print type(LHS), type(RHS)
            #print productions

            for prod in productions:
            #    print 'prod:', prod
                if prod.lhs() == RHS:
            #        print '  match for RHS'
                    if isinstance(prod.rhs()[0], basestring) or len(prod.rhs()) > 1:
            #            print 
            #            print '  GOOD PROD', prod
                        P = Production(LHS, prod.rhs())
            #            print '  ADDING', P
                        NEW.add(P)
                    else:
                        pass
            #            print '  BAD PROD'
                else:
                    pass
                    #print '  no match for RHS'

    return NEW

    #print NEW
#    productions += NEW
#    productions[:] = list(set([p for p in productions 
#                if len(p.rhs()) > 1 or isinstance(p.rhs()[0], basestring)]))


def convert_to_cnf(input_grammar):
    """Return a CNF grammar that accepts the same language as `grammar`."""
    grammar = deepcopy(input_grammar)

    if grammar.is_chomsky_normal_form():
        print >> sys.stderr, "Already CNF"
        return grammar

    letters = _letter_gen(grammar) # sequential letter generator
    productions = grammar.productions()

    # Replace RHS Terminals
    replace_rhs_terminals(productions, letters)
    for prod in productions:
        assert all([isinstance(token, Nonterminal) for token in prod.rhs() 
                    if len(prod.rhs()) > 1])


    # Binarize rules
    _binarize(productions, letters)
    for prod in productions:
        assert len(prod.rhs()) <= 2

    #TODO: is this necessary? why can't S be on rhs?
    #_replace_start(productions, letters)


    # Remove empty productions
    _remove_empty_productions(productions, letters)


    # Remove unit productions
    new_prods = _remove_unit_productions(productions, letters)
    #TODO: the problem is here. it's messing up the rule S -> A in empty.cfg

    # Recalculate forms, including is_cnf
    #print; print
    #print new_prods
    gram = ContextFreeGrammar(grammar.start(), new_prods)
    return gram
#    grammar._calculate_grammar_forms()
#    return grammar




def convert(filename):
    grammar = nltk.data.load('file:%s' % filename)
    print '*' * 10,
    print 'INITIALLY'
    print grammar
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
