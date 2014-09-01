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
def name():             return _(r'[a-zA-Z_]([a-zA-Z_]|[0-9])*')
def qual_ident():       return _(r'([a-zA-Z_]([a-zA-Z_]|[0-9])*\.)*[a-zA-Z_]([a-zA-Z_]|[0-9])*')
def integer():          return _(r'([1-9][0-9]*)|[0-9]')
def rel_id():           return [qual_ident, name]

# Defines the starting rules for all types
# defines categorization of said types into data_types and constraints
def types():            return [data_types, constraint_type]
# Defines data_types as either user made types, built-in types (e.g. integer, string)
# and enumerations of elements
def data_types():       return [user_type, built_type, enum]
def user_type():        return Kwd("dataType"), name, Optional(named_elem)
def built_type():       return Kwd("buildinDataType"), name, Optional(named_elem)

# Defines the rules for enumeration literals
def enum():             return Kwd("enum"), name, Optional(named_elem),\
                                "{", OneOrMore(enum_literals), "}"
def enum_literals():    return name, string, Optional(named_elem)

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
def builtin_valid():    return Kwd("buildinValidator"), common_tag
def common_tag():       return name, Optional(constr_def),\
                                Optional(apply_def), Optional(named_elem)
def constr_def():       return [("(", [elipsis, (constr_type, ",", elipsis)],\
                                ")"), ("(", constr_type, ZeroOrMore(",",\
                                    constr_type) , ")")]
def apply_def():        return Kwd("appliesTo"), ZeroOrMore([Kwd("_entity"),\
                                Kwd("_prop"), Kwd("_param"), Kwd("_op"),\
                                Kwd("_service"), Kwd("_valueObject")])
def constr_type():      return [Kwd("_string"), Kwd("_int"), Kwd("_ref")]
def elipsis():          return Kwd("...")

# Defines package which is a unit of code organization, which may contain other nested packages
def package():          return Kwd("package"), name, Optional(named_elem),\
                                "{", ZeroOrMore(pack_elem), "}"
def pack_elem():        return [package,classifier]

# Defines rules for various structure classifications (i.e. package elements)
def classifier():       return [entity, service, value_object, exception,\
                                types]

# Defines an entity in DOMMLite model that often represents actors
# in the business model
def entity():           return Kwd("entity"), name, Optional(ext_def),\
                            Optional(dep_def), Optional(oper),\
                            Optional(named_elem),\
                            "{", key, Optional(ent_repr), \
                            Optional(constr_speclist), ZeroOrMore(feature),\
                            ZeroOrMore(feature_compart), "}"
# Defines service in DOMMLite model that provides one or more operations.
def service():          return Kwd("service"), name, Optional(ext_def),\
                            Optional(dep_def), Optional(named_elem),\
                            "{", Optional(constr_speclist),\
                            ZeroOrMore(oper), ZeroOrMore(oper_compart), "}"

def ext_def():          return Kwd("extends"), rel_id
def dep_def():          return Kwd("depends"), rel_id, ZeroOrMore(",", rel_id)

# An entity contains a key through which it is referenced.
# This models something analogous to a complex database key.
def key():              return Kwd("key"), "{", OneOrMore(prop), "}"

# Representation of given entity in the system. For example
# a Person can be presented using their name and last name, despite having
# age, ID number, place of residence, etc.
def ent_repr():         return Kwd("repr"), repr_param, \
                            ZeroOrMore("+", repr_param)
def repr_param():       return [string, prop_ref]
def prop_ref():         return name
# Constraint definition defines a set of limitations to a type
# for instance we can define that some elements are between certain values.
# For examples grades of a student are between 1 and 5 (or A and F)
def constr_speclist():  return "[", constr_spec, ZeroOrMore(",", constr_spec),\
                            "]"
def constr_spec():      return rel_id, Optional("(", constr_param, \
                            ZeroOrMore(",", constr_param), ")"),
def constr_param():     return [string, name, integer]

# Feature represents a combinationf of properties and operation which
# are features of other classifiers
def feature():          return [prop, oper]

# Defines property of an entity
# You first the define basic constraints like ordered, unique, readonly and
# required. Then type and it's cardinality are defined. And lastly the reference to another
# entity is shown.
def prop():             return Kwd("prop"), ZeroOrMore([Kwd("ordered"),\
                            Kwd("unique"), Kwd("readonly"), Kwd("required")]),\
                            Optional("+"), type_def, Optional(ref), \
                            Optional(constr_speclist), Optional(named_elem)
def type_def():         return rel_id,  Optional("[", Optional(integer),"]"),\
                            name
def ref():              return "<>", rel_id

# Defines set of operations you can perform on an entity.
# Operations have parameters they take in, exceptions their throw, like
# any standard method in a general purpose language
def oper():             return Kwd("op"), ZeroOrMore([Kwd("ordered"),\
                            Kwd("unique"), Kwd("required")]), type_def,"(", \
                            Optional(op_param, ZeroOrMore(",", op_param)),\
                            ")", Optional("throws", rel_id, ZeroOrMore(",", \
                            rel_id) ), Optional(constr_speclist), \
                            Optional(named_elem)

def op_param():           return ZeroOrMore([Kwd("ordered"), Kwd("unique"),\
                            Kwd("required")]), type_def,\
                            Optional(constr_speclist), Optional(named_elem)

# Feature and operation compartments, group a set of feature
# or operations into a single logical part
def feature_compart():  return Kwd("compartment"), name, Optional(named_elem)\
                            , "{", ZeroOrMore(feature), "}"

def oper_compart():     return Kwd("compartment"), name, Optional(named_elem)\
                            , "{", ZeroOrMore(oper), "}"

# Value objects are objects that have no operations, only properties
def value_object():     return Kwd("valueObject"), name, Optional(ext_def),\
                            Optional(dep_def), Optional(named_elem), \
                            "{",Optional(constr_def), ZeroOrMore(prop), "}"

# Defines exceptions in DOMMLite, which are entities that are used for
# reporting errors.
def exception():        return Kwd("exception"), name, Optional(named_elem),\
                            "{", ZeroOrMore(prop), "}"

# Defines the model rule of DOMMLite
# which is a container for one or more types or packages
def model() :           return Kwd("model"), name, Optional(named_elem),\
                            ZeroOrMore([user_type, constraint_type]),\
                            ZeroOrMore(package)


# The basic root rule of grammar defintion
def domm():             return model, EOF

# Next block connects semantic actions with
# Parser rules.

# Root rules
model.sem = ModelAction()
# Basic types
string.sem = StringAction()
name.sem = IdAction()
qual_ident.sem = QidAction()
rel_id.sem = RelIdAction()
integer.sem = IntAction()

# Named element and dataTypes
named_elem.sem = NamedElementAction()
user_type.sem = DataTypeAction(built_in = False)
built_type.sem = DataTypeAction(built_in = True)

# Semantic actions for enumerations
enum.sem = EnumAction()
enum_literals.sem = EnumLiteralAction()

# Semantic actions for Validators/TagTypes and related constucts
elipsis.sem = ElipsisAction()
constr_def.sem = ConstrDefAction()
apply_def.sem = ApplyDefAction()
common_tag.sem = CommonTagAction()
user_validator.sem = ConstraintAction(built_in = False, is_tag = False)
builtin_valid.sem = ConstraintAction(built_in = True, is_tag = False)
user_tag.sem = ConstraintAction(built_in = False, is_tag = True)
builtin_tag.sem = ConstraintAction(built_in = True, is_tag = True)
type_def.sem = TypeDefAction()
constr_spec.sem = ConstraintSpecAction()
constr_speclist.sem = ConstraintSpecListAction()

# Semantic action for package
package.sem = PackageAction()

# Semantic actions for prop and related constructs
ref.sem = RefAction()
prop.sem = PropertyAction()

# Semantic actions for classifiers that extend/depend
ext_def.sem = ExtDefAction()
dep_def.sem = DepDefAction()

# Semantic actions for operation
oper.sem = OperationAction()
op_param.sem = OpParamAction()
oper_compart.sem = CompartmentAction(is_op = True)

#Semantic actions for entity components
key.sem = KeyAction()
ent_repr.sem = ReprAction()
prop_ref.sem = PropRefAction()

# Semantic action for classifiers
exception.sem = ExceptionAction()
service.sem = ServiceAction()
value_object.sem = ValueObjectAction()
entity.sem = EntityAction()

class DommParser(ParserPython):
    """
    Parser of DOMMLite DSL language
    """
    def __init__(self, debugDomm = False, *args, **kwargs):
        super(DommParser, self).__init__(domm, None, *args, **kwargs)
        self.debugDomm = debugDomm

    def string_into_ast(self, content):
        """
        Method that reads a given content, parses it and returns a parsed AST.
        After method retrns AST any used namespace is cleared.
        """
        self.parse(content)
        val = self.getASG()
        self.namespace = None
        return val



if __name__ == "__main__":
    # First parameter is bibtex file
    # First we will make a parser - an instance of the DOMMLite parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = DommParser(debugDomm = True)

    # Then we export it to a dot file in order to visualise DOMMLite's model.
    # This step is optional but it is handy for debugging purposes.
    # We can make a png out of it using dot (part of graphviz) like this
    # dot -O -Tpng domm_parse_tree_model.dot
    PMDOTExporter().exportFile(parser.parser_model,\
                    "domm_parse_tree_model.dot")

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
