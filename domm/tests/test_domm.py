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
        dataType Name "Ime osobe" """)["simple"]

    expected2 = Model(name = "simple").add_type(DataType(name = "Name", short_desc = "Ime osobe"))
    assert parsed2 ==  expected2

    parsed3 = DommParser().string_into_ast("""model simple
        dataType Name "Ime osobe" "Detaljno objasnjenje imena osobe" """)["simple"]

    expected3 = Model(name = "simple").add_type(
        DataType(name = "Name", short_desc = "Ime osobe", long_desc="Detaljno objasnjenje imena osobe"))
    assert parsed3 ==  expected3

def test_enum():
    parser = DommParser()
    parser.parse(""" model enum
    enum Boje "boje" {
        R "Red"
        G "Green"
        B "Blue"
    }""")

    parser.parse(""" model enum
    enum Boje "boje" {
        R "Red" "Crvena" "Boja Crvena"
        G "Green" "Zelena" "Boja Zelena"
        B "Blue" "Plava" "Boja Plava"
    }""")

def test_tagType():
    parser = DommParser()
    parser.parse("""model test
        tagType orderBy (_ref, ...) appliesTo _entity
        buildinTagType plural (_string) appliesTo _entity _valueObject
        validatorType type3
        buildInValidatorType type4
    """)

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
