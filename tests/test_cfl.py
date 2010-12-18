
"""
Test various CFLGeneration methods.
"""

import nose

from nltk.grammar import parse_cfg

from .. import cfl

class TestInit(object):
    """Test various initialization methods."""

    def test_no_len(self):
        """Tests loading Generator without specifying length."""
        cfl.CFLGenerator("""S -> 'a'""")
        
    def test_len10(self):
        """Tests loading Generator with large length."""
        cfl.CFLGenerator("""S -> 'a'""", length=10)

    @nose.tools.raises(ValueError)
    def test_neg_len(self):
        """Should fail since length must be positive."""
        cfl.CFLGenerator("""S -> 'a'""", -1)

    def test_from_file(self):
        """Test loading CFG from file."""
        cfl.CFLGenerator('cnf1.cfg')
        
    def test_from_cfg(self):
        grammar = parse_cfg("""S -> 's' | A B\n A -> 'a'\n B -> 'b'""")
