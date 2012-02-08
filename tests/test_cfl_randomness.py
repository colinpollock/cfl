
"""
Tests randomness of the GFGGenerator.generate method.

When given an unambiguous input grammar, all strings should be generated at the
same frequency. To test this, a number of unambiguous grammars are passed
to cfl.CFLGenera

Note that a failure here doesn't necessarily mean there's a problem since 
there's a small chance something unlikely happened.

"""

from __future__ import division

from collections import defaultdict
import random

from .. import cfl


def check_grammar(generator, length):
    """Generate a lot of strings, make sure they are roughly as likely."""
    results = defaultdict(int)
    # TODO: See when the probability converges. Use it to choose the number
    #       of iterations. I could monitor the changes in probabilities while
    #       going through the loop. Or maybe just base it on an estimate of the
    #       number of strings that can be generated. For now 10k should work
    #       most of the time.
    N = 2000
    for i in range(N):
        try:
            string_ = ''.join(generator.generate(length))
        except cfl.GenerationFailure:
            # Skip this grammar since it can't generate strings of the required
            # length and it can't help test randomness.
            return
        results[string_] += 1

    total = sum(results.values())
    average = total / len(results)
    expected_probability = average / total
    for string_, count in results.iteritems():
        probability = count / total
        diff = abs(expected_probability - probability)
        assert diff < .03

def test_gen():
    grammars = [
        """S -> A B
           A -> A C
           A -> 'a'
           B -> B D
           B -> 'b'
           C -> 'c'
           D -> 'd'

        """,
    ]
    for gram in grammars:
        generator = cfl.CFLGenerator(gram, 10)
        for i in range(1, 11):
            yield (check_grammar, generator, i)
