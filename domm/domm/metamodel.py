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
    def __init__(self, name, short_desc = None, long_desc = None):
        super(Model, self).__init__(short_desc, long_desc)
        self.name = name
        self.types = set()
        self.packages = set()

    def add_types(self, type_def):
        self.types.add(type_def)

    def set_types(self, types):
        self.types = types

    def add_package(self, package):
        self.packages.add(package)

    def set_types(self, packages):
        self.packages = packages

    def __repr__(self):
        return 'Model "%s" (%s %s)\ntypes: "%s"' % (self.name, self.short_desc, self.long_desc, self.types)


class DataType(NamedElement):

    all_types = set()

    def __init__(self, name, short_desc = None, long_desc = None, built_in = True):
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
        return 'dataType "%s" built_in(%s) (%s %s)' % (
            self.name, self.built_in, self.short_desc, self.long_desc)

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
        retStr = ' enum %s (%s, %s) {' % (self.name, self.short_desc, self.long_desc)
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
