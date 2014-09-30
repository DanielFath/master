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

def test_operation_type():
    op_test = """
    model x
    dataType int
    package test {
        service serv1 {
            op int getCode(int name, int stuff)
        }
    }
    """
    parsed1 = DommParser()._test_crossref(op_test)
    op = parsed1["test"]["serv1"]["getCode"]
    int_type = parsed1["int"]
    assert op.type_def._bound == int_type
    for param in op.params:
        assert param.type_def._bound == int_type

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
    vo2 = parsed1["test"]["Vo2"]
    extVo21 = RelObj(rel_type = RelType.Extends, elem_a = vo2, elem_b = vo1)
    assert type(ext_vo) is CrossRef
    assert type(vo1) is ValueObject
    assert ext_vo._bound == vo1
    assert len(parsed1._rels) == 3
    assert extVo21 in parsed1._rels

    ext_serv = parsed1["test"]["serv2"].extends
    serv1 = parsed1["test"]["serv1"]
    en1 = parsed1["test"]["ent1"]
    en2 = parsed1["test"]["ent2"]
    extEnt21 = RelObj(rel_type = RelType.Extends, elem_a = en2, elem_b = en1)
    assert type(ext_serv) is CrossRef
    assert type(serv1) is Service
    assert ext_serv._bound == serv1
    assert extEnt21 in parsed1._rels

    ext_ent = parsed1["test"]["ent2"].extends
    ent1 = parsed1["test"]["ent1"]
    s1 = parsed1["test"]["serv1"]
    s2 = parsed1["test"]["serv2"]
    extServ21 = RelObj(rel_type = RelType.Extends, elem_a = s2, elem_b = s1)
    assert type(ext_ent) is CrossRef
    assert type(ent1) is Entity
    assert ext_ent._bound == ent1
    assert extServ21 in parsed1._rels

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
    serv2 = parsed1["test"]["serv2"]
    dep_s2_s1 = RelObj(RelType.Depends, serv2, serv1)
    assert type(dep_serv) is CrossRef
    assert type(serv1) is Service
    assert dep_serv._bound == serv1
    assert dep_s2_s1 in parsed1._rels
    assert len(parsed1._rels) == 3

    ent1 = parsed1["test"]["ent1"]
    dep_ent = parsed1["test"]["ent1"].dependencies[0]
    dep_ent1_serv1 = RelObj(RelType.Depends, ent1, serv1)
    assert type(ent1) is Entity
    assert type(dep_ent) is CrossRef
    assert dep_ent._bound == serv1
    assert dep_ent1_serv1 in parsed1._rels


    dep_vo = parsed1["test"]["vo1"].dependencies[0]
    v1 = parsed1["test"]["vo1"]
    dep_v1_ent1 = RelObj(RelType.Depends, v1, ent1)
    assert type(dep_vo) is CrossRef
    assert dep_vo._bound == ent1
    assert dep_v1_ent1 in parsed1._rels

def test_constraint():
    cosntr_test = """model x
    dataType int
    buildinTagType plural (_string) appliesTo _entity _valueObject
    buildinTagType all_tag appliesTo _entity _valueObject _service _prop _op _param
    package test {
        valueObject Vo1 {
            [all_tag]
            prop int vos [all_tag]
        }

        service serv1 {
            [all_tag]
            op int getStuff(int val [all_tag]) [all_tag]
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

    prop_constr = parsed1["test"]["Vo1"]["vos"].constraints
    assert type(prop_constr) is set
    assert len(prop_constr) == 1
    assert list(prop_constr)[0]._bound == all_tag

    op_constr = parsed1["test"]["serv1"]["getStuff"].constraints
    assert type(op_constr) is set
    assert len(op_constr) == 1
    assert list(op_constr)[0]._bound == all_tag

    param = parsed1["test"]["serv1"]["getStuff"].params[0]
    assert type(param) is OpParam
    assert type(param.constraints) is set
    assert len(param.constraints) == 1
    assert list(param.constraints)[0]._bound == all_tag

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

