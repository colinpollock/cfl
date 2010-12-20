#!/usr/bin/env python 

"""Manipulation of regular and context free languages."""

from __future__ import division

from optparse import OptionParser
import random
import simplejson
import sys

import nltk
from nltk.grammar import parse_cfg, Nonterminal, ContextFreeGrammar, Production

from cnf import convert_to_cnf

class CFLGenerator(object):
    """Random string generation from the language generated by input grammar.
    """

    def __init__(self, grammar, length=1):
        """Convert the grammar to Chomsky Normal Form and do preprocessing.
        
        `grammar` can be:
            (1) an instance of nltk.grammar.ContextFreeGrammar,
            (2) a string representing the path to a .cfg file, or
            (3) a string that can be parsed into a grammar by parse_cfg

        `length` is the maximum string length that should be preprocessed.
        """
        if length < 1:
            raise ValueError('length must be greater than 0.')

        # self.grammar must be instance of nltk.grammar.Grammar
        if isinstance(grammar, ContextFreeGrammar): 
            self.grammar = grammar
        elif isinstance(grammar, str) and grammar.endswith('.cfg'):
            self.grammar = nltk.data.load('file:' + grammar)
        elif isinstance(grammar, str):
            self.grammar = parse_cfg(grammar)
        else:
            raise ValueError('Arg grammar must be nltk.grammar.Grammar or str.')
        
        if not self.grammar.is_chomsky_normal_form():
            raise ValueError('Input grammar must be in CNF '
                             '(conversion method isn\'t implemented)')
            #convert_to_cnf(self.grammar)

        self.productions = self.grammar.productions()

        # TODO: Is it ok to assume all nonterminals occur on a LHS?
        # Technically yes, but check whether nltk's is_cnf ensures it.
        self.nonterminals = set([p.lhs() for p in self.productions])

        self.terminals = set([token for prod in self.productions 
                              for token in prod.rhs()
                              if not isinstance(token, Nonterminal)])

        # Initialize self._counts then populate it in _preprocess(). 
        # self.length is the string length that has been preprocessed.
        self._counts = {}
        self.length = 0
        self._preprocess(length)


    def __repr__(self):
        return "CFLGenerator(%s)" % str(self.grammar)
        
    def count_by_nonterm(self, nonterm, length):
        """Return number of strings of length `length` derivable from `nonterm`.
        """
        if isinstance(nonterm, basestring):
            nts = [nt for nt in self.nonterminals if nt.symbol() == nonterm]
            if not nts:
                raise KeyError("nonterm isn't in grammar.")
                #TODO: subclass Exception and print the missing nonterm
            (nonterm,) = nts
        return self._counts[nonterm][length]

    def count_by_prod(self, prod, length):
        """Return the number of strings of length `length` derivable from the
        RHS of `prod`."""
        assert isinstance(prod, Production)
        assert len(prod.rhs()) < 3

        if isinstance(prod.rhs()[0], basestring):
            if length == 1:
                return 1
            else:
                return 0

        left, right = prod.rhs()[0], prod.rhs()[1]
        return sum([self.count_by_nonterm(left, k) *  
                    self.count_by_nonterm(right, length - k)
                    for k in range(1, length)])


    def generate(self, length):
        """Return a string of length `length` that is in L(self.grammar).
        
        Raise GenerationFailure if no strings of the requested length can be 
        generated.
        """
        # Update self._counts for string lengths up to `length` if necessary.
        if length > self.length:
            self._update_counts(length)

        start = self.grammar.start()
        return self._generate_rec(start, length)


    def _generate_rec(self, nonterm, length):
        """Recursive workhorse for generate method.

        Return a list of length `length`, where the `length` items are terminals
        of a tree rooted at `nonterm`.
        """
        # The recursion bottoms out when the method attempts to find subtree 
        # that yields a single terminals. At this point, a terminal is chosen
        # randomly and returned as the single element in a list.
        if length == 1:
            productions = self._prods_by_lhs(nonterm)
            terminals = [p.rhs()[0] for p in productions if len(p.rhs()) == 1]
            if productions and not terminals:
                raise GenerationFailure(length)
            choice = random.choice(terminals)
            return [choice]

        # Find all productions that have `nonterm` as the LHS. Choose one of
        # them randomly by setting the probability of each production being 
        # chosen as the number of strings derivable from the production's RHS
        # divided by the number of strings derivable from the LHS.
        productions = [prod for prod in self._prods_by_lhs(nonterm)
                       if self.count_by_prod(prod, length) > 0]
        if not productions:
            raise GenerationFailure(length)

        # TODO: See if listcomp version is fast enough to compensate  for its 
        #       ugliness
        probabilities = []
        for prod in productions:
            numerator = self.count_by_prod(prod, length)
            denominator = self.count_by_nonterm(prod.lhs(), length)
            if denominator != 0: 
                probabilities.append(numerator / denominator)
        production = _choose(zip(productions, probabilities))
        
        # For each call to _generate_rec, the input length needs to be split up
        # into two smaller lengths so that when the method is called recursively
        # twice, the length of the two results will equal the length of their
        # parent. 
        first, second = production.rhs()[0], production.rhs()[1]
        split_probs = [(k, self.count_by_nonterm(first, k) * 
                       self.count_by_nonterm(second, length - k) / 
                       self.count_by_prod(production, length))
                       for k in range(1, length)
                      ]
        assert split_probs
        split = _choose(split_probs)

        left = self._generate_rec(production.rhs()[0], split)
        right = self._generate_rec(production.rhs()[1], length - split)
        return left + right



    def _prods_by_lhs(self, lhs):
        assert isinstance(lhs, Nonterminal)
        return set([p for p in self.productions if p.lhs() == lhs])


    def _update_counts(self, new_length):
        """Extend self._counts to cover strings of length `new_length`."""
        assert self.length <= max([new_length, 1])

        # Extend the count lists with 0s
        diff = new_length - self.length
        for value in self._counts.itervalues():
            value += [0 for i in range(diff)]

        for L in range(self.length + 1, new_length + 1):
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
                                                   left * right

        # Check that the number of counts for a nonterminal is equal to
        # `new_length` (with 1 added for the None value). Then reset self.length
        # to reflect that.
        assert len(self._counts.itervalues().next()) == new_length + 1
        self.length = new_length

    def _preprocess(self, length):
        """Populate self._counts.

        _counts is a dict from nltk.grammar.Nonterminal to lists. Each index
        in the list holds the number of strings of length index that can be
        generated starting from the Nonterminal.
        """
        # Set the 0th value of self._counts to None since these values should
        # never be used. The lists need to be initialized so they can be used
        # below.
        for nonterm in self.nonterminals:
            self._counts[nonterm] = [None, 0]
        self.length = 1

        # For each production A -> 'a', increment the number of strings of
        # length one that can be generated from A.
        for prod in [p for p in self.productions if len(p.rhs()) == 1]:
            self._counts[prod.lhs()][1] += 1

        # Recursively find and set counts for lengths up to `length`
        self._update_counts(length)


class GenerationFailure(Exception):
    """Raised when a grammar can't generate a string of the requested length."""
    def __init__(self, length):
        self.length = length

    def __str__(self):
        return "GenerationFailure: length %d" % self.length


def _choose(pairs):
    """Choose at random from items and their probabilities of being chosen.

    pairs = [(item, probability), ...]
    """
    assert pairs
    the_sum = sum([pair[1] for pair in pairs])
    if the_sum == 0:
        return None

    # Allow a range since floats aren't exact.
    if not .99 < the_sum < 1.01:
        raise ValueError('Probabilities must add to 1.')
    r = random.uniform(0, the_sum)
    current = 0
    for (item, prob) in pairs:
        current += prob
        if r <= current:
            return item
     

class RegexToCFG(object):
    """Conversion of basic REs to their corresponding CFGs.
    """
    

def main(argv):
    """
    python cfl.py gram.cfg --number 100 --length 4
    python cfl.py gram.cfg --number 47 --lowerlength 4 --upperlength 10
    """
    # args are grammar files
    # option for length, defaults to random number between 1 and 10
    # option for number of strings to generate, default=1
    # option for output: to string, json, ...?
    parser = OptionParser()
    parser.add_option('-n', '--number', dest='number', action='store', 
                      default=1, metavar='<NUMBER>', type='int',
                      help='')
    parser.add_option('-l', '--length', dest='length', action='store', 
                       default=None, metavar='<STRING LENGTH>', type='int',
                       help='')
    parser.add_option('-f', '--format', action='store', default='string', 
                      metavar='<FORMAT>', dest='the_format', 
                      help="Output format. Must be 'json' or 'string'.")
    parser.add_option('-o', '--outfile', action='store', default='-',
                      metavar='<FILENAME>', 
                      help="Filename of output. Defaults to stdout ('-').")

    options, args = parser.parse_args(argv)
    if options.the_format not in ('string', 'json'):
        parser.error("Argument of option --fmrat must be 'string' or 'json'.")

    if options.outfile == '-':
        out = sys.stdout
    else:
        out = open(options.outfile, 'w')

    if len(args) != 1: 
        parser.error("Only one grammar can be used.")
    results = []
    if options.length:
        length = lambda: options.length
        generator = CFLGenerator(args[0], options.length)
    else:
        length = lambda: random.randint(1, 10)
        generator = CFLGenerator(args[0], 10)
    results = [generator.generate(length()) for i in range(options.number)]
    if options.the_format == 'string':
        for res in results:
            print >> out, res
    elif options.the_format == 'json':
        print >> out, simplejson.dumps(results)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))

