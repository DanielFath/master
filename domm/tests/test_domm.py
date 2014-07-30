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


def test_dataType():
    parsed1 = DommParser().string_into_ast("""model simple
        dataType Name""")["simple"]

    expected1 = Model(name = "simple").add_type(DataType(name = "Name"))
    assert parsed1 == expected1

    parsed2 = DommParser().string_into_ast("""model simple
        buildinDataType Name "Name of person" """)["simple"]

    expected2 = Model(name = "simple").add_type(DataType(name = "Name", short_desc = "Name of person", built_in = True))
    assert parsed2 ==  expected2

    parsed3 = DommParser().string_into_ast("""model simple
        dataType Name "Name of person" "Detailed description of field" """)["simple"]

    expected3 = Model(name = "simple").add_type(
        DataType(name = "Name", short_desc = "Name of person", long_desc="Detailed description of field"))
    assert parsed3 ==  expected3

def test_enum():
    parsed1 = DommParser().string_into_ast(""" model enum
    enum Color "Color desc." {
        R "Red"
        G "Green"
        B "Blue"
    }""")["enum"]

    expected1 = Model(name = "enum").add_type(
        Enumeration(name = "Color", short_desc = "Color desc." ).add_all_literals([
            EnumLiteral(value = "R", name = "Red"),
            EnumLiteral(value = "G", name = "Green"),
            EnumLiteral(value = "B", name = "Blue")
            ])
        )
    assert parsed1 == expected1

def test_tagType():
    parsed1 = DommParser().string_into_ast("""model test
        tagType orderBy (_ref, ...) appliesTo _entity
        buildinTagType plural (_string) appliesTo _entity _valueObject
        validatorType example
        buildInValidatorType text_example "short desc" "long description"
    """)["test"]



def test_package():
    parser = DommParser()
    parser.parse(""" model test
        package test {
            dataType test

            package inner {

            }
        }
        """)

def test_exception():
    parser = DommParser()
    parser.parse(""" model test
        package test {
            exception ResultNotFound "Rezultat nije nadjen." {
                prop int errorCode
            }
        }
    """)
