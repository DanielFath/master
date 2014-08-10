import pytest
from  arpeggio import NoMatch
from  domm.error import TypeExistsError
from  domm.parser import DommParser
from  domm.metamodel import *

with pytest.raises(NoMatch):
    DommParser().parse("")

with pytest.raises(TypeExistsError):
    DommParser().string_into_ast("model simple dataType a dataType a")

with pytest.raises(TypeExistsError):
    DommParser().string_into_ast("model simple dataType a dataType a")

def test_model():
    assert DommParser().string_into_ast("model simple")["simple"] == Model(name="simple")

    simple2 = Model(name="simple", short_desc="short_desc")
    assert DommParser().string_into_ast('model simple "short_desc" ')["simple"] == simple2


    simple3 = Model(name="simple", short_desc="short_desc", long_desc="long_desc")
    assert DommParser().string_into_ast('model simple "short_desc" "long_desc" ')["simple"] == simple3

    assert DommParser().string_into_ast('model simple1 "short_desc"  "long_desc"' )["simple1"] != simple3
    assert DommParser().string_into_ast('model simple  "short_desc1" "long_desc"' )["simple"]  != simple3
    assert DommParser().string_into_ast('model simple  "short_desc"  "long_desc1"')["simple"]  != simple3

def test_dataType():
    parsed1 = DommParser().string_into_ast("""model simple
        dataType Name""")["simple"]["Name"]

    expected1 = DataType(name = "Name")
    assert parsed1 == expected1

    parsed3 = DommParser().string_into_ast("""model simple
        dataType Name "Name of person" "Detailed description of field" """)["simple"]["Name"]

    expected3 = DataType(name = "Name", short_desc = "Name of person", long_desc="Detailed description of field")
    assert parsed3 ==  expected3

def test_enum():
    parsed1 = DommParser().string_into_ast(""" model enum package test {
    enum Color "Color desc." {
        R "Red"
        G "Green"
        B "Blue"
    }}""")["enum"]["test"]["Color"]

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

def test_tagType():
    parsed1 = DommParser().string_into_ast("""model test
        tagType orderBy (_ref, ...) appliesTo _entity
        buildinTagType plural (_string) appliesTo _entity _valueObject
        validatorType example
        buildinValidator text_example "short desc" "long description"
    """)["test"]

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
    assert not parsed1 == unexpected1


def test_package():
    parsed1 = DommParser().string_into_ast(""" model test
        package example {
        }
        """)["test"]

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

def test_exception():
    parsed1 = DommParser().string_into_ast(""" model test
        package exception_example {
            exception ResultNotFound "Result has not been found" {
                prop int errCode
                prop +string[2] message <> testing [isValidErrCode(2, "string", X), finder]  "error message" "message"
            }
        }
    """)["test"]

    type_def1 = TypeDef(name = "message", type_of = "string", short_desc = "error message" , long_desc = "message")
    type_def1.set_multi(2)

    rel1 = Relationship(containment = True, opposite_end = Id("testing"))

    prop2 = Property(type_def = type_def1, relation = rel1
        ).add_constraint_spec(ConstraintSpec(ident = Id("isValidErrCode"), parameters = [2, "string", Id("X")])
        ).add_constraint_spec(ConstraintSpec(ident = Id("finder")))

    prop1 = Property(type_def = TypeDef(name = "errCode", type_of = "int"))

    exec1 = ExceptionType(name = "ResultNotFound", short_desc = "Result has not been found"
       ).add_prop(prop1
       ).add_prop(prop2)

    expected1 = Model(name = "test").add_package(Package(name = "exception_example"
            ).add_elem(exec1))

    print("parsed1 ", parsed1)
    print("expected1 ", expected1)
    print("parsed1   hash", hash(parsed1))
    print("expected1 hash", hash(expected1))

    assert parsed1 == expected1
    assert parsed1["exception_example"]["ResultNotFound"]["errCode"] == prop1

def test_service():
    parsed1 = DommParser(debugDomm = True).string_into_ast(""" model test
        package exception_example {
            service StudentService {

            }
        }
    """)["test"]

    ext = ClassifierBound(ref = Id("Ext"), type_of = ClassType.Service)
    dep = ClassifierBound(ref = Id("Dep1"), type_of = ClassType.Service)
    service1 = Service(name = "StudentService"#, \
        #short_desc = "Student service", \
        #long_desc = "Gives services to students", \
        #extends = ext, depends = [dep]
        )
    expected1 = Model(name = "test").add_package(Package(name = "exception_example"
        ).add_elem(service1))

    #print("parsed1 ", parsed1)
    #print("expected1 ", expected1)

    expected1 == parsed1

    print("expected1 == parserd", expected1.all["exception_example"] == parsed1.all["exception_example"])
    print("expected1.all", parsed1.all["exception_example"]["StudentService"])
    print("parsed1.all", expected1.all["exception_example"]["StudentService"])
    print("parsed1   hash", hash(parsed1))
    print("expected1 hash", hash(expected1))



    assert parsed1 == expected1
