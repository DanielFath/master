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
    Copied from this site:
    http://www.gossamer-threads.com/lists/python/python/679002#679002
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
                retStr += " %s " % c.ident._id
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

def type_to_name(element):
    if type(element) is Entity:
        return "entity"
    elif type(element) is Service:
        return "service"
    elif type(element) is ValueObject:
        return "value object"
    elif type(element) is ExceptionType:
        return "exception"
    elif type(element) is DataType:
        return "data type"
    elif type(element) is Constraint:
        return "constraint"
    elif type(element) is Package:
        return "package"
    else:
        return ""

class NamedElement(object):
    """
    Named element represents short and long description
    that is encountered across various DOMMLite constructs
    """
    def __init__(self, name = None, short_desc = None, long_desc = None):
        super(NamedElement, self).__init__()
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc

    def set_descs(self, named_el):
        assert type(named_el) is NamedElement
        assert named_el is not None
        self.short_desc = named_el.short_desc
        self.long_desc = named_el.long_desc

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name\
                and self.short_desc == other.short_desc\
                and self.long_desc == other.long_desc
        return False

    def __repr__(self):
        """
        Pretty print named element out
        """
        return 'Named element { short_desc = "%s" long_desc  = "%s" }' %\
        (self.short_desc, self.long_desc)

class Id(object):
    """
    Id that represents a name of a type or a parameter
    """
    def __init__(self, ident):
        super(Id, self).__init__()
        self._id = ident;

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
        assert type(path) is list or type(path) is str
        self.path = []
        if type(path) is list:
            if path and len(path) > 0:
                self.path = path
        elif type(path) is str:
            self.path = path.split(".")

    @property
    def _canon(self):
        retval = ""
        for i, part in enumerate(self.path):
            if i > 0:
                retval += "."
            retval += part
        return retval

    @property
    def _id(self):
        if self.path and len(self.path) > 0:
            return self.path[-1]
        else:
            return None

    def depth(self):
        return len(self.path)

    def is_resolved():
        return len(self.path) > 1

    def add_outer_level(self, outer):
        assert type(outer) is str
        self.path.insert(0, outer)
        return self

    def __eq__(self, other):
        if type(self) is type(other):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return fnvhash(self.path)

    def __repr__(self):
        retval = "Qid("
        for i, part in enumerate(self.path):
            if i > 0:
                retval += "."
            retval += part
        retval += ")"
        return retval

class Model(NamedElement):
    """
    This class represents the meta model for DOMMLite model
    object. DOMMLite model is a container for other objects.
    """
    def __init__(self, name =None, short_desc = None, long_desc = None):
        super(Model, self).__init__(name, short_desc, long_desc)
        self.qual_elems = dict()
        self.unique = dict()

    def _flatten_package(self, pack):
        for qid, elem in pack.elems.iteritems():
            if type(elem) is not Package:
                if type(qid) is Qid:
                    self.add_elem(elem, qid._canon, qid._id,\
                        type_to_name(elem))
                elif type(qid) is str:
                    self.add_elem(elem, qid, qid, type_to_name(elem))
        for qid, elem in pack._imported.iteritems():
            if type(elem) is not Package:
                if type(qid) is Qid:
                    self.add_elem(elem, qid._canon, qid._id,\
                        type_to_name(elem))
                elif type(qid) is str:
                    self.add_elem(elem, qid, qid, type_to_name(elem))

    def add_elem(self, ref, qid, name, type_of):
        if ref and qid:
            if not qid in self.qual_elems:
                self.qual_elems[qid] = ref
                if name in self.unique:
                    self.unique[name] = False
                else:
                    self.unique[name] = qid
            else:
                raise DuplicateTypeError(type_of, name)

    def get_qid(self, name_or_qid):
        retval = ""
        if type(name_or_qid) is str \
            or (type(name_or_qid) is Qid and not name_or_qid.is_resolved):
            retval = name_or_qid
            if name_or_qid in self.unique:
                if self.unique[name_or_qid] != False:
                    retval = self.unique[name_or_qid]
        elif type(name_or_qid) is Qid:
            retval = name_or_qid._canon
        return retval

    def get_elem_by_crosref(self, cross_ref):
        assert type(cross_ref) is CrossRef
        elem = None
        qid = self.get_qid(cross_ref.ref._canon)
        if qid in self.qual_elems:
            elem = self.qual_elems[qid]
            if type(elem) is not cross_ref.ref_type.into_type():
                raise TypeNotFoundError(qid)
        else:
            raise TypeNotFoundError(qid)
        cross_ref._bound = elem
        return elem

    def add_type(self, type_def):
        assert type(type_def) is DataType
        self.add_elem(type_def, type_def.name, type_def.name, "dataType")
        return self

    def add_package(self, package):
        assert type(package) is Package
        package._update_parent_model(self)
        self.add_elem(package, package.name, package.name, "package")
        self._flatten_package(package)
        return self

    def add_constraint(self, constr):
        assert type(constr) is Constraint
        self.add_elem(constr, constr.name, constr.name, "constraint")
        return self


    def __repr__(self):
        return 'Model "%s" (%s %s)\nall: %s\n' %\
        (self.name, self.short_desc, self.long_desc, self.qual_elems)

    def __eq__(self, other):
        if type(other) is type(self):
            return NamedElement.__eq__(self, other)\
                and self.qual_elems == other.qual_elems
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc,\
        fnvhash(self.qual_elems.items())))

    def __getitem__(self, key):
        return self.qual_elems[key]

class DataType(NamedElement):


    def __init__(self, name = None, short_desc = None, long_desc = None,\
        built_in = False):
        super(DataType, self).__init__(name, short_desc, long_desc)
        self.built_in = built_in

    def _update_parent_model(self, model):
        pass

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
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        constr_def = None, applies = None):
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

def constr_to_type(constr_param):
    param_type = None
    if constr_param == "_int":
        param_type = int
    elif constr_param == "_string":
        param_type = str
    elif constr_param == "_ref":
        param_type = CrossRef
    return param_type

class Constraint(object):
    """
    A unified container for tagTypes and validators,
    both built-in and user defined.
    """

    def __init__(self, tag = None, built_in = False, constr_type = None):
        super(Constraint, self).__init__()
        self.tag = tag
        self.built_in = built_in
        self.constr_type = constr_type

    def _update_parent_model(self, model):
        pass

    # Returns whether the constraint spec matched by id
    # is compatible with property it is bound to
    # and the parameters provided
    def check_applies(self, field, field_name):
        if self.tag:
            if not self.tag.applies.check_applies(field):
                raise ConstraintDoesntApplyError(self.tag.name, field_name)

    def check_params(self, constr):
        if self.tag:
            # FIXME remove these
            print("self.tag.constr_def", self.tag.constr_def)
            print("constr.parameters", constr.parameters)
            # Check is constraint definition doesn't have any parameter
            if self.tag.constr_def is None:
                if len(constr.parameters) > 0:
                    raise NoParameterError(self.tag.name)
            elif self.tag.constr_def is not None \
                and len(self.tag.constr_def.constraints) == 0:
                if len(constr.parameters) > 0:
                    raise NoParameterError(self.tag.name)
            # Check if constraint definition has elipsis
            elif self.tag.constr_def is not None\
                    and len(self.tag.constr_def.constraints) == 1\
                    and self.tag.constr_def.constraints[0] == "..." :
                return True
            elif self.tag.constr_def is not None\
                    and len(self.tag.constr_def.constraints) == 2\
                    and self.tag.constr_def.constraints[1] == "...":
                param_type = constr_to_type(self.tag.constr_def.constraints[0])
                for param in constr.parameters:
                    if type(param) is not param_type:
                        raise WrongConstraintError(self.tag.name, param)
                return True
            elif self.tag.constr_def is not None\
                    and len(self.tag.constr_def.constraints) !=\
                    len(constr.parameters):
                expected = len(self.tag.constr_def.constraints)
                found = len(constr.parameters)
                raise WrongNumberOfParameterError(self.tag.name, expected,\
                    found)
            elif self.tag.constr_def is not None\
                    and len(self.tag.constr_def.constraints) ==\
                    len(constr.parameters):
                for pos, param in enumerate(constr.parameters):
                    constr_def = self.tag.constr_def.constraints[pos]
                    param_type = constr_to_type(constr_def)
                    if type(param) is not param_type:
                        raise WrongConstraintAtPosError(self.tag.name, param,\
                            pos)
                return True

    @property
    def name(self):
        retval = None
        if self.tag and self.tag.name:
            retval = self.tag.name
        return retval

    def __repr__(self):
        retStr = '\n'
        if self.built_in == True and self.constr_type == ConstraintType.Tag:
            retStr += 'buildinTagType'
        elif self.built_in == False and self.constr_type == ConstraintType.Tag:
            retStr += 'tagType'
        elif self.built_in == True\
          and self.constr_type == ConstraintType.Validator:
            retStr += 'buildinValidator'
        elif self.built_in == False \
          and self.constr_type == ConstraintType.Validator:
            retStr += 'validatorType'

        if self.tag is not None:
            retStr += ' %s ' % self.name
            if self.tag.constr_def is not None:
                retStr += ' %s ' % self.tag.constr_def
            if self.tag.applies is not None:
                retStr += ' %s ' % self.tag.applies
            retStr += ' "%s" "%s"' % (self.tag.short_desc, self.tag.long_desc)

        return retStr

    def __eq__(self, other):
        if type(other) is type(self):
            return self.built_in == other.built_in and self.tag == other.tag\
                and self.constr_type == other.constr_type
        else:
            return False

    def __hash__(self):
        return hash((self.tag, self.built_in, self.constr_type))

    def __ne__(self, other):
        return not self.__eq__(other)

class Enumeration(NamedElement):


    def __init__(self, name = None, short_desc = None,long_desc = None) :
        super(Enumeration, self).__init__(name, short_desc, long_desc)
        self.literals = set()

    def add_all_literals(self, list_literals):
        assert type(list_literals) is list
        for i in list_literals:
            self.add_literal(i)

        return self

    def _update_parent_model(self, model):
        pass

    def add_literal(self, literal):
        if literal in self.literals:
            raise DuplicateLiteralError(literal.value)
        else:
            literals_value = (x.value for x in self.literals)
            if literal.value in literals_value:
                raise DuplicateLiteralError(literal.value)
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

    def check_applies(self, field):
        retval = False
        if type(field) is Entity:
            retval = self.to_entity
        elif type(field) is Property:
            retval = self.to_prop
        elif type(field) is OpParam:
            retval = self.to_param
        elif type(field) is Service:
            retval = self.to_service
        elif type(field) is Operation:
            retval = self.to_op
        elif type(field) is ValueObject:
            retval = self.to_value_object
        return retval

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

    def check_params(self, constr):
        size = len(self.constraints)
        #if size == 0 and constr.

    def add_constr(self, constr):
        if "..." in self.constraints:
            raise ElipsisMustBeLast()
        else:
            self.constraints.append(constr)
        return self

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
        self._parent_model = None
        self.elems = dict()
        self._imported = dict()

    def _checked_add(self, add_map, qid, element):
        if qid in add_map:
            raise DuplicateTypeError(type_to_name(element), qid._id)
        add_map[qid] = element

    def _flatten_ns(self, prefix):
        flatten = dict()
        for qid, elem in self.elems.iteritems():
            flatten[qid.add_outer_level(prefix)] = elem
        for imp_qid, import_val in self._imported.iteritems():
            flatten[imp_qid.add_outer_level(prefix)] = import_val
        return flatten

    def _update_parent_model(self, model):
        self._parent_model = model
        for elem in self.elems.itervalues():
            elem._update_parent_model(model)

    def set_name(self, name):
        self.name = name

    def add_elem(self, element):
        if element and element.name:
            qid = Qid(element.name).add_outer_level(self.name)
            self._checked_add(self.elems, qid, element)
            try:
                flattened = element._flatten_ns(self.name)
                for qid, element in flattened.iteritems():
                    self._imported[qid] = element
            except AttributeError:
                # We just attempt to read a method or nothing happens
                pass
        return self

    def add_constraint(self, constraint):
        assert type(constraint) is Constraint
        self.elems[constraint.name] = constraint
        return self

    def __eq__(self, other):
        if type(self) is type(other):
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
        retval = None
        for i in self.elems:
            if i._id == key or i._canon == key:
                retval = self.elems[i]
        return retval

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
        return " Relationship:  %s (containment:%s)" % \
            (opposite_end, self.containment)

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
    def __init__(self, name = None, type_of = None, short_desc = None,\
        long_desc = None):
        super(TypeDef, self).__init__(name, short_desc, long_desc)
        self.type = type_of
        self.container = False
        self.multi = None
        self._bound = None

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
        bound is the definition of constraint which is bound to other
        (for equality it won't be considered)
    """
    def __init__(self, ident = None, parameters = None):
        super(ConstraintSpec, self).__init__()
        self.ident = ident
        self.parameters = []
        if parameters and type(parameters) is list:
            for param in parameters:
                self.add_param(param)
        self._bound = None

    def _update_parent_model(self, model):
        pass#self._parent_model = model

    def _replace_qids(self, model):
        refs = (x for x in self.parameters if type(x) is CrossRef)
        for cref in refs:
            qual_id = model.unique[cref.ref._canon]

            if qual_id is None:
                raise TypeNotFoundError(cref.ref._canon)
            else:
                elem  = model.qual_elems[qual_id]
                cref.ref = qual_id
                cref._bound = elem

    def add_param(self, param):
        if type(param) is Id:
            qid = Qid(param._id)
            cross_ref = CrossRef(ref = qid)
            self.parameters.append(cross_ref)
        else:
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
    describes the Property. After it there is the type_def which is the
    property's type signature.
    Relationship field determines if the field is a relation and to what.
    Constraint fields are referenced constraints applied to this property.
    """
    def __init__(self, type_def = None, relation = None):
        self._parent_model = None

        self.ordered = False
        self.unique = False
        self.readonly = False
        self.required = False

        self.type_def = type_def
        self.relationship = relation
        self.constraints = set()

    def _update_parent_model(self, model):
        self._parent_model = model

    @property
    def name(self):
        if self.type_def and self.type_def.name:
            return self.type_def.name
        else:
            return None

    def add_relationship(self, rel):
        self.relationship = rel
        return self

    def add_type_def(self, type_def):
        self.type_def = type_def
        return self

    def add_constraint_spec(self, constraint_spec):
        assert type(constraint_spec) is ConstraintSpec
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

class ExceptionType(NamedElement):
    """
    Exception object describing models
    """

    def __init__(self, name = None, short_desc = None, long_desc = None):
        super(ExceptionType, self).__init__(name, short_desc, long_desc)
        self._parent_model = None
        self.props = dict()

    def _update_parent_model(self, model):
        self._parent_model = model
        for prop in self.props.itervalues():
            prop._update_parent_model(model)

    def _flatten_ns(self, prefix):
        retval = dict()
        for name, val in self.props.iteritems():
            namespace = "%s.%s.%s" % (prefix, self.name, name)
            retval[Qid(namespace)] = val
        return retval

    def add_prop(self, prop):
        # In exception we can't for example have two same named fields
        #
        # exception FileNotFound {
        #    prop int errorCode
        #    prop char errorCode
        # }
        # Can't exist simultaneously
        if prop.type_def.name in self.props:
            raise DuplicatePropertyError(prop.name)
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

class Ref(Enum):
    """
    Represents possible classifier type amongst the one of specified
    """
    Entity = 1,
    Service = 2,
    ValueObject = 3,
    ExceptType = 4,
    DataType = 5,
    Constraint = 6,
    Property = 7

    def into_type(self):
        if self == Ref.Entity:
            return Entity
        elif self == Ref.Service:
            return Service
        elif self == Ref.ValueObject:
            return ValueObject
        elif self == Ref.ExceptType:
            return ExceptionType
        elif self == Ref.DataType:
            return DataType
        elif self == Ref.Constraint:
            return Constraint
        elif self == Ref.Property:
            return Property

class CrossRef(object):
    """
    Tracks a relation used to refer to other classifier.
    For example an Entity may depend on a service or extend another Entity.

    This class models said behavior
    """
    def __init__(self, ref = None, ref_type = None):
        super(CrossRef, self).__init__()
        assert type(ref) is Qid
        if ref_type:
            assert type(ref_type) is Ref
        self.ref = ref
        self.ref_type = ref_type
        self._bound = None

    def _update_parent_model(self, model):
        self._parent_model = model

    def __repr__(self):
        return "%s (of type %s)" % (self.ref._id, self.ref_type)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.ref == other.ref and self.ref_type == other.ref_type
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.ref, self.ref_type))

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
    like ValueObject, Entity or Services. It has name, short and long
    description and has list of parameters it requires.

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
        self._parent_model = None
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

    def _update_parent_model(self, model):
        self._parent_model = model
        #for param in self.params:
        #    param._update_parent_model(model)


    @property
    def op_name(self):
        if self.type_def and self.type_def.name:
            return self.type_def.name
        else:
            return None

    def _check_throws(self, exception):
        if exception in self.throws:
            raise DuplicateExceptionError(self.op_name, exception.ref._canon)

    def add_param(self, param):
        assert type(param) is OpParam
        for p in self.params:
            if param.name == p.name:
                raise DuplicateParamError(p.name)
        self.params.append(param)
        return self

    def add_constraint_spec(self, constraint):
        assert type(constraint) is ConstraintSpec
        self.constraints.add(constraint)
        return self

    def add_throws_exception(self, exception):
        assert type(exception) is CrossRef
        assert exception.ref_type == Ref.ExceptType
        self._check_throws(exception)
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

    Args:
        name(str):  name of compartment
        short_desc(str): Short description of the compartment
        long_desc(str): Long description of the compartment
        is_op(bool): Compartemnts can be operation compartments,  if this
            parameter is True, or feature compartment if argument is False.
            Operation compartment which only store operations or feature that
            store operations or properties
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
            assert type(elem) is Operation or type(elem) is Property
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

    def __getitem__(self, key):
        retval = None
        for val in self.elements:
            if key == val.name:
                retval = val
                break
        return retval

class Service(NamedElement):
    """
    Service classifier meta-model.
    """
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        extends = None, depends = None):
        super(Service, self).__init__(name, short_desc, long_desc)
        self._parent_model = None
        self.extends = extends
        self.dependencies = []
        if depends and type(depends) is list:
            self.dependencies = depends
        self.constraints = set()
        self.elems = dict()
        self.operations = set()
        self.op_compartments = dict()

    def _flatten_ns(self, prefix):
        retval = dict()
        for name, val in self.elems.iteritems():
            namespace = "%s.%s.%s" % (prefix, self.name, name)
            retval[Qid(namespace)] = val
        return retval

    def _check_op(self, oper):
        if oper.op_name in self.elems:
            raise DuplicateTypeError("operation", oper.op_name)

    def _update_parent_model(self, model):
        self._parent_model = model
        for elem in self.elems.itervalues():
            elem._update_parent_model(model)

    def set_extends(self, extends):
        assert type(extends) is CrossRef
        self.extends = extends
        self.extends.ref_type = Ref.Service
        return self

    def set_dependencies(self, deps):
        assert type(deps) is list
        for cross_ref in deps:
            cross_ref.ref_type = Ref.Service
            self.dependencies.append(cross_ref)
        return self

    def add_constraint_spec(self, constr):
        assert type(constr) is ConstraintSpec
        self.constraints.add(constr)
        return self

    def add_operation(self, oper, is_compartment = False):
        assert type(oper) is Operation
        self._check_op(oper)
        self.elems[oper.op_name] = oper
        if not is_compartment:
            self.operations.add(oper.op_name)
        return self

    def add_op_compartment(self, compartment):
        self.op_compartments[compartment.name] = compartment
        for op in compartment.elements:
            self.add_operation(op, True)
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

        retStr += print_partial_map(self.elems, self.operations)

        if self.op_compartments:
            for compartment in self.op_compartments.values():
                retStr += "\n%s\n" % compartment

        retStr += "}"

        return retStr

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self, other)\
            and self.extends == other.extends\
            and self.dependencies == other.dependencies\
            and self.constraints == other.constraints\
            and self.elems == other.elems
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.extends,
            fnvhash(self.dependencies), fnvhash(self.constraints),
            fnvhash(self.elems.items())))

    def __getitem__(self, key):
        if key in self.op_compartments:
            return self.op_compartments[key]
        else:
            return self.elems[key]

class ValueObject(NamedElement):
    """
    """
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        extends = None, depends = None):
        super(ValueObject, self).__init__(name, short_desc, long_desc)
        self._parent_model = None
        self.extends = extends
        self.dependencies = []
        if depends and type(depends) is list:
            self.dependencies = depends
        self.constraints = set()
        self.props = dict()

    def _flatten_ns(self, prefix):
        retval = dict()
        for name, val in self.props.iteritems():
            namespace = "%s.%s.%s" % (prefix, self.name, name)
            retval[Qid(namespace)] = val
        return retval

    def _check_prop(self, element):
        if element.name in self.props:
            raise DuplicatePropertyError(element.name)

    def _update_parent_model(self, model):
        self._parent_model = model
        for prop in self.props.itervalues():
            prop._update_parent_model(model)

    def set_extends(self, extends):
        assert type(extends) is CrossRef
        self.extends = extends
        self.extends.ref_type = Ref.ValueObject
        return self

    def set_dependencies(self, deps):
        assert type(deps) is list
        for depend in deps:
            depend.ref_type = Ref.Entity
            self.dependencies.append(depend)
        return self

    def add_constraint_spec(self, constr):
        assert type(constr) is ConstraintSpec
        self.constraints.add(constr)
        return self

    def add_prop(self, prop):
        assert type(prop) is Property
        self._check_prop(prop)
        self.props[prop.type_def.name] = prop
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
            fnvhash(self.props.items())))

    def __getitem__(self, key):
        return self.props[key]

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
        retStr = "key {\n"
        for x in self.props:
            retStr += "    %s\n" % x
        retStr += "}"
        return retStr

class Repr(object):
    """Models textual representation of the entity metamodel"""
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
        retStr = "repr "
        for i,x in enumerate(self.parts):
            if i > 0 :
                retStr += "+"
            if type(x) is str:
                retStr += " `%s` " % x
            elif type(x) is CrossRef:
                retStr += " %s " % x
        return retStr

class Entity(NamedElement):
    """
    Models the entity of a DOMMLite metamodel. Entity is a data structure
    with it's corresponding fields, relationships and methods.
    """
    def __init__(self, name = None, short_desc = None, long_desc = None,\
        extends = None, depends = None):
        super(Entity, self).__init__(name, short_desc, long_desc)
        self._parent_model = None
        self.extends = None
        self.dependencies = []
        self.elems = dict()
        self.repr = None

        if self.extends:
            self.set_extends(extends)
        if self.dependencies and len(self.dependencies) > 0:
            self.set_dependencies(depends)

        self.constraints = set()
        self.features = set()
        self.key = set()
        self.compartments = dict()

    def _update_parent_model(self, model):
        self._parent_model = model
        for elem in self.elems.itervalues():
            elem._update_parent_model(model)

    def _flatten_ns(self, prefix):
        retval = dict()
        for key, val in self.elems.iteritems():
            namespace = "%s.%s.%s" % (prefix, self.name, key)
            retval[Qid(namespace)] = val
        return retval

    def set_key(self, key):
        assert type(key) is Key
        if key and key.props:
            for prop in key.props:
                self.add_feature(prop, True)
                self.key.add(prop.name)
        return self

    def set_repr(self, arg):
        assert type(arg) is Repr
        self.repr = arg
        return self

    def set_extends(self, extends):
        assert type(extends) is CrossRef
        self.extends = extends
        self.extends.ref_type = Ref.Entity
        return self

    def set_dependencies(self, deps):
        assert type(deps) is list
        for val in deps:
            val.ref_type = Ref.Service
            self.dependencies.append(val)
        return self

    def add_constraint_spec(self, constr):
        assert type(constr) is ConstraintSpec
        self.constraints.add(constr)
        return self

    def add_feature(self, feat, is_compartment = False):
        assert type(feat) is Operation or type(feat) is Property
        if feat.type_def.name in self.elems:
            raise DuplicateFeatureError(feat.type_def.name)
        if not is_compartment:
            self.features.add(feat)
        self.elems[feat.type_def.name] = feat
        return self

    def add_comparment(self, compartment):
        assert type(compartment) is Compartment
        if compartment.elems:
            self.compartments[self.compartment.name] = compartment
            for op in compartment.elems:
                self.add_feature(op, True)
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

        if self.key:
            retStr += print_partial_map(self.elems,self.key)

        if self.repr:
            retStr += "\n    {}\n".format(self.repr)

        if self.constraints and len(self.constraints) > 0:
            retStr += "    {}\n".format(print_constraints(self.constraints))

        for op in self.elems.values():
            retStr += "    {}\n".format(op)
        retStr += "}"

        return retStr

    def __eq__(self, other):
        if type(self) is type(other):
            return NamedElement.__eq__(self,other) \
            and self.elems == other.elems and self.extends == other.extends\
            and self.dependencies == other.dependencies\
            and self.repr == other.repr\
            and self.constraints == other.constraints
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.short_desc, self.long_desc, self.extends,
            fnvhash(self.dependencies), fnvhash(self.constraints),
            fnvhash(self.elems.items()), self.repr))

    def __getitem__(self, key):
        if key in self.compartments:
            return self.compartments[key]
        else:
            return self.elems[key]
