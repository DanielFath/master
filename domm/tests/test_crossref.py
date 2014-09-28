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

def test_depends():
    dep_test = """model x
    package test {
        dataType int
        service serv1 {
            op int getCode()
        }

        service serv2 depends serv1 {
            op int getStuff()
        }

        valueObject vo1 depends ent1 {
            prop int vo_id
        }

        entity ent1 depends serv1 {
            key { prop int id}
        }
    }"""
    parsed1 = DommParser()._test_crossref(dep_test)
    serv1 = parsed1["test"]["serv1"]
    dep_serv = parsed1["test"]["serv2"].dependencies[0]
    assert type(dep_serv) is CrossRef
    assert type(serv1) is Service
    assert dep_serv._bound == serv1

    ent1 = parsed1["test"]["ent1"]
    dep_ent = parsed1["test"]["ent1"].dependencies[0]
    assert type(ent1) is Entity
    assert type(dep_ent) is CrossRef
    assert dep_ent._bound == serv1

    dep_vo = parsed1["test"]["vo1"].dependencies[0]
    assert type(dep_vo) is CrossRef
    assert dep_vo._bound == ent1

def test_constraint():
    cosntr_test = """model x
    dataType int
    buildinTagType plural (_string) appliesTo _entity _valueObject
    buildinTagType all_tag appliesTo _entity _valueObject _service _prop _op _param
    package test {
        valueObject Vo1 {
            [all_tag]
            prop int vos
        }

        service serv1 {
            [all_tag]
            op int getStuff()
        }

        entity ent {
            key {
                prop int key
            }
            [plural("2")]
        }
    }
    """
    parsed1 = DommParser()._test_crossref(cosntr_test)
    vo1_constr = parsed1["test"]["Vo1"].constraints
    all_tag = parsed1["all_tag"]
    assert type(vo1_constr) is set
    assert len(vo1_constr) == 1
    assert list(vo1_constr)[0]._bound == all_tag

    serv1_constr = parsed1["test"]["serv1"].constraints
    assert type(serv1_constr) is set
    assert len(serv1_constr) == 1
    assert list(serv1_constr)[0]._bound == all_tag

    plural = parsed1["plural"]
    entity = parsed1["test"]["ent"].constraints
    assert type(entity) is set
    assert len(entity) == 1
    assert list(entity)[0]._bound == plural

    with pytest.raises(ConstraintDoesntApplyError):
        DommParser()._test_crossref("""model x
        dataType int
        buildinTagType ent_only appliesTo _entity
        package test {
            valueObject Vo1 {
                [ent_only]
                prop int vos
            }
        }
            """)

    with pytest.raises(NoParameterError):
        DommParser()._test_crossref("""model x
        dataType int
        buildinTagType wrong_param  appliesTo _valueObject
        package test {
            valueObject Vo1 {
                [wrong_param(2)]
                prop int vos
            }
        }
            """)

    # Test pure elipsis
    DommParser()._test_crossref("""model x
    dataType int
    buildinTagType wrong_param (...) appliesTo _valueObject
    package test {
        valueObject Vo1 {
            [wrong_param (2,3,"string",int)]
            prop int vos
        }
    }
        """)

    # Test partial elipsis
    DommParser()._test_crossref("""model x
    dataType int
    buildinTagType wrong_param (...) appliesTo _valueObject
    package test {
        valueObject Vo1 {
            [wrong_param (2,3,"string",int)]
            prop int vos
        }
    }
        """)

    # Test partial elipsis
    DommParser()._test_crossref("""model x
    dataType int
    buildinTagType wrong_param (_int,...) appliesTo _valueObject
    package test {
        valueObject Vo1 {
            [wrong_param (2,3,44)]
            prop int vos
        }
    }
        """)
    # Test wrong elipsis
    with pytest.raises(WrongConstraintError):
        DommParser()._test_crossref("""model x
        dataType int
        buildinTagType wrong_param (_string, ...) appliesTo _valueObject
        package test {
            valueObject Vo1 {
                [wrong_param (2)]
                prop int vos
            }
        }
            """)

    with pytest.raises(WrongNumberOfParameterError):
        DommParser()._test_crossref("""model x
        dataType int
        buildinTagType wrong_param (_int,_int) appliesTo _valueObject
        package test {
            valueObject Vo1 {
                [wrong_param(2,3,2,4,535)]
                prop int vos
            }
        }""")

    with pytest.raises(WrongConstraintAtPosError):
        DommParser()._test_crossref("""model x
        dataType int
        buildinTagType wrong_param (_string, _int) appliesTo _valueObject
        package test {
            valueObject Vo1 {
                [wrong_param ("s", "meh")]
                prop int vos
            }
        }
            """)

