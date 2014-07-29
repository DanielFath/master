import pytest
from  arpeggio import NoMatch
from  domm.parser import DommParser
from  domm.metamodel import *

with pytest.raises(NoMatch):
    DommParser().parse("")


def test_model():
    assert DommParser().string_into_ast("model simple")["simple"] == Model(name="simple")
    DommParser.reset_namespace()

    simple2 = Model(name="simple", short_desc="short_desc")
    assert DommParser().string_into_ast('model simple "short_desc" ')["simple"] == simple2
    DommParser.reset_namespace()

    simple3 = Model(name="simple", short_desc="short_desc", long_desc="long_desc")
    assert DommParser().string_into_ast('model simple "short_desc" "long_desc" ')["simple"] == simple3
    DommParser.reset_namespace()

def test_dataType():
    parsed1 = DommParser().string_into_ast("""model simple
        dataType Name""")["simple"]
    DommParser.reset_namespace()

    expected1 = Model(name = "simple").add_type(DataType(name = "Name"))
    assert parsed1 == expected1
    DommParser.reset_namespace()

    parsed2 = DommParser().string_into_ast("""model simple
        dataType Name "Ime osobe" """)["simple"]
    DommParser.reset_namespace()

    expected2 = Model(name = "simple").add_type(DataType(name = "Name", short_desc = "Ime osobe"))
    assert parsed2 ==  expected2
    DommParser.reset_namespace()

    parsed3 = DommParser().string_into_ast("""model simple
        dataType Name "Ime osobe" "Detaljno objasnjenje imena osobe" """)["simple"]
    DommParser.reset_namespace()

    expected3 = Model(name = "simple").add_type(
        DataType(name = "Name", short_desc = "Ime osobe", long_desc="Detaljno objasnjenje imena osobe"))
    assert parsed3 ==  expected3
    DommParser.reset_namespace()

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
