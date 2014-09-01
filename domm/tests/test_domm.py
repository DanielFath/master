import pytest
from  arpeggio import NoMatch
from  domm.error import DuplicateTypeError, DuplicateFeatureError
from  domm.parser import DommParser
from  domm.metamodel import *

def test_qid():
    qid_from_str = Qid("test.x.a")
    qid = Qid(["test", "x", "a"])
    assert qid_from_str == qid
    assert qid_from_str.depth() == 3

    qid_outer = Qid(qid.path).add_outer_level("out")
    assert qid_outer == Qid(["out", "test", "x", "a"])
    assert qid_outer.depth() == 4

def test_package_id():
    pack1 = Package(name = "test")
    prop1 = Property(type_def = TypeDef(name = "X", type_of = "string"))
    vobj1 = ValueObject(name = "vo").add_prop(prop1)
    pack1.add_elem(vobj1)

    expected1elems = {Qid("test.vo"): vobj1}
    expected1imprt = {Qid("test.vo.X") : prop1}
    assert expected1elems == pack1.elems
    assert expected1imprt == pack1._imported


    pack2 = Package(name = "test")
    prop2 = Property(type_def = TypeDef(name = "X", type_of = "string"))
    excp2 = ExceptionType(name = "except").add_prop(prop2)
    pack2.add_elem(excp2)

    expected2elems = {Qid("test.except") : excp2}
    expected2imprt = {Qid("test.except.X") : prop2}
    assert expected2elems == pack2.elems
    assert expected2imprt == pack2._imported

    pack3 = Package(name = "test")
    oper3 = Operation(type_def = TypeDef(name = "X", type_of = "int"))
    serv3 = Service(name = "service").add_operation(oper3)
    pack3.add_elem(serv3)

    expected3elems = {Qid("test.service"): serv3}
    expected3imprt = {Qid("test.service.X") : oper3}
    assert expected3elems == pack3.elems
    assert expected3imprt == pack3._imported

    pack4 = Package(name = "test")
    prop4 = Property(type_def = TypeDef(name = "id", type_of = "int"))
    key4  = Key().add_prop(prop4)
    enti4 = Entity(name = "ent").set_key(key4)
    pack4.add_elem(enti4)

    expected4elems = {Qid("test.ent"): enti4}
    expected4imprt = {Qid("test.ent.id") : prop4}
    assert expected4elems == pack4.elems
    assert expected4imprt == pack4._imported

    pack5 = Package(name = "ex")
    pack5.add_elem(pack4)

    expected5elems = {Qid("ex.test"): pack4}
    expected5imprt = {Qid("ex.test.ent") : enti4, Qid("ex.test.ent.id"): prop4}
    print("pack5._imported ", pack5._imported)
    print("pack5.elems ", pack5.elems)
    assert expected5elems == pack5.elems
    assert expected5imprt == pack5._imported


def test_empty():
    with pytest.raises(NoMatch):
        DommParser().parse("")

def test_duplicate_datatype():
    with pytest.raises(DuplicateTypeError):
        DommParser()._test_parse("model simple dataType a dataType a")


def test_duplicate_prop_name():
    with pytest.raises(DuplicateFeatureError):
        DommParser()._test_parse("""model simple package test {
                entity test {
                    key { prop int id}
                    prop string X
                    prop int X
                }
            }""")

def test_model():
    assert DommParser()._test_parse("model simple") == Model(name="simple")

    simple2 = Model(name="simple", short_desc="short_desc")
    assert DommParser()._test_parse('model simple "short_desc" ') == simple2


    simple3 = Model(name="simple", short_desc="short_desc", long_desc="long_desc")
    assert DommParser()._test_parse('model simple "short_desc" "long_desc" ') == simple3

    assert DommParser()._test_parse('model simple1 "short_desc"  "long_desc"' ) != simple3
    assert DommParser()._test_parse('model simple  "short_desc1" "long_desc"' ) != simple3
    assert DommParser()._test_parse('model simple  "short_desc"  "long_desc1"') != simple3

def test_dataType():
    parsed1 = DommParser()._test_parse("""model simple
        dataType Name""")["Name"]

    expected1 = DataType(name = "Name")
    assert parsed1 == expected1
    assert hash(parsed1) == hash(expected1)

    parsed2 = DommParser()._test_parse("""model simple
        dataType Name "Name of person" "Detailed description of field" """)["Name"]

    expected2 = DataType(name = "Name", short_desc = "Name of person", long_desc="Detailed description of field")
    assert parsed2 ==  expected2
    assert hash(parsed2) == hash(expected2)

def test_enum():
    parsed1 = DommParser()._test_parse(""" model enum package test {
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

    tag1 = CommonTag(name = "orderBy", constr_def = ConstrDef(["_ref", "..."]), applies = ApplyDef(to_entity = True))
    tag2 = CommonTag(name = "plural", constr_def = ConstrDef(["_string"]), applies = ApplyDef(to_entity = True, to_value_object = True))
    tag3 = CommonTag(name = "example")
    tag4 = CommonTag(name = "text_example", short_desc = "short desc", long_desc = "long description")

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
    print("expected1 ", expected1)

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
