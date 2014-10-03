##############################################################################
# Name: test_ast.py
# Purpose: Test for verifying output AST of DOMM parser
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
from  domm.parser import DommParser
from  domm.metamodel import *

def test_model():
    assert DommParser()._test_parse("model simple") == Model(name="simple")

    simple2 = Model(name="simple", short_desc="short_desc")
    assert DommParser()._test_parse('model simple "short_desc" ') == simple2


    simple3 = Model(name="simple", short_desc="short_desc",\
        long_desc="long_desc")
    assert DommParser()._test_parse('model simple "short_desc" "long_desc" ')\
                == simple3
    assert DommParser()._test_parse('model simple1 "short_desc"  "long_desc"' )\
                != simple3
    assert DommParser()._test_parse('model simple  "short_desc1" "long_desc"' )\
                != simple3
    assert DommParser()._test_parse('model simple  "short_desc"  "long_desc1"')\
                != simple3

def test_dataType():
    parsed1 = DommParser()._test_parse("""model simple
        dataType Name""")["Name"]

    expected1 = DataType(name = "Name")
    assert parsed1 == expected1
    assert hash(parsed1) == hash(expected1)

    parsed2 = DommParser()._test_parse("""model simple
        dataType Name "Name of person" "Detailed description of field" """)["Name"]

    expected2 = DataType(name = "Name", short_desc = "Name of person",\
                long_desc="Detailed description of field")
    assert parsed2 ==  expected2
    assert hash(parsed2) == hash(expected2)

def test_validator():
    parsed1 = DommParser()._test_parse("""model std
        package std {
            buildinValidator matchesRegularExpression (_string) appliesTo _prop
        }""")

def test_enum():
    parsed1 = DommParser()._test_parse(""" model x package test {
    enum Color "Color desc." {
        R "Red"
        G "Green"
        B "Blue"
    }}""")["test"]["Color"]

    expected1 = Enumeration(name = "Color", short_desc = "Color desc."
        ).add_all_literals([
            EnumLiteral(value = "R", name = "Red"),
            EnumLiteral(value = "G", name = "Green"),
            EnumLiteral(value = "B", name = "Blue")
            ])

    unexpected1 = Enumeration(name = "Color", short_desc = "Color desc."
        ).add_all_literals([
            EnumLiteral(value = "R", name = "Red"),
            EnumLiteral(value = "G", name = "Green"),
            EnumLiteral(value = "B", name = "Blues")
            ])

    assert parsed1 == expected1
    assert parsed1 != unexpected1
    assert hash(parsed1) == hash(expected1)
    assert hash(parsed1) != hash(unexpected1)

def test_tagType():
    parsed1 = DommParser()._test_parse("""model test
        tagType orderBy (_ref, ...) appliesTo _entity
        buildinTagType plural (_string) appliesTo _entity _valueObject
        validatorType example
        buildinValidator text_example "short desc" "long description"
    """)

    tag1 = CommonTag(name = "orderBy", constr_def = ConstrDef(["_ref", "..."]),\
                applies = ApplyDef(to_entity = True))
    tag2 = CommonTag(name = "plural", constr_def = ConstrDef(["_string"]),\
                applies = ApplyDef(to_entity = True, to_value_object = True))
    tag3 = CommonTag(name = "example")
    tag4 = CommonTag(name = "text_example", short_desc = "short desc",\
                long_desc = "long description")

    expected1 = Model(name = "test"
        ).add_constraint(Constraint(built_in = False, constr_type = ConstraintType.Tag, tag = tag1)
        ).add_constraint(Constraint(built_in = True, constr_type = ConstraintType.Tag, tag = tag2)
        ).add_constraint(Constraint(built_in = False, constr_type = ConstraintType.Validator, tag = tag3)
        ).add_constraint(Constraint(built_in = True, constr_type = ConstraintType.Validator, tag = tag4))

    unexpected1 = Model(name = "test"
        ).add_constraint(Constraint(built_in = False, constr_type = ConstraintType.Tag, tag = tag1)
        ).add_constraint(Constraint(built_in = True, constr_type = ConstraintType.Tag, tag = tag3)
        ).add_constraint(Constraint(built_in = False, constr_type = ConstraintType.Validator, tag = tag2)
        ).add_constraint(Constraint(built_in = True, constr_type = ConstraintType.Validator, tag = tag4))

    assert parsed1 == expected1
    assert parsed1 != unexpected1
    assert hash(parsed1) == hash(expected1)
    assert hash(parsed1) != hash(unexpected1)

def test_package():
    parsed1 = DommParser()._test_parse(""" model test
        package example {
        }
        """)

    pack1 = Package(name = "example"
        )

    pack1alt = Package(name = "test"
        ).add_elem(DataType(name = "test")
        ).add_elem(Package(name="inner2"))


    expected1 = Model(name = "test").add_package(pack1)
    unexpected1 = Model(name = "test").add_package(pack1alt)

    print("parsed1 ", parsed1)
    print("parsed.model ", parsed1["example"]._parent_model)
    print("expected1 ", expected1)

    assert parsed1["example"]._parent_model == expected1
    assert parsed1 == expected1
    assert parsed1 != unexpected1
    assert hash(parsed1) == hash(expected1)
    assert hash(parsed1) != hash(unexpected1)

def test_exception():
    parsed1 = DommParser()._test_parse(""" model test
        package exception_example {
            exception ResultNotFound "Result has not been found" {
                prop int errCode
                prop +string[2] message <> testing [isValidErrCode(2, "string", X), finder]  "error message" "message"
            }
        }
    """)

    type_def1 = TypeDef(name = "message", type_of = "string", short_desc = "error message" , long_desc = "message")
    type_def1.set_multi(2)

    rel1 = Relationship(containment = True, opposite_end = Qid("testing"))

    prop2 = Property(type_def = type_def1, relation = rel1
        ).add_constraint_spec(ConstraintSpec(ident = Qid("isValidErrCode"), parameters = [2, "string", Id("X")])
        ).add_constraint_spec(ConstraintSpec(ident = Qid("finder")))

    prop1 = Property(type_def = TypeDef(name = "errCode", type_of = "int"))

    exec1 = ExceptionType(name = "ResultNotFound", short_desc = "Result has not been found"
       ).add_prop(prop1
       ).add_prop(prop2)

    expected1 = Model(name = "test").add_package(Package(name = "exception_example"
            ).add_elem(exec1))

    unexec1 = ExceptionType(name = "GlDos", short_desc = "Result has been modified")

    unexpected1 = Model(name = "test").add_package(Package(name = "exception_example").add_elem(unexec1))

    print("parsed1 ", parsed1)
    print("expected1 ", expected1)
    print("parsed1   hash", hash(parsed1))
    print("expected1 hash", hash(expected1))

    assert parsed1["exception_example"]["ResultNotFound"]["errCode"] == prop1
    assert parsed1["exception_example"]["ResultNotFound"]["message"] == prop2

    print("parsed1._parent_model ", parsed1["exception_example"]["ResultNotFound"]._parent_model )
    assert parsed1["exception_example"]["ResultNotFound"]._parent_model == expected1

    assert parsed1 == expected1
    assert parsed1 != unexpected1
    assert hash(parsed1) == hash(expected1)
    assert hash(parsed1) != hash(unexpected1)

def test_service():
    parsed1 = DommParser(debugDomm = True)._test_parse(""" model test
        package exception_example {
            service StudentService extends Ext depends Dep1 "Student service" "Gives services to students" {
                [finder]
                op string getName(datetime from)
                compartment test {
                    op char testing()
                }
            }
        }
    """)

    ext = CrossRef(ref = Qid("Ext"), ref_type = Ref.Service)
    dep = CrossRef(ref = Qid("Dep1"), ref_type = Ref.Service)
    op1 = Operation(type_def = TypeDef(name = "getName", type_of = "string")
        ).add_param(OpParam(type_def = TypeDef(name = "from", \
            type_of = "datetime")))
    op2 = Operation(type_def = TypeDef(name = "testing", type_of = "char"))
    comp = Compartment(name = "test").add_elem(op2)

    service1 = Service(name = "StudentService", \
        short_desc = "Student service", \
        long_desc = "Gives services to students", \
        extends = ext, depends = [dep]
        ).add_constraint_spec(ConstraintSpec(ident = Qid("finder"))
        ).add_operation(op1).add_op_compartment(comp)

    expected1 = Model(name = "test").add_package(Package(name = "exception_example"
        ).add_elem(service1))

    print("parsed1   ", parsed1)
    print("expected1 ", expected1)
    print("parsed1   hash", hash(parsed1))
    print("expected1 hash", hash(expected1))

    assert parsed1 == expected1
    assert hash(parsed1) == hash(expected1)

def test_value_object():
    parsed1 = DommParser(debugDomm = True)._test_parse(""" model test
        package vo_example {
            valueObject example {
                prop string X
            }
        }""")

    vo1 = ValueObject(name = "example").add_prop(Property(type_def = TypeDef(
        name = "X", type_of = "string")))
    pack1 = Package(name = "vo_example")
    pack1.add_elem(vo1)
    expected1 = Model(name = "test").add_package(pack1)

    print("vo1", vo1)
    print("parsed1   ", parsed1)
    print("expected1 ", expected1)
    print("parsed1   hash", hash(parsed1))
    print("expected1 hash", hash(expected1))

    assert parsed1 == expected1
    assert hash(parsed1) == hash(expected1)

def test_containter():
    parsed1 = DommParser()._test_parse("""model test
        package example {
            valueObject vo {
                prop int id
                prop string[] x
                prop string[2] n2
            }
        }""")
    i = parsed1["example"]["vo"]["id"]
    x = parsed1["example"]["vo"]["x"]
    n2 = parsed1["example"]["vo"]["n2"]
    assert i.type_def.container == False
    assert x.type_def.container == True
    assert n2.type_def.container == True
    assert i.type_def.multi == None
    assert x.type_def.multi == None
    assert n2.type_def.multi == 2

def test_entity():
    parsed1 = DommParser(debugDomm = True)._test_parse("""
        model test

        package ent_example {
            entity example extends std.Ex depends D1{
                key {
                    prop int id
                }
            }
        }
        """)

    key1 = Key().add_prop(Property(type_def = TypeDef(name = "id", type_of = "int")))
    ext1 = CrossRef(ref = Qid(["std","Ex"]), ref_type = Ref.Entity)
    dep1 = CrossRef(ref = Qid("D1"), ref_type = Ref.Service)


    ent1 = Entity(name = "example"
        ).set_key(key1
        ).set_extends(ext1
        ).set_dependencies([dep1])
    pack1 = Package(name = "ent_example").add_elem(ent1)
    expected1 = Model(name = "test").add_package(pack1)

    parsed1 == expected1

    print("ent1 ", ent1)
    print("parsed1 ", parsed1)
    print("expected1 ", expected1)
    print("parsed1   hash", hash(parsed1))
    print("expected1 hash", hash(expected1))

    assert parsed1 == expected1
    assert hash(parsed1) == hash(expected1)
