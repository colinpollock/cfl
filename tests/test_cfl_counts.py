#!/usr/bin/env python

""" Test the counts for a few CNF grammars against counts I got by hand."""

import unittest

from .. import cfl


def check_grammar(generator, answers):
    for nonterm, count_list in answers.iteritems():
        for i, count in enumerate(count_list):
            if i == 0:  # Skip None value
                continue  
            assert generator.count_by_nonterm(nonterm, i) == count


def test_gen():
    pairs = [
        ("""
         S -> A X
         S -> U B
         S -> X A

         X -> A X
         X -> U B
         X -> X A

         A -> 'b'
         A -> A X
         A -> U B
         A -> X A

         B -> 'b'

         U -> 'a'
         """,
         {
          'S': [None, 0, 1, 2, 6],
          'A': [None, 1, 1, 2, 6],
          'B': [None, 1, 0, 0, 0],
          'U': [None, 1, 0, 0, 0],
          'X': [None, 0, 1, 2, 6]
         }
        ),
    ]
    for grammar, answers in pairs:
        max_str_len = len(answers.itervalues().next())
        generator = cfl.CFLGenerator(grammar, max_str_len)
        yield (check_grammar, generator, answers)




