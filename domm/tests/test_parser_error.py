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

def test_duplicate_tagtype():
    with pytest.raises(DuplicateTypeError):
        DommParser()._test_parse("model simple tagType b tagType b")
        DommParser()._test_parse("model simple validator b validator b")

def test_duplicate_enums():
    with pytest.raises(DuplicateLiteralError):
        DommParser()._test_parse("""model simple
            package test {
                enum DuplicateName {
                    red "Red"
                    red "Green"
                }
            }
        """)

def test_duplicate_valueobject():
    with pytest.raises(DuplicatePropertyError):
        DommParser()._test_parse("""model simple
            package test {
                valueObject vo {
                    prop int X
                    prop string X
                }
            }
            """)

    with pytest.raises(DuplicateConstrError):
        DommParser()._test_parse("""model simple
            package test {
                valueObject vo {
                    [test, test]
                    prop int X
                    prop string Y
                }
            }
            """)

    with pytest.raises(DuplicateDependsError):
        DommParser()._test_parse("""model simple
            package test {
                valueObject vo depends X, X, Y {
                    [test, tester("x")]
                    prop int X
                    prop string Y
                }
            }
            """)

def test_duplicated_exception():
    with pytest.raises(DuplicatePropertyError):
        DommParser()._test_parse("""model simple
            package test {
                exception ex {
                    prop int X
                    prop string X
                }
            }
            """)

def test_duplicated_service():
    with pytest.raises(DuplicateTypeError):
        DommParser()._test_parse("""model simple
            package test {
                service serv {
                    op int getName()
                    op string getName()
                }
            }
            """)

    with pytest.raises(DuplicateDependsError):
        DommParser()._test_parse("""model simple
            package test {
                service serv depends X, X {
                    op int testing()
                }
            }
            """)

    with pytest.raises(DuplicateConstrError):
        DommParser()._test_parse("""model simple
            package test {
                service serv {
                    [test, test]
                    op int getName()
                    op int testing()
                }
            }
            """)

def test_duplicate_entity():
    with pytest.raises(DuplicateFeatureError):
        DommParser()._test_parse("""model simple
            package test {
                entity ent {
                    key {
                        prop int id
                    }
                    op int id()
                }
            }""")

    with pytest.raises(DuplicateFeatureError):
        DommParser()._test_parse("""model simple
            package test {
                entity ent {
                    key {
                        prop int id
                    }
                    prop int id
                }
            }""")

    with pytest.raises(DuplicateDependsError):
        DommParser()._test_parse("""model simple
            package test {
                entity ent depends X, X {
                    key {
                        prop int id
                    }
                }
            }""")


    with pytest.raises(DuplicateConstrError):
        DommParser()._test_parse("""model simple
            package test {
                entity ent {
                    key {
                        prop int id
                    }
                    [X, X]
                }
            }""")

    with pytest.raises(DuplicateExceptionError):
        DommParser()._test_parse("""model simple
            package test {
                entity ent {
                    key {
                        prop int id
                    }

                    op string getName() throws Ex1, Ex1
                }
            }""")


def test_duplicated_package_names():
    with pytest.raises(DuplicateTypeError):
        DommParser()._test_parse("""model pack_test
            package dup {}
            package dup {}
            """)
    par = DommParser()._test_parse("""model test package not_dup {
            package not_dup {}
        }""")
    par.unique == dict()

    with pytest.raises(DuplicateTypeError):
        DommParser()._test_parse("""model dup_test
            package test {
                package inner_dup {}
               package inner_dup {}
            }""")


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

def test_duplicate_op_param():
    with pytest.raises(DuplicateParamError):
        DommParser()._test_parse("""
            model simple
            package test {
                service s1 {
                    op int getDouble(double a, double a)
                }
            }""")

    DommParser()._test_parse("""
        model simple
        package test {
            service s1 {
                op int getDouble(double a, double b)
            }
        }""")

def test_reserved_keyword():
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model dataType""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model buildinDataType""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model enum""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model tagType""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model buildinTagType""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model validatorType""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model buildinValidator""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model appliesTo""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model package""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model service""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model entity""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model extends""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model depends""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model key""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model repr""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model prop""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model ordered""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model unique""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model readonly""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model required""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model op""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model throws""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model compartment""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model valueObject""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model exception""")
    with pytest.raises(KeywordError):
        DommParser()._test_parse("""model model""")