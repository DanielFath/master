import pytest
from  arpeggio import NoMatch
from  domm.parser import DommParser
from  domm.metamodel import Model, Id

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

def test_entity():
    parser = DommParser()
    parser.parse("""model simple
        dataType Name
        """)

    parser.parse("""model simple
        buildinDataType Name
        """)

    parser.parse("""model simple
        dataType Name "Ime osobe"
        """)

    parser.parse("""model simple
        dataType Name "Ime osobe" "Detaljno objasnjenje imena osobe"
        """)

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
        tagType type1
        buildinTagType type2
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
