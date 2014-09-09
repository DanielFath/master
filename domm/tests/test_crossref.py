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

    with pytest.raises(TypeNotFoundError):
        parsederr = DommParser()._test_crossref("""model x
            dataType int
            package test {
                entity Ent {
                    key {
                        prop int id
                    }

                    op int getName() throws NanError
                }
            }""")

def test_extends():
    ext_test = """
    model x
    dataType int
    package test {
        valueObject Vo1 {
            prop int vos
        }

        valueObject Vo2 extends Vo1 {
            prop int stuff
        }

        service serv1 {
            op int getCode()
        }

        service serv2 extends serv1 {
            op int getStuff()
        }

        entity ent1 {
            key { prop int code}
        }

        entity ent2 extends ent1 {
            key { prop int code2}
        }
    }
    """
    parsed1 = DommParser()._test_crossref(ext_test)
    ext_vo = parsed1["test"]["Vo2"].extends
    vo1 = parsed1["test"]["Vo1"]
    assert type(ext_vo) is CrossRef
    assert type(vo1) is ValueObject
    assert ext_vo._bound == vo1

    ext_serv = parsed1["test"]["serv2"].extends
    serv1 = parsed1["test"]["serv1"]
    assert type(ext_serv) is CrossRef
    assert type(serv1) is Service
    assert ext_serv._bound == serv1

    ext_ent = parsed1["test"]["ent2"].extends
    ent1 = parsed1["test"]["ent1"]
    assert type(ext_ent) is CrossRef
    assert type(ent1) is Entity
    print("dep_bound ", ext_ent._bound)
    print("ent1 ", ent1)
    assert ext_ent._bound == ent1
