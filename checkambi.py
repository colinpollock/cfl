#!/usr/bin/env python

"""Script for approximating whether a grammar is ambiguous."""

from __future__ import division

from collections import defaultdict
import random
import sys

from cfl import CFLGenerator, GenerationFailure


#TODO: Split most of check_ambiguity() off into a function that tests ambiguity 
#      for strings of one length. Then call that function with different 
#      lengths. The number of strings to generate for each length should depend
#      on how quickly the probabilities converge.

#TODO: Add main program with options for types of output. Tables of 
#      probabilities, significance, just 'yes'/'no', etc..

def check_ambiguity(grammar):
    """Print the approximated probabilities of each string in L(`grammar`)."""
    results = defaultdict(int)
    generator = CFLGenerator(grammar)
    while True:
        try:
            length = random.randint(1, 10)
            strings = make_strings(generator, 1000, length)
        except GenerationFailure:
            continue
        else:
            break
    for string_ in strings:
        results[string_] += 1

    total_count = sum(results.values())
    average_count = total_count / len(results)
    expected_probability = average_count / total_count
    print ("Expected probability of each string if grammar is unambiguous: "
           "%.2f." % expected_probability)

    for string_, count in results.iteritems():
        actual_probability = count / total_count
        print "'%s' occurs with probability %.2f" \
              % (string_, actual_probability)

def make_strings(generator, count, length):
    """Generate and return a list of `count` strings of length `length`."""
    return [generator.generate(length) for i in range(count)]


if __name__ == '__main__':
    check_ambiguity(sys.argv[1])
