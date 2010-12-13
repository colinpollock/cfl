#!/usr/bin/env python 

"""Manipulation of regular and context free languages."""

from pprint import pprint
import sys

import nltk
from nltk.grammar import Grammar, parse_cfg, Nonterminal


class CFLGeneration(object):
    """Random string generation from the language generated by input grammar.
    """

    def __init__(self, grammar, length=0):
        """Convert the grammar to Chomsky Normal Form and do preprocessing.
        
        `grammar` can be:
            (1) an instance of nltk.grammar.Grammar,
            (2) a string representing the path to a .cfg file, or
            (3) a string that can be parsed into a grammar by parse_cfg

        `length` is the maximum string length that should be preprocessed.
        """
        self.length = length

        # self.grammar must be instance of nltk.grammar.Grammar
        if isinstance(grammar, Grammar):
            self.grammar = grammar
        elif isinstance(grammar, str) and grammar.endswith('.cfg'):
            self.grammar = nltk.data.load('file:' + grammar)
        elif isinstance(grammar, str):
            self.grammar = parse_cfg(grammar)
        else:
            raise ValueError('Arg grammar must be nltk.grammar.Grammar or str.')
        
        if not self.grammar.is_chomsky_normal_form():
            self.grammar = convert_to_cnf(self.grammar)

        self.productions = self.grammar.productions()

        # NOTE: Is it ok to assume all nonterminals occur on a LHS?
        self.nonterminals = set([p.lhs() for p in self.productions])

        self.terminals = set()
        for prod in self.productions:
            for token in prod.rhs():
                if not isinstance(token, Nonterminal):
                    self.terminals.add(token)

        # Initialize _counts then populate it in _preprocess().
        self._counts = {}
        self._preprocess()


    def generate(self, length):
        """Return a string of length `length` that is in L(self.grammar)."""
        # Update self._counts for string lengths up to `length` if necessary.
        if length > self.length:
            self._update_counts(length)

        # TODO: GENERATION
        print >> sys.stderr, 'Calling generate with length=%d.' % length


    def _prods_by_lhs(self, lhs):
        assert isinstance(lhs, Nonterminal)
        return set([p for p in self.productions if p.lhs() == lhs])


    def _update_counts(self, new_length):
        """Extend self._counts to cover strings of length `new_length`."""
        if self.length >= new_length:
            return

        # Extend the count lists with 0s
        diff = new_length - self.length
        for key, value in self._counts.iteritems():
            value += [0 for i in range(diff)]

        for L in range(self.length, new_length + 1):
            for nonterm in self.nonterminals:
                prods = (p for p in self._prods_by_lhs(nonterm) 
                         if len(p.rhs()) == 2)

                # Handle productions of form A -> B C. Increment the count of
                # strings of length L derivable from A by the number of ways 
                # that B and C can combine to form a string of length L.
                for prod in prods:
                    B = prod.rhs()[0]
                    C = prod.rhs()[1]
                    for k in range(1, L):
                        left = self._counts[B][k]
                        right = self._counts[C][L - k]
                        self._counts[nonterm][L] = self._counts[nonterm][L] +  \
                                                   left + right

        # Check that the number of counts for a nonterminal is equal to
        # `new_length` (with 1 added for the None value). Then reset self.length
        # to reflect that.
        assert len(self._counts.itervalues().next()) == new_length + 1
        self.length = new_length

    def _preprocess(self):
        """Populate self._counts.

        _counts is a dict from nltk.grammar.Nonterminal to lists. Each index
        in the list holds the number of strings of length index that can be
        generated starting from the Nonterminal.
        """
        # Set the counts for all lengths for each nonterminal to 0.
        for nonterm in self.nonterminals:
            self._counts[nonterm] = [None] + [0 for i in range(self.length)]

        # For each production A -> 'a', increment the number of strings of
        # length one that can be generated from A.
        for prod in [p for p in self.productions if len(p.rhs()) == 1]:
            self._counts[prod.lhs()][1] += 1

        # Recursively find and set counts for lengths up to self.length
        self._update_counts(self.length)





def convert_to_cnf(grammar):
    """Return a CNF grammar that accepts the same language as `grammar`."""
    # This should be a method in nltk.grammar.
    # S
    if grammar.is_chomsky_normal_form():
        return grammar
    else:
        raise StubError("convert_to_cnf isn't complete.")



class RegexToCFG(object):
    """Conversion of basic REs to their corresponding CFGs.
    """
    
class StubError(Exception):
    pass


def main():
    generator = CFLGeneration('g.cfg', 3)
    print generator.length
    generator.generate(10)
    print generator.length
    pprint(generator._counts, indent=3)


if __name__ == '__main__':
    main()  
