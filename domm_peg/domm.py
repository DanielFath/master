##############################################################################
# Name: domm_peg.py
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

# Defines a meta type named element and its sub rules
def named_elem():       return Optional(string), Optional(string)

# Defines basic literalls
def string():           return '"', _('[^"]*'),'"'
def id():               return _(r'[a-zA-Z_]([a-zA-Z_]|[0-9])*')
def integer():               return _(r'([1-9][0-9]*)|[0-9]')

# Defines the starting rules for all types
# defines categorization of said types into data_types and constraints
def types():            return [data_types, constraint_type]
# Defines data_types as either user made types, built-in types (e.g. integer, string)
# and enumerations of elements
def data_types():       return [user_type, built_type, enum]
def user_type():        return Kwd("dataType"), id, named_elem
def built_type():       return Kwd("buildinDataType"), id, named_elem

# Defines the rules for enumeration literals
def enum():             return Kwd("enum"), id, named_elem, "{", OneOrMore(enum_literals), "}"
def enum_literals():    return id, string, named_elem

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
def builtin_valid():    return Kwd("builtInValidatorType"), common_tag
def common_tag():       return id, Optional(constr_def), Optional(apply_def), Optional(string), Optional(string)
def constr_def():       return "(", Optional(constr_type), ZeroOrMore(",", constr_type), ")"
def apply_def():        return Kwd("appliesTo"), ZeroOrMore([Kwd("_entity"), Kwd("_prop"),
                            Kwd("_param"), Kwd("_op"), Kwd("_service"), Kwd("_valueObject")])
def constr_type():      return [Kwd("_string"), Kwd("_int"), Kwd("_ref"), Kwd("...")]

# Defines package which is a unit of code organization, which may contain other nested packages
def package():          return Kwd("package"), id, named_elem, "{", ZeroOrMore(pack_elem), "}"
def pack_elem():        return [package,classifier]

# Defines rules for various structure classifications (i.e. package elements)
def classifier():       return [entity, service, value_object, exception, data_types,constraint_type]

# Defines an entity in DOMMLite model that often represents actors in the business model
def entity():           return Kwd("entity"), id, Optional(Kwd("extends"), id), Optional(Kwd("depends"), id,
                             ZeroOrMore(",", id)), named_elem, "{", key, repr, Optional(constr_def
                             ), ZeroOrMore(feature), ZeroOrMore(feature_compart), "}"
# Defines service in DOMMLite model that provides one or more operations.
def service():          return Kwd("service"), id, Optional(Kwd("extends"), id), Optional(Kwd("depends"), id,
                             ZeroOrMore(",", id)), named_elem, "{", Optional(constr_def), ZeroOrMore(oper
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
def constr_def():       return "[", constr_spec, ZeroOrMore(",", constr_spec), "]"
def constr_spec():      return constraint_type, Optional("(", constr_param, ZeroOrMore(",", constr_param), ")"),
def constr_param():     return [string, prop, integer]

# Feature represents a combinationf of properties and operation which
# are features of other classifiers
def feature():          return [prop, oper]

# Defines property of an entity
# You first the define basic constraints like ordered, unique, readonly and
# required. Then type and it's cardinality are defined. And lastly the reference to another
# entity is shown.
def prop():             return Kwd("prop"), ZeroOrMore([Kwd("ordered"),Kwd("unique"), Kwd("readonly"),
                            Kwd("required")]), Optional("+"), type_def, Optional(ref), Optional(constr_def), named_elem
def type_def():         return id,  Optional("[", Optional(integer),"]"), id
def ref():              return "<>", id

# Defines set of operations you can perform on an entity.
# Operations have parameters they take in, exceptions their throw, like
# any standard method in a general purpose language
def oper():             return Kwd("op"), ZeroOrMore([Kwd("ordered"),Kwd("unique"),
                            Kwd("required")]), type_def, "(", Optional(param, ZeroOrMore(",", param)
                            ), ")", Optional("throws", id,
                            ZeroOrMore(",", id) ), Optional(constr_def), named_elem

def param():           return ZeroOrMore([Kwd("ordered"), Kwd("unique"), Kwd("required")]
                            ), type_def, Optional(constr_def), named_elem
# Feature and operation compartments, group a set of feature
# or operations into a single logical part
def feature_compart():  return Kwd("compartment"), id, named_elem, "{", ZeroOrMore(feature), "}"

def oper_compart():     return Kwd("compartment"), id, named_elem, "{", ZeroOrMore(oper), "}"

# Value objects are objects that have no operations, only properties
def value_object():     return Kwd("valueObject"), id, Optional(Kwd("extends"), id), Optional(Kwd("depends"), id,
                             ZeroOrMore(",", id)), named_elem, "{", Optional(constr_def), ZeroOrMore(prop), "}"

# Defines exceptions in DOMMLite, which are entities that are used for
# reporting errors.
def exception():        return Kwd("exception"), id, named_elem, "{", ZeroOrMore(prop), "}"

# Defines the model rule of DOMMLite
# which is a container for one or more types or packages
def model() :           return Kwd("model"), id, named_elem, ZeroOrMore(types), ZeroOrMore(package)

# The basic root rule of grammar defintion
def domm():             return OneOrMore(model), EndOfFile

if __name__ == "__main__":
    # First parameter is bibtex file
    # First we will make a parser - an instance of the DOMMLite parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = ParserPython(domm)

    # Then we export it to a dot file in order to visualise DOMMLite's model.
    # This step is optional but it is handy for debugging purposes.
    # We can make a png out of it using dot (part of graphviz) like this
    # dot -O -Tpng domm_parse_tree_model.dot
    PMDOTExporter().exportFile(parser.parser_model, "domm_parse_tree_model.dot")

    # We only parse if there is an input
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as bibtexfile:
            content = bibtexfile.read()
        # An expression we want to evaluate

        # We create a parse tree out of textual input_expr
        parse_tree = parser.parse(content)

        # Then we export it to a dot file in order to visualise it.
        # This is also optional.
        PTDOTExporter().exportFile(parse_tree, "domm_parse_tree.dot")
    else:
        print("Usage: python domm_peg.py file_to_parse")