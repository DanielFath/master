import pytest
from  arpeggio import NoMatch
from  domm.parser import DommParser

with pytest.raises(NoMatch):
    DommParser().parse("")

def test_model():
    parser = DommParser()
    parser.parse("model simple")
    parser.parse('model simple "short_desc"')
    parser.parse('model simple "short_desc" "long_desc"')

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