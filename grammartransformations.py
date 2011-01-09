
"""A collection of functions for transforming grammars.

TODO:
  Is there a way to modify the grammar in place if I need to change the start
  state? I could access grammar._start. Ask StackOverflow question about refs.

  Maybe I should just return a new grammar. The class could keep track of the
  Start symbol and the productions and then when get_grammar() is called, a 
  grammar can be created at that point.
"""

from copy import deepcopy

from nltk.grammar import ContextFreeGrammar, Nonterminal

def convert_to_chomsky_normal_form(grammar):
    grammar_trans = GrammarTransformations(grammar)
    grammar_trans.convert_to_cnf()
    return grammar_trans.get_grammar()

class GrammarTransformations(object):
    def __init__(self, grammar):
        self.start = deepcopy(grammar.start())
        self.productions = deepcopy(grammar.productions())
        self._all_symbols = _get_all_symbols(self.productions)
        self._letter_generator = _letter_generator(self.all_symbols)

    @property
    def all_symbols(self):
        """Return all symbols in `self.productions`."""
    @property
    def nonterminals(self):
        pass

    @property
    def terminals(self):
        return [[tok for tok in prod] for prod in self.productions
                 if isinstance(tok, Nonterminal)]

    def get_grammar(self):
        return ContextFreeGrammar(self.start, self.productions)

    def convert_to_cnf(self):
        if self.grammar.is_chomsky_normal_form():
            return
        self.replace_rhs_terminals()
        self.convert_to_binary()
        self.remove_empty_productions()
        self.remove_unit_productions()


    def replace_rhs_terminals(self): pass
    def convert_to_binary(self): pass
    def remove_empty_productions(self): pass
    def remove_unit_productions(self): pass



    # _symbols(self)  ???
    def remove_unreachable(self): pass
    def remove_nongenerating(self): pass
    def remove_useless(self): pass

    @property
    def useless_symbols(self): pass
    @property
    def nongenerating_symbols(self): pass
    @property
    def nonreachable_symbols(self): pass

#
# Utility stuff
#
def letter_generator(letters_to_avoid=None):
    assert False, "INCOMPLETE"

def demo():
    pass

if __name__ == '__main__':
    demo()
