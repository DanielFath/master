##############################################################################
# Name: metamodel.py
# Purpose: Meta model for DOMMLite DSL
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
from error import *

class NamedElement(object):
    """
    Named element represents short and long description
    that is encountered accross various DOMMLite constructs
    """
    def __init__(self, short_desc = None, long_desc = None):
        super(NamedElement, self).__init__()
        self.short_desc = short_desc
        self.long_desc = long_desc

    def set_desc(self, short_desc, long_desc):
        self.short_desc = short_desc
        self.long_desc = long_desc
    """
    Pretty print named element out
    """
    def __repr__(self):
        return 'Named element { short_desc = "%s" long_desc  = "%s" }' % (self.short_desc, self.long_desc)

class Id(object):

    all_id = set()

    """
    Id that represents a name of a type or a parameter
    """
    def __init__(self, id):
        super(Id, self).__init__()
        self._checked_add(id)
        self._id = id;

    def _checked_add(self, ids):
        if ids in Id.all_id:
            raise IdExistsError(ids)
        else:
            Id.all_id.add(ids)

    def __repr__(self):
        return 'Id("%s")' % (self._id)

class Model(NamedElement):
    """
    This class represents the meta model for DOMMLite model
    object. DOMMLite model is a container for other objects.
    """
    def __init__(self, name =None, short_desc = None, long_desc = None):
        super(Model, self).__init__(short_desc, long_desc)
        self.name = name
        self.types = set()
        self.constrs = set()
        self.packages = set()

    def add_type(self, type_def):
        self.types.add(type_def)

    def set_types(self, types):
        self.types = types

    def add_package(self, package):
        self.packages.add(package)

    def set_types(self, packages):
        self.packages = packages

    def add_constraint(self, constr):
        self.constrs.add(constr)

    def set_packages(self, packages):
        self.packages = packages

    def __repr__(self):
        return 'Model "%s" (%s %s)\ntypes: %s\nconstraint: %s\n%s' % (
            self.name, self.short_desc, self.long_desc, self.types, self.constrs, self.packages)

class DataType(NamedElement):

    all_types = set()

    def __init__(self, name, short_desc = None, long_desc = None, built_in = False):
        super(DataType, self).__init__(short_desc, long_desc)
        self._checked_add(name)
        self.built_in = built_in

    def _checked_add(self, name):
        if name in DataType.all_types:
            raise TypeExistsError(name)
        else:
            self.name = name
            DataType.all_types.add(name)

    def __repr__(self):
        return '\ndataType "%s" built_in(%s) (%s %s)' % (
            self.name, self.built_in, self.short_desc, self.long_desc)

class CommonTag(NamedElement):
    """
    Common function signature for Tags/Validators
    """
    def __init__(self, name, short_desc = None, long_desc = None, constr = None, applies = None):
        super(CommonTag, self).__init__(short_desc, long_desc)
        self.name = name
        self.constr = constr
        self.applies = applies

    def __repr__(self):
        return 'common_tag %s %s %s' % (self.name, self.constr, self.applies)

class ConstraintType(object):
    Tag, Validator = range(2)

class Constraint(object):
    """
    A unified container for tagTypes and validators,
    both built-in and user defined.
    """

    all_constraints = set()

    def __init__(self, tag = None, built_in = False, constr_type = None):
        super(Constraint, self).__init__()
        self.tag = None
        self._checked_add(tag)
        self.built_in = built_in
        self.constr_type = constr_type

    def _checked_add(self, tag):

        if tag is None:
            return
        elif tag.name in self.all_constraints:
            raise DuplicateTypeError(tag.name)
        else:
            self.tag = tag
            Constraint.all_constraints.add(tag.name)

    def __repr__(self):
        retStr = '\n'
        if self.built_in == True and self.constr_type == ConstraintType.Tag:
            retStr += 'buildinTagType'
        elif self.built_in == False and self.constr_type == ConstraintType.Tag:
            retStr += 'tagType'
        elif self.built_in == True and self.constr_type == ConstraintType.Validator:
            retStr += 'buildinValidator'
        elif self.built_in == False and self.constr_type == ConstraintType.Validator:
            retStr += 'validator'

        if self.tag is not None:
            retStr += ' %s appliesTo %s %s ' % (self.tag.name, self.tag.applies, self.tag.constr)

        return retStr

class Enumeration(NamedElement):

    all_enums = set()

    def __init__(self, name, short_desc = None, long_desc = None):
        super(Enumeration, self).__init__(short_desc, long_desc)
        self._checked_add(name)
        self.literals = set()

    def _checked_add(self, name):
        if name in Enumeration.all_enums:
            raise TypeExistsError(name)
        else:
            self.name = name
            Enumeration.all_enums.add(name)

    def add_literal(self, literal):
        if literal in self.literals:
            raise DuplicateLiteralError(literal.name)
        else:
            self.literals.add(literal)

    def __repr__(self):
        retStr = '\nenum %s (%s, %s) {' % (self.name, self.short_desc, self.long_desc)
        for i in self.literals:
            retStr += ' %s \n' % (i)
        retStr += "}"
        return retStr


class EnumLiteral(NamedElement):
    """
    Enumeration literal
    """
    def __init__(self, value, name, short_desc = None, long_desc = None):
        super(EnumLiteral, self).__init__(short_desc = None, long_desc = None)
        self.value = value
        self.name = name

    def __repr__(self):
        return ' %s - %s (%s, %s)' % (self.name, self.value, self.short_desc, self.long_desc)

class ApplyDef(object):
    """
    Apply def signature. There can't be multiple applies on same type of parameter.
    For example, you can't have a `applyTo _str _str`.
    """
    def __init__(self):
        super(ApplyDef, self).__init__()
        self.applies = set()

    def add_apply(self, appl):
        if appl in self.applies:
            raise DuplicateApplyError(appl)
        else:
            self.applies.add(appl)

    def __repr__(self):
        retStr = ' applies to ('
        for i in self.applies:
            retStr += ' %s ' % i
        retStr += ')'
        return retStr

class ConstrDef(object):
    """
    Apply constr signature
    """
    def __init__(self):
        super(ConstrDef, self).__init__()
        self.constraints = set()

    def add_constr(self, constr):
        if "..." in self.constraints:
            raise ElipsisMustBeLast()
        else:
            self.constraints.add(constr)

    def __repr__(self):
        retStr = ' constr ['
        for i in self.constraints:
            retStr += ' %s ' % i
        retStr += ']'
        return retStr

class Package(NamedElement):
    """
    Package model that contains other packages or package elements
    """
    def __init__(self, name = None, short_desc = None, long_desc = None):
        super(Package, self).__init__(short_desc=short_desc, long_desc=long_desc)
        self.name = name
        self.elems = set()

    def set_name(self, name):
        self.name = name

    def add_elem(self, element):
        self.elems.add(element)

    def __repr__(self):
        retStr = '\n--------------\npackage %s {\n' % self.name
        for i in self.elems:
            retStr += ' %s '% i
        retStr += "}\n--------------\n"
        return retStr

class ExceptionType(NamedElement):
    """
    Exception object describing models
    """
    def __init__(self, name = None, short_desc = None, long_desc = None):
        super(Exception, self).__init__(short_desc = short_desc, long_desc = long_desc)
