##############################################################################
# Name: parser.py
# Purpose: PEG parser for DOMMLite domain language
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
#
# PEG used to describe a DOMMLite DSL
# For more information about DOMMLite DSL please consult the guide
#    Metamodel, model editor and business  applications generator
# By Igor Dejanović. The work can be found at:
#   Library of Faculty of Engineering,
#   Trg Dositeja Obradovića 6, Novi Sad
##############################################################################
import sys

from arpeggio import *
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _

from actions import *

# Defines a meta type named element and its sub rules
def named_elem():       return [(string, string), string]

# Defines basic literalls
def string():           return '"', _('[^"]*'),'"'
def ident():               return _(r'[a-zA-Z_]([a-zA-Z_]|[0-9])*')
def integer():               return _(r'([1-9][0-9]*)|[0-9]')

# Defines the starting rules for all types
# defines categorization of said types into data_types and constraints
def types():            return [data_types, constraint_type]
# Defines data_types as either user made types, built-in types (e.g. integer, string)
# and enumerations of elements
def data_types():       return [user_type, built_type, enum]
def user_type():        return Kwd("dataType"), ident, Optional(named_elem)
def built_type():       return Kwd("buildinDataType"), ident, Optional(named_elem)

# Defines the rules for enumeration literals
def enum():             return Kwd("enum"), ident, Optional(named_elem), "{", OneOrMore(enum_literals), "}"
def enum_literals():    return ident, string, Optional(named_elem)

# Defines rules for constraint types
# Constraint types are defined as either a tagType (which may be built-in)
# or a validator type (which can also be built-in)
def constraint_type():  return [tag_type, validator_type]

# Tag types are helper values that annotate fields allowing them for instance
# to be unique, searchable, displayed in list, etc.
# An application could connect to DOMMLite and based on the attributes,
# generate bindings for various options
def tag_type():         return [user_tag, builtin_tag]
def user_tag():         return Kwd("tagType"), common_tag
def builtin_tag():      return Kwd("buildinTagType"), common_tag

# Validator types on the other hand take various values
# and return a binary yes/no values. They are often prefix with is,
# like for example isValidImage, isValidUrl.
# They determine if a given value is essentially correct.
def validator_type():   return [user_validator, builtin_valid]
def user_validator():   return Kwd("validatorType"), common_tag
def builtin_valid():    return Kwd("buildInValidatorType"), common_tag
def common_tag():       return ident, Optional(constr_def), Optional(apply_def), Optional(named_elem)
def constr_def():       return "(", constr_type, ZeroOrMore(",", constr_type) , ")"
def apply_def():        return Kwd("appliesTo"), ZeroOrMore([Kwd("_entity"), Kwd("_prop"),
                            Kwd("_param"), Kwd("_op"), Kwd("_service"), Kwd("_valueObject")])
def constr_type():      return [Kwd("_string"), Kwd("_int"), Kwd("_ref"), Kwd("...")]

# Defines package which is a unit of code organization, which may contain other nested packages
def package():          return Kwd("package"), ident, Optional(named_elem), "{", ZeroOrMore(pack_elem), "}"
def pack_elem():        return [package,classifier]

# Defines rules for various structure classifications (i.e. package elements)
def classifier():       return [entity, service, value_object, exception, data_types,constraint_type]

# Defines an entity in DOMMLite model that often represents actors in the business model
def entity():           return Kwd("entity"), ident, Optional(Kwd("extends"), ident), Optional(Kwd("depends"), ident,
                             ZeroOrMore(",", ident)), Optional(named_elem), "{", key, repr, Optional(constr_specs
                             ), ZeroOrMore(feature), ZeroOrMore(feature_compart), "}"
# Defines service in DOMMLite model that provides one or more operations.
def service():          return Kwd("service"), ident, Optional(Kwd("extends"), ident), Optional(Kwd("depends"), ident,
                             ZeroOrMore(",", ident)), Optional(named_elem), "{", Optional(constr_specs), ZeroOrMore(oper
                             ), ZeroOrMore(oper_compart), "}"

# An entity contains a key through which it is referenced.
# This models something analogous to a complex database key.
def key():              return Kwd("key"), "{", OneOrMore(prop), "}"

# Representation of given entity in the system. For example
# a Person can be presented using their name and last name, despite having
# age, ID number, place of residence, etc.
def repr():             return Kwd("repr"), repr_param, ZeroOrMore("+", repr_param)
def repr_param():       return [string, prop]

# Constraint definition defines a set of limitations to a type
# for instance we can define that some elements are between certain values.
# For examples grades of a student are between 1 and 5 (or A and F)
def constr_specs():     return "[", constr_spec, ZeroOrMore(",", constr_spec), "]"
def constr_spec():      return constraint_type, Optional("(", constr_param, ZeroOrMore(",", constr_param), ")"),
def constr_param():     return [string, ident, integer]

# Feature represents a combinationf of properties and operation which
# are features of other classifiers
def feature():          return [prop, oper]

# Defines property of an entity
# You first the define basic constraints like ordered, unique, readonly and
# required. Then type and it's cardinality are defined. And lastly the reference to another
# entity is shown.
def prop():             return Kwd("prop"), ZeroOrMore([Kwd("ordered"),Kwd("unique"), Kwd("readonly"),
                            Kwd("required")]), Optional("+"), type_def, Optional(ref), Optional(constr_def), Optional(named_elem)
def type_def():         return ident,  Optional("[", Optional(integer),"]"), ident
def ref():              return "<>", ident

# Defines set of operations you can perform on an entity.
# Operations have parameters they take in, exceptions their throw, like
# any standard method in a general purpose language
def oper():             return Kwd("op"), ZeroOrMore([Kwd("ordered"),Kwd("unique"),
                            Kwd("required")]), type_def, "(", Optional(param, ZeroOrMore(",", param)
                            ), ")", Optional("throws", ident,
                            ZeroOrMore(",", ident) ), Optional(constr_def), Optional(named_elem)

def param():           return ZeroOrMore([Kwd("ordered"), Kwd("unique"), Kwd("required")]
                            ), type_def, Optional(constr_def), Optional(named_elem)
# Feature and operation compartments, group a set of feature
# or operations into a single logical part
def feature_compart():  return Kwd("compartment"), ident, Optional(named_elem), "{", ZeroOrMore(feature), "}"

def oper_compart():     return Kwd("compartment"), ident, Optional(named_elem), "{", ZeroOrMore(oper), "}"

# Value objects are objects that have no operations, only properties
def value_object():     return Kwd("valueObject"), ident, Optional(Kwd("extends"), ident), Optional(Kwd("depends"), ident,
                             ZeroOrMore(",", ident)), Optional(named_elem), "{", Optional(constr_def), ZeroOrMore(prop), "}"

# Defines exceptions in DOMMLite, which are entities that are used for
# reporting errors.
def exception():        return Kwd("exception"), ident, Optional(named_elem), "{", ZeroOrMore(prop), "}"

# Defines the model rule of DOMMLite
# which is a container for one or more types or packages
def model() :           return Kwd("model"), ident, Optional(named_elem), ZeroOrMore(types), ZeroOrMore(package)


# The basic root rule of grammar defintion
def domm():             return OneOrMore(model), EndOfFile

# Next block connects semantic actions with
# Parser rules.
model.sem = ModelAction()
named_elem.sem = NamedElementAction()
string.sem = StringAction()
ident.sem = IdAction()
integer.sem = IntAction()
types.sem = TypesAction()
enum_literals.sem = EnumLiteralAction()

class DommParser(ParserPython):
    """docstring for DommParser"""
    def __init__(self, *args, **kwargs):
        super(DommParser, self).__init__(domm, None, *args, **kwargs)


if __name__ == "__main__":
    # First parameter is bibtex file
    # First we will make a parser - an instance of the DOMMLite parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = DommParser()

    # Then we export it to a dot file in order to visualise DOMMLite's model.
    # This step is optional but it is handy for debugging purposes.
    # We can make a png out of it using dot (part of graphviz) like this
    # dot -O -Tpng domm_parse_tree_model.dot
    PMDOTExporter().exportFile(parser.parser_model, "domm_parse_tree_model.dot")

    # We only parse if there is an input
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as dommfile:
            content = dommfile.read()
        # An expression we want to evaluate

        # We create a parse tree out of textual input_expr
        parse_tree = parser.parse(content)

        # Then we export it to a dot file in order to visualise it.
        # This is also optional.
        PTDOTExporter().exportFile(parse_tree, "domm_parse_tree.dot")

        parser.getASG()
    else:
        print("Usage: python parser.py file_to_parse")
