##############################################################################
# Name: test_parser_errors.py
# Purpose: Test for correct parser error behavior.
#           Tests verify that when needed semantic information is missing,
#           the parser will complain. For example duplicate property names are
#           allowed by grammar but not by Semantic.
#           Note: We are not testing for correct syntax. We assume Arpeggio will
#               parse the code correctly.
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
import pytest
from  arpeggio import NoMatch
from  domm.error import DuplicateTypeError, DuplicateFeatureError
from  domm.parser import DommParser
from  domm.metamodel import *

def test_empty():
    with pytest.raises(NoMatch):
        DommParser().parse("")

def test_duplicate_datatype():
    with pytest.raises(DuplicateTypeError):
        DommParser()._test_parse("model simple dataType a dataType a")

def test_duplicate_prop_name_in_entity():
    with pytest.raises(DuplicateFeatureError):
        DommParser()._test_parse("""model simple package test {
                entity test {
                    key { prop int id}
                    prop string X
                    prop int X
                }
            }""")

    with pytest.raises(DuplicateFeatureError):
        DommParser()._test_parse("""model simple package test {
                entity test {
                    key { prop int id}
                    prop int id
                }
            }""")

