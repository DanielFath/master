##############################################################################
# Name: test_crossref.py
# Purpose: Test for verifying output the semantic verification of cross-refs
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
import pytest
from  domm.parser import DommParser
from  domm.metamodel import *

def test_simple_prop_crossref():
    exception_test = """model x
        dataType int
        package test {
            exception NanError {
                prop int id
            }
        }"""
    parsed1 = DommParser()._test_parse(exception_test)
    assert parsed1.qual_elems["int"] == DataType(name="int")
    assert parsed1.unique["int"] == "int"

    cross_ref = DommParser()._test_crossref(exception_test)
    assert cross_ref["test"]["NanError"]["id"].type_def._bound == DataType(name = "int")

    with pytest.raises(TypeNotFoundError):
        DommParser()._test_crossref("""model x
        package test {
            exception NanError {
                prop int id
            }
        }""")

    all_test = DommParser()._test_crossref("""model y
    dataType int
    package all{
        exception Error {
            prop int id
        }
        valueObject VO {
            prop int vos
        }
        entity Ent {
            key { prop int stuff}
        }
    }
    """)
    int_type = DataType(name = "int")
    assert all_test["all"]["VO"]["vos"].type_def._bound == int_type
    assert all_test["all"]["Error"]["id"].type_def._bound == int_type
    assert all_test["all"]["Ent"]["stuff"].type_def._bound == int_type

def test_simple_throw_crossref():
    exception_test = """model x
        dataType int
        package test {
            exception NanError {
                prop int id
            }

            entity Ent {
                key {
                    prop int id
                }

                op int getName() throws NanError
            }
        }"""
    parsed1 = DommParser()._test_crossref(exception_test)
    excp = parsed1["test"]["NanError"]
    assert type(excp) is ExceptionType
    assert parsed1["test"]["Ent"]["getName"].throws[0]._bound == excp

