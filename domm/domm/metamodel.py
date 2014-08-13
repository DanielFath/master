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
from enum import Enum

def fnvhash(a):
    """
    Fowler, Noll, Vo Hash function.
    Copied from this site: http://www.gossamer-threads.com/lists/python/python/679002#679002
    """
    h = 2166136261
    for i in a:
        t = (h * 16777619) & 0xffffffffL
        h = t ^ i.__hash__()

    return h

def print_constraints(constraints):
    retStr = ""
    if constraints and len(constraints) > 0:
        retStr += "["
        for c in constraints:
            if c.ident:
                retStr += "%s " % c.ident._id
            if c.parameters:
                retStr += "("
                for par in c.parameters:
                    val = par
                    if type(par) is Id:
                        val = par._id
                    retStr += " %s " % val
                retStr += ")"

        retStr += "]"
    return retStr

def print_partial_map(print_map, partial):
    assert type(print_map) is dict
    retStr = ""
    for part in partial:
        retStr += "\n%s" % print_map[part]
    return retStr

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
        self.exceptions = dict()
        self.types = dict()
        self.services = dict()

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
        elif type(obj) is Service:
            self.add_service(obj)

    def add_id(self, ident):
        # We're ignoring double identificatiors because the subtypes will
        # handle this for us

        #if ident in self.all_id:
        #    raise IdExistsError(ident._id)
        #else:
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

    def add_exception(self, excp):
        if excp.name in self.exceptions:
            raise ExceptionExistsError(excp_name)
        else:
            self.exceptions.add(excp_name)
            self.types[excp_name] = excp

    def add_service(self, serv):
        # TODO IMPLEMENT
        assert False

class NamespacedObject(object):
    """
    These are objects that belong to a certain namespace.

    They carry a link to their namespace and can be checked to
    see if they are valid in given namespace
    """
    def __init__(self, namespace):
        super(NamespacedObject, self).__init__()
        self._namespace = namespace

    def _check(self):
        if self._namespace is not None:
            self._namespace.check(self)

    def set_namespace(self, namespace):
        if namespace is not None:
            self._namespace = namespace
            self._check()

class NamedElement(object):
    """
    Named element represents short and long description
    that is encountered across various DOMMLite constructs
    """
    def __init__(self, name = None, short_desc = None, long_desc = None):
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc

    def set_desc(self, short_desc, long_desc):
        self.short_desc = short_desc
        self.long_desc = long_desc

    def set_from_named(self, named_el):
        assert type(named_el) is NamedElement
        assert named_el is not None
        self.short_desc = named_el.short_desc
        self.long_desc = named_el.long_desc

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.short_desc == other.short_desc and self.long_desc == other.long_desc
        return False

    def __repr__(self):
        """
        Pretty print named element out
        """
        return 'Named element { short_desc = "%s" long_desc  = "%s" }' %\
        (self.short_desc, self.long_desc)

class Id(NamespacedObject):
    """
    Id that represents a name of a type or a parameter
    """
    def __init__(self, ident, namespace = None):
        super(Id, self).__init__(namespace)
        self._id = ident;
        self._check()

    def __eq__(self, other):
        if type(other) is type(self):
            return self._id == other._id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return 'Id("%s")' % (self._id)

class Qid(object):
    """
    Qualified ID
    """
    def __init__(self, path):
        super(Qid, self).__init__()
        assert type(path) is list
        self.path = []
        if path and len(path) > 0:
            self.path = path

    def __eq__(self, other):
        if type(self) is type(other):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return fnvhash(self.path)

    def __repr__(self):
        retStr = "Qid("
        for i, part in enumerate(path):
            if i > 0:
                retStr += "."
            retStr += i
        retStr += ")"
        return retStr



class Model(NamedElement):
    """
    This class represents the meta model for DOMMLite model
    object. DOMMLite model is a container for other objects.
    """
    def __init__(self, name =None, short_desc = None, long_desc = None):
        super(Model, self).__init__(name, short_desc, long_desc)
        self.all = dict()
        self.types = set()
        self.constrs = set()
        self.packages = set()

    def add_type(self, type_def):
        assert type(type_def) is DataType
        if type_def and type_def.name:
            self.all[type_def.name] = type_def
            self.types.add(type_def.name)
        return self

    def add_package(self, package):
        assert type(package) is Package
        if package and package.name:
            self.all[package.name] = package
            self.types.add(package.name)
        return self


    def add_constraint(self, constr):
        assert type(constr) is Constraint
        if constr and constr.tag and constr.tag.name:
            self.all[constr.tag.name] = constr
            self.constrs.add(constr.tag.name)
        return self


    def __repr__(self):
        return 'Model "%s" (%s %s)\nall: %s\n' %\
        (self.name, self.short_desc, self.long_desc, self.all)

    def __eq__(self, other):
        if type(other) is type(self):
            return NamedElement.__eq__(self, other)\
                and self.all == other.all
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc,\
        fnvhash(self.all.items())))

    def __getitem__(self, key):
        return self.all[key]

class DataType(NamedElement, NamespacedObject):


    def __init__(self, name = None, short_desc = None, long_desc = None, built_in = False, namespace = None):
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
    def __init__(self, name = None, short_desc = None, long_desc = None, constr_def = None, applies = None):
        super(CommonTag, self).__init__(name, short_desc, long_desc)
        self.constr_def = constr_def
        self.applies = applies

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and\
            self.short_desc == other.short_desc and\
            self.long_desc == other.long_desc and\
            self.constr_def == other.constr_def and\
            self.applies == other.applies
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.constr_def, self.applies))

    def __repr__(self):
        return 'common_tag %s %s %s [%s %s]' % (self.name, self.constr_def,\
            self.applies, self.short_desc, self.long_desc)

class ConstraintType(Enum):
    Tag = 1,
    Validator = 2

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
        elif self.built_in == True\
         and self.constr_type == ConstraintType.Validator:
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
            # WARNING can't use __dict__ == __dict__ because
            # namespace is transient
            return self.built_in == other.built_in and self.tag == other.tag and self.constr_type == other.constr_type
        else:
            return False

    def __hash__(self):
        return hash((self.tag, self.built_in, self.constr_type))

    def __ne__(self, other):
        return not self.__eq__(other)

class Enumeration(NamedElement, NamespacedObject):


    def __init__(self, name = None, short_desc = None,\
        long_desc = None, namespace = None):
        super(Enumeration, self).__init__(name, short_desc, long_desc)
        self._namespace = namespace
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
        return hash((self.name, self.short_desc, self.long_desc,\
            fnvhash(self.literals) ))

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and\
            self.short_desc == other.short_desc and\
            self.long_desc == other.long_desc and\
            self.literals == other.literals
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        retStr = '\nenum %s (%s, %s) {' %\
          (self.name, self.short_desc, self.long_desc)
        for i in self.literals:
            retStr += ' %s\n' % (i)
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
            return self.value == other.value  and self.name == other.name\
                and self.short_desc == other.short_desc\
                and self.long_desc == other.short_desc
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.value, self.name, self.short_desc, self.long_desc))

    def __repr__(self):
        return ' %s - %s (%s, %s)' % (self.name, self.value, self.short_desc,\
            self.long_desc)

class ApplyDef(object):
    """
    Apply def signature. There can't be multiple applies on same
    type of parameter.  For example, you can't have an
    `applyTo _entity _entity` because applyTo definition
    only works on a type of object which is unique.
    """
    def __init__(self, to_entity = False, to_prop = False, to_param = False,\
        to_service = False, to_op = False, to_value_object = False):
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
        return hash((self.to_entity, self.to_prop, self.to_param,\
            self.to_service, self.to_op, self.to_value_object))

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
    AppliesTo constraint signature meta-model, that denotes what
    object can a constraint apply to. Some constrain are limited to only
    operations (_op) or entities (_entity).
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
        self.elems = dict()

    def set_name(self, name):
        self.name = name

    def add_elem(self, element):
        if element and element.name:
            self.elems[element.name] = element
        return self

    def add_constraint(self, constraint):
        assert type(constraint) is Constraint
        self.elems[constraint.tag.name] = constraint
        return self

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name \
             and self.short_desc == other.short_desc\
             and self.long_desc == other.long_desc\
             and self.elems == other.elems
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc,\
            fnvhash(self.elems.items()) ))

    def __repr__(self):
        retStr = '\n--------------\npackage %s {\n' % self.name
        for i in self.elems.itervalues():
            retStr += ' %s '% i
        retStr += "}\n--------------\n"
        return retStr

    def __getitem__(self, key):
        return self.elems[key]

class Relationship(object):
    """Describes all properties of a Relationship property"""
    def __init__(self, containment = False, opposite_end = None):
        super(Relationship, self).__init__()
        self.containment = containment
        self.opposite_end = opposite_end

    def __repr__(self):
        opposite_end = ""
        if self.opposite_end:
            opposite_end = "<> %s" % self.opposite_end
        return " Relationship:  %s (containment:%s)" % (opposite_end, self.containment)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.opposite_end == other.opposite_end\
                and self.containment == other.containment
        return False

    def __ne__(self, other):
        return not self.__ne__(other)

    def __hash__(self):
        return hash((self.containment, self.opposite_end))


class TypeDef(NamedElement):
    """
    Models the type signature of fields
    """
    def __init__(self, name = None, type_of = None, short_desc = None, long_desc = None):
        super(TypeDef, self).__init__(name, short_desc, long_desc)
        self.type = type_of
        self.container = False
        self.multi = None

    def set_multi(self, multi = None):
        if multi is None:
            self.container = False
            self.multi = None
        elif multi is not None and multi > 0:
            self.container = True
            self.multi = multi
        elif multi is not None and multi == 0:
            self.container = True
            self.multi = None

        return self

    def set_type(self, type_sign):
        self.type = type_sign
        return self

    def __eq__(self, other):
        if type(other) is type(self):
            return NamedElement.__eq__(self, other)\
                and self.type == other.type\
                and self.container == other.container\
                and self.multi == other.multi
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.type,\
            self.container, self.multi))

    def __repr__(self):
        retStr = " %s %s " % ( self.type, self.name)
        if self.container:
            retStr += "["
            if self.multi is not None:
                retStr += "%s" % (self.multi)
            retStr += "]"
        return retStr

class ConstraintSpec(object):
    """
    Constraint specification applies constraint to an bound entity
        ident is the identifier found in first pass of the parser
        parameters is a list of parameters supplied to the constraint
        bound is the definition of constraint which is bound to other (for equality it won't be considered)
    """
    def __init__(self, ident = None, parameters = None):
        super(ConstraintSpec, self).__init__()
        self.ident = ident
        self.parameters = []
        if parameters and type(parameters) is list:
            self.parameters = parameters
        self.bound = None

    # Returns whether the constraint spec matched by id
    # is compatible with property it is bound to
    # and the parameters provided
    def match_field(self, field):
        pass

    def add_param(self, param):
        self.parameters.append(param)
        return self

    def __eq__(self, other):
        if type(other) is type(self):
            return self.ident == other.ident\
            and self.parameters == other.parameters
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.ident, self.parameters.__repr__()))

    def __repr__(self):
        retStr = "  %s ( " % self.ident
        for val in self.parameters:
            retStr += " `%s` " % val
        retStr += " )"
        return retStr

class Property(object):
    """
    Models properties of entities and other DOMM Classifiers

    There is a set of attributes of a property (ordered, unique ...) which
    describes the Property. After it there is the type_def which is the property's type signature.
    Relationship field determines if the field is a relation and to what.
    Constraint fields are referenced constraints applied to this property.
    """
    def __init__(self, type_def = None, relation = None):
        self.ordered = False
        self.unique = False
        self.readonly = False
        self.required = False

        self.type_def = type_def
        self.relationship = relation
        self.constraints = set()

    def add_relationship(self, rel):
        self.relationship = rel
        return self

    def add_type_def(self, type_def):
        self.type_def = type_def
        return self

    def add_constraint_spec(self, constraint_spec):
        self.constraints.add(constraint_spec)
        return self

    def __hash__(self):
        return hash((self.ordered, self.unique, self.readonly,
            self.type_def, self.relationship, fnvhash(self.constraints)
            ))

    def __eq__(self, other):
        if type(other) is type(self):
            return self.ordered == other.ordered\
                and self.unique == other.unique\
                and self.readonly == other.readonly\
                and self.required == other.required\
                and self.type_def == other.type_def\
                and self.relationship == other.relationship\
                and self.constraints == other.constraints
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

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

        containment = ""
        if self.relationship:
            if self.relationship.containment:
                containment = "+"

        retStr += " %s  %s%s " %\
            (self.type_def.type, containment, self.type_def.name)
        if self.type_def.container:
            retStr += "["
            if self.type_def.multi is not None:
                retStr += "%s" % (self.type_def.multi)
            retStr += "]"

        if self.relationship:
            if self.relationship.opposite_end:
                retStr += " <> %s " % self.relationship.opposite_end._id

        retStr += print_constraints(self.constraints)

        retStr += ' "%s" "%s" ' %\
            (self.type_def.short_desc, self.type_def.long_desc)
        return retStr

class ExceptionType(NamedElement, NamespacedObject):
    """
    Exception object describing models
    """

    def __init__(self, name = None, short_desc = None, long_desc = None,\
        namespace = None):
        super(ExceptionType, self).__init__(name, short_desc, long_desc)
        self.props = dict()
        self._namespace = namespace
        self._check()


    def add_prop(self, prop):
        # In exception we can't for example have two same named fields
        #
        # exception FileNotFound {
        #    prop int errorCode
        #    prop char errorCode
        # }
        # Can't exist simultaneously
        if prop.type_def.name in self.props:
            raise DuplicatePropertyerror(prop.name)
        else:
            self.props[prop.type_def.name] = prop

        return self

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self, other)\
                and self.props == other.props
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc,\
            fnvhash(self.props.items())))

    def __repr__(self):
        retStr = ' exception %s "%s" "%s" {\n' %\
                (self.name, self.short_desc, self.long_desc)
        for prop in self.props.itervalues():
            retStr += "    %s\n" % prop
        return retStr

    def __getitem__(self, key):
        return self.props[key]

class ClassType(Enum):
    """
    Represents possible classifier type amongst the one of specified
    """
    Entity = 1,
    Service = 2,
    ValueObject = 3,
    ExceptType = 4,
    DataType = 5,
    Constraint = 6

class ClassifierBound(object):
    """
    Tracks a relation used to refer to other classifier.
    For example an Entity may depend on a service or extend another Entity.

    This class models said behavior
    """
    def __init__(self, ref = None, type_of = None):
        super(ClassifierBound, self).__init__()
        assert type(ref) is Id
        if type_of:
            assert type(type_of) is ClassType
        self.ref = ref
        self.type_of = type_of
        self.bound = None

    def __repr__(self):
        return "%s (of type %s)" % (self.ref._id, self.type_of)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.ref == other.ref and self.type_of == other.type_of
        return False

    def __ne__(self, other):
        return not self.__init__(other)

    def __hash__(self):
        return hash((self.ref, self.type_of))

class OpParam(NamedElement):
    """docstring for OpParam"""
    def __init__(self, type_def = None, short_desc = None, long_desc = None):
        super(OpParam, self).__init__()
        self.ordered = False
        self.unique = False
        self.required = False
        self.name = None

        self.short_desc = short_desc
        self.long_desc = long_desc

        self.type_def = type_def
        self.constraints = set()

    def __repr__(self):
        retStr = ""
        if self.ordered:
            retStr += " ordered "
        if self.unique:
            retStr += " unique "
        if self.required:
            retStr += " required "
        if self.constraints:
            retStr += " constraints(%s)" % self.constraints
        retStr += " %s (%s %s) " % (self.type_def, self.short_desc,\
            self.long_desc)
        return retStr

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self, other)\
            and self.ordered == other.ordered\
            and self.unique == other.unique\
            and self.required == other.required\
            and self.type_def == other.type_def\
            and self.constraints == other.constraints

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc,
            self.type_def, self.unique, self.required, self.ordered,
            fnvhash(self.constraints)))

class Operation(NamedElement):
    """
    This class models the Operation classifier in DOMMLite.

    It represents a method that is often used in various DOMMLite objects
    like ValueObject, Entity or Services. It has name, short and long description
    and has list of parameters it requires.


    Example:
        service ExampleService {
            ...
            unique op string getName()
            ...
        }
    """
    def __init__(self, short_desc = None, long_desc = None,\
        type_def = None, params = None):
        super(Operation, self).__init__()
        self.name = None
        self.short_desc = short_desc
        self.long_desc = long_desc

        self.ordered = False
        self.unique = False
        self.required = False

        self.type_def = type_def

        self.params = []

        if params:
            assert type(params) is list
            self.params = params

        self.throws = []
        self.constraints = set()

    def add_param(self, param):
        assert type(param) is OpParam
        self.params.append(param)
        return self

    def add_constraint_spec(self, constraint):
        assert type(constraint) is ConstraintSpec
        self.constraints.add(constraint)
        return self

    def add_throws_exception(self, exception):
        assert type(exception) is ClassifierBound
        assert exception.type_of == ClassType.ExceptType
        self.throws.append(exception)
        return self

    def __eq__(self, other):
        return NamedElement.__eq__(self,other)\
            and self.ordered == other.ordered and self.unique == other.unique\
            and self.required == other.required\
            and self.constraints == other.constraints\
            and self.type_def == other.type_def\
            and self.params == other.params and self.throws == other.throws\

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.ordered,\
            self.unique, self.required, self.type_def, fnvhash(self.params),\
            fnvhash(self.constraints), fnvhash(self.throws)))

    def __repr__(self):
        retStr = " op "
        if self.ordered:
            retStr += " ordered "
        if self.unique:
            retStr += " unique "
        if self.required:
            retStr += " required "
        retStr += '%s(' % self.type_def
        if self.params:
            for x in self.params:
                retStr += " %s " % x
        retStr += ") "
        if self.throws:
            retStr += " throws "
            for x in self.throws:
                retStr += " %s " % x.ref._id
        retStr += print_constraints(self.constraints)
        retStr += " (%s %s) " % (self.short_desc, self.long_desc)
        return retStr

class Compartment(NamedElement):
    """
    Class that denotes a named group of either operations or properties.
    Generally used to respresent things like logical/visual grouping of
    elements, for example tabs.
    """
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        is_op = True):
        super(Compartment, self).__init__(name, short_desc, long_desc)
        self.elements = set()
        self.is_op = is_op

    def add_elem(self, elem):
        if self.is_op:
            assert type(elem) is Operation
        else:
            assert type(elem) is Property
        self.elements.add(elem)
        return self

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self, other)\
            and self.elements == other.elements
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc,\
                    fnvhash(self.elements)))

    def __repr__(self):
        retStr = "comparement %s (%s %s) {\n" %\
            (self.name, self.short_desc, self.long_desc)
        if self.elements:
            for x in self.elements:
                retStr += '%s\n' % x
        retStr += "}"
        return retStr

class Service(NamedElement, NamespacedObject):
    """
    Service classifier meta-model.
    """
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        extends = None, depends = None, namespace = None):
        super(Service, self).__init__(name, short_desc, long_desc)
        self.extends = extends
        self.dependencies = []
        if depends and type(depends) is list:
            self.dependencies = depends
        self.constraints = set()
        self.operations = set()
        self.op_compartments = set()
        self._namespace = namespace
        self._check()

    def set_extends(self, extends):
        assert type(extends) is ClassifierBound
        self.extends = extends
        self.extends.type_of = ClassType.Service
        return self

    def set_dependencies(self, deps):
        assert type(deps) is list
        for val in deps:
            val.type_of = ClassType.Service
            self.dependencies.append(val)
        return self

    def add_constraint_spec(self, constr):
        assert type(constr) is ConstraintSpec
        self.constraints.add(constr)
        return self

    def add_operation(self, oper):
        assert type(oper) is Operation
        self.operations.add(oper)
        return self

    def add_op_compartment(self, compartment):
        self.op_compartments.add(compartment)
        return self

    def __repr__(self):
        retStr = " service %s (%s %s)" %\
            (self.name, self.short_desc, self.long_desc)

        if self.extends:
             retStr += " extends %s " % self.extends

        if self.dependencies and len(self.dependencies) > 0:
            retStr += " depends "
            for val in self.dependencies:
                retStr += " %s " % val

        retStr += "{\n"

        if self.constraints and len(self.constraints) > 0:
            retStr += print_constraints(self.constraints)

        if self.op_compartments:
            for compartment in self.op_compartments:
                retStr += "\n%s\n" % compartment


        for op in self.operations:
            retStr += "    %s" % op
        retStr += "}"

        return retStr

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self, other)\
            and self.extends == other.extends\
            and self.dependencies == other.dependencies\
            and self.constraints == other.constraints\
            and self.operations == other.operations\
            and self.op_compartments == other.op_compartments
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.extends,
            fnvhash(self.dependencies), fnvhash(self.constraints),
            fnvhash(self.operations), fnvhash(self.op_compartments)))

class ValueObject(NamedElement, NamespacedObject):
    """
    """
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        extends = None, depends = None, namespace = None):
        super(ValueObject, self).__init__(name, short_desc, long_desc)
        self.extends = None
        self.dependencies = []

        if self.extends:
            self.set_extends(extends)
        if self.depends and len(self.depends) > 0:
            self.set_dependencies(depends)

        self.constraints = set()
        self.props = set()
        self._namespace = namespace
        self._check()

    def set_extends(self, extends):
        assert type(extends) is ClassifierBound
        self.extends = extends
        self.extends.type_of = ClassType.ValueObject
        return self

    def set_dependencies(self, deps):
        assert type(deps) is list
        for val in deps:
            val.type_of = ClassType.Entity
            self.dependencies.append(val)
        return self

    def add_constraint_spec(self, constr):
        assert type(constr) is ConstraintSpec
        self.constraints.add(constr)
        return self

    def add_prop(self, prop):
        assert type(prop) is Property
        self.props.add(prop)
        return self

    def __repr__(self):
        retStr = " ValueObject %s (%s %s)" %\
            (self.name, self.short_desc, self.long_desc)

        if self.extends:
             retStr += " extends %s " % self.extends

        if self.dependencies and len(self.dependencies) > 0:
            retStr += " depends "
            for val in self.dependencies:
                retStr += " %s " % val

        retStr += "{\n"

        if self.constraints and len(self.constraints) > 0:
            retStr += print_constraints(self.constraints)


        for op in self.props:
            retStr += "    %s" % op
        retStr += "}"

        return retStr

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self, other)\
            and self.extends == other.extends\
            and self.dependencies == other.dependencies\
            and self.constraints == other.constraints\
            and self.props == other.props
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.extends,
            fnvhash(self.dependencies), fnvhash(self.constraints),
            fnvhash(self.props)))

class Key(object):
    """Models a key of the entity metamodel"""
    def __init__(self):
        super(Key, self).__init__()
        self.props = set()

    def add_prop(self, prop):
        assert type(prop) is Property
        self.props.add(prop)
        return self

    def __eq__(self, other):
        if type(self) is type(other):
            return self.props == other.props
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return fnvhash(self.props)

    def __repr__(self):
        retStr += "key {\n"
        for x in self.props:
            retStr += "    %s\n" % x
        retStr += "}"
        return retStr

class Repr(object):
    """Models textual represnetation of the entity metamodel"""
    def __init__(self):
        super(Repr, self).__init__()
        self.parts = []

    def add_elem(self, elem):
        self.parts.append(elem)
        return self

    def __eq__(self, other):
        if type(self) is type(other):
            return self.parts == other.parts
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return fnvhash(self.parts)

    def __repr__(self):
        retStr += "repr "
        for x in self.parts:
            retStr += "    %s" % x
        retStr += "}"
        return retStr

class Entity(NamedElement, NamespacedObject):
    """
    Models the entity of a DOMMLite metamodel. Entity is a data structure
    with it's corresponding fields, relationships and methods.
    """
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        extends = None, depends = None, namespace = None):
        super(Entity, self).__init__(name, short_desc, long_desc)
        self.extends = None
        self.dependencies = []
        self.elems = dict()
        self.key = None
        self.repr = None

        if self.extends:
            self.set_extends(extends)
        if self.depends and len(self.depends) > 0:
            self.set_dependencies(depends)

        self.constraints = set()
        self.props = set()
        self.opers = set()
        self.op_compartments = dict()
        self.prop_compartments = dict()
        self._namespace = namespace
        self._check()

    def set_extends(self, extends):
        assert type(extends) is ClassifierBound
        self.extends = extends
        self.extends.type_of = ClassType.Entity
        return self

    def set_dependencies(self, deps):
        assert type(deps) is list
        for val in deps:
            val.type_of = ClassType.Service
            self.dependencies.append(val)
        return self

    def add_constraint_spec(self, constr):
        assert type(constr) is ConstraintSpec
        self.constraints.add(constr)
        return self

    def add_operation(self, oper):
        assert type(oper) is Operation
        self.elems[oper.name] = oper
        return self

    def add_prop(self, prop):
        assert type(prop) is Property
        self.elems[prop.name] = prop
        return self

    def add_comparment(self, compartment):
        assert type(compartment) is Compartment
        if compartment.is_op:
            self.op_compartments.add(compartment.name)
            for op in compartment:
                self.add_operation(op)
        else:
            self.prop_compartments.add(compartment.name)
            for prop in compartment:
                self.add_prop(prop)
        return self

    def __repr__(self):
        retStr = " Entity %s (%s %s)" %\
            (self.name, self.short_desc, self.long_desc)

        if self.extends:
             retStr += " extends %s " % self.extends

        if self.dependencies and len(self.dependencies) > 0:
            retStr += " depends "
            for val in self.dependencies:
                retStr += " %s " % val

        retStr += "{\n"

        if self.constraints and len(self.constraints) > 0:
            retStr += print_constraints(self.constraints)


        for op in self.elems:
            retStr += "    %s" % op
        retStr += "}"

        return retStr

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self,other) \
            and self.elems == other.elems and self.extends == other.extenn ds\
            and self.dependencies == other.dependencies\
            and self.constraints == other.constraints
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.extends,
            fnvhash(dependencies), fnvhash(self.constraints),
            fnvhash(elems.items())))
