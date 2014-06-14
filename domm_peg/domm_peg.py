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
# By Igor Dejanovich. The work can be found at:
#   Library of Faculty of Engineering,
#   Trg D. Obradovica 6, Novi Sad
##############################################################################
from arpeggio import *
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _


# Defines basic litterals
# Defines a meta type named element and its sub rules
def named_elem():       return Optional(shortdesc), Optional(longdesc)
def shortdesc():        return string
def longdesc():         return string

# Defines basic literalls
def string():           return '"', _('[^"]*'),'"'
def id():               return _(r'[a-zA-Z_]([a-zA-Z_]|[0-9])*')
def integer():               return _(r'([1-9][0-9]*)|[0-9]')

def model() :           return Kwd("model"), id, named_elem
                               # ZeroOrMore(types), ZeroOrMore(package)

"""



def types():            return [data_types, constraint_type]
def data_types():       return [user_type, built_type, enum]
def user_type():        return Kwd("dataType"), id, Optional(string), Optional(string)
def built_type():       return Kwd("buildinDataType"), id, Optional(string), Optional(string)

def enum():             return Kwd("enum"), id, Optional(string), Optional(string), "{",
                                OneOrMore(enum_literals), "}"
def enum_literals():    return id, string,  Optional(string), Optional(string)

def constraint_type():  return [tag_type, validator_type]
def tag_type():         return [user_tag, builtin_tag]
def user_tag():         return Kwd("tagType"), common_tag
def builtin_tag():      return Kwd("buildinTagType"), common_tag
def validator_type():   return [user_validator, builtin_valid]
def user_validator():   return Kwd("validatorType"), common_tag
def builtin_valid():    return Kwd("builtInValidatorType"), common_tag


def common_tag():       return id, Optional(constr_def), Optional(apply_def), Optional(string), Optional(string)
def constr_def():       return "(", Optional(constr_type), ZeroOrMore(",", constr_type), ")"
def apply_def():        return Kwd("appliesTo") ZeroOrMore([Kwd("_entity"), Kwd("_prop"), Kwd("_param"), Kwd("_op"), Kwd("_service"), Kwd("_valueObject")])
def constr_type():      return [Kwd("_string"), Kwd("_int"), Kwd("_ref"), Kwd("...")]

def package():          return Kwd("package"), id, Optional(string), Optional(string), "{", ZeroOrMore(pack_elem) "}"
def pack_elem():        return [package,classifier]

def classifier():       return [entity, service, value_object, exception, data_types,constraint_type]
def entity():           return Kwd("entity"), id, Optional(Kwd("extends"), id),
                                Optional(Kwd("depends"), id, Optional(",", id))
                                Optional(string), Optional(string),
                                "{", key, repr, feature, feature_compart,
                                "}"
def key():              return Kwd("key"), "{", "}"
def repr():             return Kwd("repr"), repr_param, Optional(ZeroOrMore(",", repr_param))
def constr_def():       return "[", constr_spec, Optional(ZeroOrMore(",", constr_spec)), "]"
def constr_spec():      return constraint_type, "(", Optional(constr_param),
                                    Optional(ZeroOrMore(",", constr_param))")"
def repr_param():       return [string, prop]
def constr_param():     return [string, prop, integer]
def feature():          return [prop, oper]
def oper():             return Kwd("op"), ZeroOrMore([Kwd("ordered"),Kwd("unique"), Kwd("required")]),
                                classifier, Optional("[", Optional(integer),"]"), id,
                                "(", Optional(parameter), Optional(ZeroOrMore(",", parameter)), ")"
                                Optional(Kwd("throws"), exception, Optional(ZeroOrMore(",", exception))
                                constr_def, Optional(string), Optional(string)
def prop():             return Kwd("prop"), ZeroOrMore([Kwd("ordered"),Kwd("unique"), Kwd("readonly"), Kwd("required")]),
                                Optional("+"), type_def, id,
                                Optional(Kwd("<>"), prop), constr_def, Optional(string), Optional(string)

def parameter():        return ZeroOrMore([Kwd("ordered"), Kwd("unique"), Kwd("required")])
def feature_compart():  return Kwd("compartment"), id, Optional(string), Optional(string),
                                "{", ZeroOrMore(feature), "}"

def type_def():         return classifier, Optional("[", Optional(integer),"]"), constr_spec, Optional(string), Optional(string)


def oper_compart():  return Kwd("compartment"), id, Optional(string), Optional(string),
                                "{", ZeroOrMore(oper), "}"

def exception():        return Kwd("exception"), id, Optional(string), Optional(string),
                                "{", ZeroOrMore(prop), "}"
"""



# The basic root rule of grammar defintion
def domm():             return OneOrMore(model), EndOfFile

if __name__ == "__main__":
    # First we will make a parser - an instance of the DOMMLite parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = ParserPython(domm)

    # Then we export it to a dot file in order to visualise DOMMLite's model.
    # This step is optional but it is handy for debugging purposes.
    # We can make a png out of it using dot (part of graphviz) like this
    # dot -O -Tpng domm_parse_tree_model.dot
    PMDOTExporter().exportFile(parser.parser_model, "domm_parse_tree_model.dot")

    # An expression we want to evaluate
    input_expr = """model example "short desc" "long desc" """

    # We create a parse tree out of textual input_expr
    parse_tree = parser.parse(input_expr)

    # Then we export it to a dot file in order to visualise it.
    # This is also optional.
    PTDOTExporter().exportFile(parse_tree, "domm_parse_tree.dot")