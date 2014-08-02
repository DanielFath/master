﻿##############################################################################
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

class NamespaceResolver(object):
    """
    A utility class that temporarily stores and resolves
    namespace problems
    """
    def __init__(self):
        super(NamespaceResolver, self).__init__()
        self.all_id = set()
        self.all_datatypes = set()
        self.all_constraints = set()
        self.all_enums = set()
        self.exceptions = set()
        self.types = dict()

    def check(self, obj):
        if obj is None:
            return

        if type(obj) is Id:
            self.add_id(obj)
        elif type(obj) is DataType:
            self.add_datatype(obj, obj.name)
        elif type(obj) is Constraint:
            self.add_tag(obj)
        elif type(obj) is Enumeration:
            self.add_enum(obj, obj.name)
        elif type(obj) is ExceptionType:
            self.add_exception(obj)

    def add_id(self, ident):
        if ident in self.all_id:
            raise IdExistsError(ident)
        else:
            self.all_id.add(ident)

    def add_datatype(self, data_type, name):
        if name in self.all_datatypes:
            raise TypeExistsError(name)
        else:
            self.all_datatypes.add(name)
            self.types[name] = data_type

    def add_tag(self, obj):
        if obj.tag.name in self.all_constraints:
            raise DuplicateTypeError(obj.tag.name)
        else:
            self.all_constraints.add(obj.tag.name)

    def add_enum(self, enum, enum_name):
        if enum_name in self.all_enums:
            raise TypeExistsError(enum_name)
        else:
            self.all_enums.add(enum_name)
            self.types[enum_name] = enum

    def add_exception(self, excp, excp_name):
        if excp_name in self.exceptions:
            raise ExceptionExistsError(excp_name)
        else:
            self.exceptions.add(excp_name)
            self.types[excp_name] = excp

class NamespacedObject(object):
    """
    These are objects that belong to a certain namespace
    """
    def __init__(self, namespace):
        super(NamespacedObject, self).__init__()
        self._namespace = namespace

    def _check(self):
        if self._namespace is not None:
            self._namespace.check(self)

class NamedElement(object):
    """
    Named element represents short and long description
    that is encountered accross various DOMMLite constructs
    """
    def __init__(self, name = None, short_desc = None, long_desc = None):
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc

    def set_desc(self, short_desc, long_desc):
        self.short_desc = short_desc
        self.long_desc = long_desc

    def __repr__(self):
        """
        Pretty print named element out
        """
        return 'Named element { short_desc = "%s" long_desc  = "%s" }' % (self.short_desc, self.long_desc)

class Id(NamespacedObject):
    """
    Id that represents a name of a type or a parameter
    """
    def __init__(self, ident, namespace = None):
        super(Id, self).__init__(namespace)
        self._id = ident;
        self._check()

    def __repr__(self):
        return 'Id("%s")' % (self._id)



class Model(NamedElement):
    """
    This class represents the meta model for DOMMLite model
    object. DOMMLite model is a container for other objects.
    """
    def __init__(self, name =None, short_desc = None, long_desc = None):
        super(Model, self).__init__(name, short_desc, long_desc)
        self.types = set()
        self.constrs = set()
        self.packages = set()

    def add_type(self, type_def):
        self.types.add(type_def)
        return self

    def set_types(self, types):
        self.types = types
        return self

    def add_package(self, package):
        self.packages.add(package)
        return self

    def set_types(self, packages):
        self.packages = packages
        return self

    def add_constraint(self, constr):
        self.constrs.add(constr)
        return self

    def set_packages(self, packages):
        self.packages = packages
        return self

    def __repr__(self):
        return 'Model "%s" (%s %s)\ntypes: %s\nconstraint: %s\n%s' % (
            self.name, self.short_desc, self.long_desc, self.types, self.constrs, self.packages)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.short_desc == other.short_desc and (
                self.types == other.types and self.constrs == other.constrs and self.packages == other.packages)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class DataType(NamedElement, NamespacedObject):


    def __init__(self, name, short_desc = None, long_desc = None, built_in = False, namespace = None):
        super(DataType, self).__init__(name, short_desc, long_desc)
        self._namespace = namespace
        self.built_in = built_in
        self._check()

    def __repr__(self):
        return '\ndataType "%s" built_in(%s) (%s %s)' % (
            self.name, self.built_in, self.short_desc, self.long_desc)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.built_in == other.built_in
        else:
            return False

    def __hash__(self):
        return hash((self.name, self.built_in))

    def __ne__(self, other):
        return not self.__eq__(other)

class CommonTag(NamedElement):
    """
    Common function signature for Tags/Validators
    """
    def __init__(self, name, short_desc = None, long_desc = None, constr_def = None, applies = None):
        super(CommonTag, self).__init__(name, short_desc, long_desc)
        self.constr_def = constr_def
        self.applies = applies

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.short_desc == other.short_desc and self.long_desc == other.long_desc and (
                self.constr_def == other.constr_def and self.applies == other.applies)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.constr_def, self.applies))

    def __repr__(self):
        return 'common_tag %s %s %s [%s %s]' % (self.name, self.constr_def, self.applies, self.short_desc, self.long_desc)

class ConstraintType(object):
    Tag, Validator = range(2)

class Constraint(NamespacedObject):
    """
    A unified container for tagTypes and validators,
    both built-in and user defined.
    """

    def __init__(self, tag = None, built_in = False, constr_type = None, namespace = None):
        super(Constraint, self).__init__(namespace)
        self.tag = tag
        self.built_in = built_in
        self.constr_type = constr_type
        self._check()

    def __repr__(self):
        retStr = '\n'
        if self.built_in == True and self.constr_type == ConstraintType.Tag:
            retStr += 'buildinTagType'
        elif self.built_in == False and self.constr_type == ConstraintType.Tag:
            retStr += 'tagType'
        elif self.built_in == True and self.constr_type == ConstraintType.Validator:
            retStr += 'buildinValidator'
        elif self.built_in == False and self.constr_type == ConstraintType.Validator:
            retStr += 'validatorType'

        if self.tag is not None:
            retStr += ' %s ' % self.tag.name
            if self.tag.constr_def is not None:
                retStr += ' %s ' % self.tag.constr_def
            if self.tag.applies is not None:
                retStr += ' %s ' %self.tag.applies
            retStr += ' "%s" "%s"' % (self.tag.short_desc, self.tag.long_desc)

        return retStr

    def __eq__(self, other):
        if type(other) is type(self):
            # WARNING can't use __dict__ == __dict__ because namespace is transient
            return self.built_in == other.built_in and self.tag == other.tag and self.constr_type == other.constr_type
        else:
            return False

    def __hash__(self):
        return hash((self.tag, self.built_in, self.constr_type))

    def __ne__(self, other):
        return not self.__eq__(other)

class Enumeration(NamedElement, NamespacedObject):


    def __init__(self, name, short_desc = None, long_desc = None, namespace = None):
        super(Enumeration, self).__init__(name, short_desc, long_desc)
        self.namespace = namespace
        self.literals = set()
        self._check()

    def add_all_literals(self, list_literals):
        assert type(list_literals) is list
        for i in list_literals:
            self.add_literal(i)

        return self

    def add_literal(self, literal):
        if literal in self.literals:
            raise DuplicateLiteralError(literal.name)
        else:
            self.literals.add(literal)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, hash(frozenset(self.literals)) ))

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.short_desc == other.short_desc and self.long_desc == other.long_desc and self.literals == other.literals
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

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
        super(EnumLiteral, self).__init__(name, short_desc, long_desc)
        self.value = value

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value  and self.name == other.name and (
                self.short_desc == other.short_desc and self.long_desc == other.short_desc)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.value, self.name, self.short_desc, self.long_desc))

    def __repr__(self):
        return ' %s - %s (%s, %s)' % (self.name, self.value, self.short_desc, self.long_desc)

class ApplyDef(object):
    """
    Apply def signature. There can't be multiple applies on same type of parameter.
    For example, you can't have a `applyTo _str _str`.
    """
    def __init__(self, to_entity = False, to_prop = False, to_param = False, to_service = False, to_op = False, to_value_object = False):
        super(ApplyDef, self).__init__()
        self.to_entity = to_entity
        self.to_prop = to_prop
        self.to_param = to_param
        self.to_service = to_service
        self.to_op = to_op
        self.to_value_object = to_value_object

    def add_apply(self, appl):
        if appl == "_entity":
            if self.to_entity:
                raise DuplicateApplyError(appl)
            else:
                self.to_entity = True

        if appl == "_prop":
            if self.to_prop:
                raise DuplicateApplyError(appl)
            else:
                self.to_prop = True

        if appl == "_param":
            if self.to_param:
                raise DuplicateApplyError(appl)
            else:
                self.to_param = True

        if appl == "_service":
            if self.to_service:
                raise DuplicateApplyError(appl)
            else:
                self.to_service = True

        if appl == "_op":
            if self.to_op:
                raise DuplicateApplyError(appl)
            else:
                self.to_op = True

        if appl == "_valueObject":
            if self.to_value_object:
                raise DuplicateApplyError(appl)
            else:
                self.to_value_object = True

        return self

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.to_entity, self.to_prop, self.to_param, self.to_service, self.to_op, self.to_value_object))

    def __repr__(self):
        retStr = ' appliesTo '
        if self.to_entity:
            retStr += "_entity "
        if self.to_prop:
            retStr += "_prop "
        if self.to_param:
            retStr += "_param "
        if self.to_service:
            retStr += "_service "
        if self.to_op:
            retStr += "_op "
        if self.to_value_object:
            retStr += "_valueObject "
        return retStr

class ConstrDef(object):
    """
    Apply constr signature
    """
    def __init__(self, constraints = None):
        super(ConstrDef, self).__init__()
        self.constraints = list()
        if constraints is not None and type(constraints) is list:
            for i in constraints:
                self.add_constr(i)

    def add_constr(self, constr):
        if "..." in self.constraints:
            raise ElipsisMustBeLast()
        else:
            self.constraints.append(constr)
        return self

    def verify(self, field):
        pass

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

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
        super(Package, self).__init__(name, short_desc, long_desc)
        self.elems = set()

    def set_name(self, name):
        self.name = name

    def add_elem(self, element):
        self.elems.add(element)
        return self

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.short_desc == other.short_desc and self.long_desc == other.long_desc and self.elems == other.elems
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, hash(frozenset(self.elems)) ))

    def __repr__(self):
        retStr = '\n--------------\npackage %s {\n' % self.name
        for i in self.elems:
            retStr += ' %s '% i
        retStr += "}\n--------------\n"
        return retStr

class ExceptionType(NamedElement, NamespacedObject):
    """
    Exception object describing models
    """

    def __init__(self, name = None, short_desc = None, long_desc = None):
        super(ExceptionType, self).__init__(name, short_desc, long_desc)
        self.props = dict()
        self._check()


    def add_prop(self, prop):
        # In exception we can't for example have two same named fields
        #
        # exception FileNotFound {
        #    prop int errorCode
        #    prop char errorCode
        # }
        # Can't exist simultaneously
        if prop.name in self.props:
            raise DuplicatePropertyerror(prop.name)
        else:
            self.props[prop.name] = prop

        return self

class Relationship(object):
    """Describes all properties of a Relationship property"""
    def __init__(self, containment = False, opposite_end = None):
        super(Relationship, self).__init__()
        self.containment = containment
        self.opposite_end = opposite_end

class TypeDef(NamedElement):

    def __init__(self, name = None, short_desc = None, long_desc = None):
        super(TypeDef, self).__init__(name, short_desc, long_desc)
        self.name = name
        self.type = None
        self.container = False
        self.multi = None

    def set_multi(self, multi = None):
        if multi is None:
            self.container = False
            self.multi = None
        elif multi is not None and multi > 0:
            self.container = True
            self.multi = multi

    def set_type(self, type_sign):
        self.type = type_sign

    def __repr__(self):
        retStr = " %s of type %s" % (self.name, self.type)
        if self.container:
            retStr += "["
            if self.multi is not None:
                retStr += "%s" % (self.multi)
            retStr += "]"
        return retStr

class ConstraintSpec(object):
    """
    Constraint specification applies constraint to an bound entity
    """
    def __init__(self, ident = None):
        super(ConstraintSpec, self).__init__()
        self.ident = ident
        self.parameters = set()
        self.bound = None

    # Returns whether the constraint spec matched by id
    # is compatible with property it is bound to
    # and the parameters provided
    def verify(self, constraint):
        pass

    def add_param(self, param):
        self.parameters.add(param)

    def __repr__(self):
        retStr = " [ %s " % self.ident
        for val in self.parameters:
            retStr += " `%s` " % val
        retStr += " ]"
        return retStr



class Property(NamedElement):
    """
    Models properties of entities and other programming objects
    """
    def __init__(self, name = None, short_desc = None, long_desc = None):
        super(Property, self).__init__(name, short_desc, long_desc)

        self.ordered = False
        self.unique = False
        self.readonly = False
        self.required = False
        self.composite = False

        self.type_def = None
        self.relationship = None
        self.constraints = set()

    def add_constraint_spec(self, constraint_spec):
        self.constraints.add(constraint_spec)

    def __repr__(self):
        retStr = " prop "
        if self.ordered:
            retStr += " ordered "
        if self.unique:
            retStr += " unique "
        if self.readonly:
            retStr += " readonly "
        if self.required:
            retStr += " required "

        retStr += " %s  %s " % (self.type_def, self.relationship)

        return retStr