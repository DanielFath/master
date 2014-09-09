##############################################################################
# Name: actions.py
# Purpose: Actions used by DOMMLite parser
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
from arpeggio import SemanticAction
from metamodel import *


class ModelAction(SemanticAction):
    """
    Represents semantic action Model in DOMMLite
    """
    def first_pass(self, parser, node, children):
        # ID should been always present
        model = Model()

        for ind, val in enumerate(children):
            if type(val) is Id:
                model.name = val._id
            elif type(val) is NamedElement:
                model.set_descs(val)
            elif type(val) is DataType or type(val) is Enumeration:
                model.add_type(val)
            elif type(val) is Constraint:
                model.add_constraint(val)
            elif type(val) is Package:
                model.add_package(val)

        if parser.debugDomm:
            print("DEBUG ModelAction returns: ", model)

        return model

class NamedElementAction(SemanticAction):
    """
    Represents the named element meta class of
    DOMMLite's model. Named elements have long
    and short descriptions
    """
    def first_pass(self, parser, node, children):
        retVal = None

        # Remove all `"`from characters from list of children in case it isn't
        # omitted by the parser
        filter_children = (x for x in children if x != '"' )

        if parser.debugDomm:
            print("Debug NamedElementAction (children)", children)

        for ind, val in enumerate(filter_children):
            if val is not None:
                if not retVal:
                    retVal = NamedElement()

                if ind == 0:
                    retVal.short_desc = val
                else:
                    retVal.long_desc = val

        if parser.debugDomm:
            print("Debug NamedElementAction returns ", retVal)

        return retVal

class StringAction(SemanticAction):
    """
    Represents the basic string identified in programm
    """
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("Debug StringAction (children)", children)

        return children[0]

class IdAction(SemanticAction):
    """
    Represents actions done when identifier is found
    """
    def first_pass(self, parser, node, children):
        return Id(node.value)

class QidAction(SemanticAction):
    """
    Represents actions done when identifier is found
    """
    def first_pass(self, parser, node, children):
        path_list =  node.value.split(".")
        return Qid(path_list)

class IntAction(SemanticAction):
    """
    Returns an integer represenetation
    """
    def first_pass(self, parser, node, children):
        return int(node.value)

class EnumAction(SemanticAction):
    """
    Evaluates value of enumeration
    """
    def first_pass(self, parser, node, children):
        enum = Enumeration()

        for val in children:
            if type(val) is Id:
                enum.name = val._id
            elif type(val) is NamedElement:
                enum.set_descs(val)
            elif type(val) is EnumLiteral:
                enum.add_literal(val)


        return enum

class CommonTagAction(SemanticAction):
    """
    Evaluates value of (buildin)validatorType/tagType
    """
    def first_pass(self, parser, node, children):
        tag = CommonTag()

        if parser.debugDomm:
            print("DEBUG CommonTagAction children: ", children)

        for value in children:
            if type(value) is Id:
                tag.name = value._id
            elif type(value) is ConstrDef:
                tag.constr_def = value
            elif type(value) is ApplyDef:
                tag.applies = value
            elif type(value) is NamedElement:
               tag.set_descs(value)


        if parser.debugDomm:
            print("DEBUG CommonTagAction returns: ", tag)
        return tag

class ApplyDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        app_def = ApplyDef()

        if parser.debugDomm:
            print("DEBUG ApplyDefAction children: ", children)

        filter_children = (x for x in children if x != "appliesTo")

        for val in children:
            app_def.add_apply(val)

        if parser.debugDomm:
            print("DEBUG ApplyDefAction returns: ", app_def)
        return app_def

class ConstrDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        constr_def = ConstrDef()

        if parser.debugDomm:
            print("DEBUG ConstrDefAction children: ", children)

        # Filter all irrelevant strings from query
        filter_children = (x for x in children\
                            if x != "(" and x != ")" and x != ',')

        for val in filter_children:
            constr_def.add_constr(val)

        return constr_def

class EnumLiteralAction(SemanticAction):
    """
    Evaluates value of a part of enumeration
    """
    def first_pass(self, parser, node, children):
        # Name and value are mandatory and will always be present
        # children[0] is the enumeration literal's value
        # children[1] is the enumeration literal's value
        literal =  EnumLiteral(children[0]._id, children[1])

        # Enumeration may have a named element
        if len(children) == 3:
            literal.short_desc = children[2].short_desc
            literal.long_desc = children[2].long_desc

        return literal



class DataTypeAction(SemanticAction):
    """
    Returns evaluated DataType
    """
    def __init__(self, built_in = False):
        self.built_in = built_in

    def first_pass(self, parser, node, children):
        data_type = DataType(built_in = self.built_in)

        if parser.debugDomm:
            print("DEBUG DataTypeAction entered (children): ", children)

        for val in children:
            if type(val) is NamedElement:
                if parser.debugDomm:
                    print("DEBUG DataTypeAction entered (val): ", val)
                data_type.set_descs(val)
            elif type(val) is Id:
                data_type.name = val._id

        if parser.debugDomm:
            print("DEBUG DataTypeAction returns: ", data_type)


        return data_type


class ElipsisAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG ElipsisAction called")
        return "..."

class ConstraintAction(SemanticAction):
    """
    Returns evaluated constraint type
    """
    def __init__(self, built_in = False, is_tag = False):
        self.built_in = built_in
        if is_tag:
            self.constr_type = ConstraintType.Tag
        else:
            self.constr_type = ConstraintType.Validator

    def first_pass(self, parser, node, children):
        constraint = Constraint(built_in = self.built_in, \
                                constr_type = self.constr_type)
        if parser.debugDomm:
            print("DEBUG ConstraintAction entered children: ", children)

        for i in children:
            if type(i) is CommonTag:
                constraint.tag = i
            elif type(i) is Id:
                constraint.name = i._id

        if parser.debugDomm:
            print("DEBUG ConstraintAction returns: ", constraint)

        return constraint

class PackageAction(SemanticAction):
    def first_pass(self, parser, node, children):
        package = Package()

        filter_children = (x for x in children if type(x) is not str)

        if parser.debugDomm:
            print("DEBUG PackageAction (children)", children)

        for val in filter_children:
            if type(val) is Id:
                package.set_name(val._id)
            elif type(val) is NamedElement:
                package.set_descs(val)
            elif type(val) is Constraint:
                package.add_constraint(val)
            else:
                package.add_elem(val)

        return package

class TypeDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        type_def = TypeDef()

        for ind, val in enumerate(children):
            if type(val) is Qid:
                type_def.set_type(val._id)
            elif type(val) is Id:
                type_def.name = val._id
            elif val == "[":
                type_def.container = True
            elif type(val) is int:
                type_def.set_multi(val)

        if parser.debugDomm:
            print("DEBUG TypeDefAction returns: ", type_def)

        return type_def

class ConstraintSpecAction(SemanticAction):
    def first_pass(self, parser, node, children):
        temp_spec = ConstraintSpec()

        # We filter for strings to remove all `(` `)` `,` strings from children
        filter_children = (x for x in children\
                            if x != "," and x != "(" and x != ")")

        if parser.debugDomm:
            print("DEBUG ConstraintSpecAction enter (children): ", children)

        for ind, val in enumerate(filter_children):
            if type(val) is Qid:
                temp_spec.ident = val
            elif type(val) is Id:
                temp_spec.add_param(val)
            elif type(val) is str:
                temp_spec.add_param(val)
            elif type(val) is int:
                temp_spec.add_param(val)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecAction returns: ", temp_spec)

        return temp_spec

class SpecsObj(object):
    """Helper class for ConstrainSpecsAction"""
    def __init__(self, specs = None):
        super(SpecsObj, self).__init__()
        self.specs = set()
        if specs:
            self.specs = specs

    def __repr__(self):
        return " SpecsObj(%s)" % self.specs

class ConstraintSpecListAction(SemanticAction):
    def first_pass(self, parser, node, children):
        list_specs = SpecsObj()

        filter_children = (x for x in children \
                            if type(x) is ConstraintSpec or type(x) is Id)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecListAction enter (children): ",\
                    children)

        for val in filter_children:
            to_add = None

            if type(val) is ConstraintSpec:
                to_add = val
            elif type(val) is Id:
                temp = ConstraintSpec(ident = val)
                to_add = val

            for spec in list_specs.specs:
                if to_add.ident == spec.ident:
                    raise DuplicateConstrError(to_add.ident)

            list_specs.specs.add(to_add)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecListAction returns (list_specs): ",\
                    list_specs)

        return list_specs

class RefObj(object):
    """Helper class for RefAction SemanticAction"""
    def __init__(self, ident):
        super(RefObj, self).__init__()
        self.ident = ident

    def __repr__(self):
        return " RefObj(%s)" % self.ident._id


class RefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        retVal = None

        for val in children:
            if type(val) is Qid:
                retVal = RefObj(val)

        if parser.debugDomm:
            print("DEBUG RefAction returns: ", retVal)

        return retVal



class PropertyAction(SemanticAction):
    def first_pass(self, parser, node, children):
        prop = Property()

        if parser.debugDomm:
            print("DEBUG PropertyAction entered (children): {}\n"\
                    .format(children))

        for val in children:
            if val == "unique":
                prop.unique = True

            elif val == "ordered":
                prop.ordered = True

            elif val == "readonly":
                prop.readonly = True

            elif val == "required":
                prop.required = True

            elif type(val) is TypeDef:
                prop.type_def = val

            elif val == "+":
                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj on enter: {}\n"\
                            .format(prop.relationship))

                if prop.relationship is None:
                    prop.relationship = Relationship()

                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj (prop): {}\n"\
                            .format(prop.relationship))

                prop.relationship.containment = True
            elif type(val) is RefObj:
                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj on enter: {}\n"\
                            .format(prop.relationship))

                if prop.relationship is None:
                    prop.relationship = Relationship()

                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj (prop): {}\n"\
                            .format(prop.relationship))

                prop.relationship.opposite_end = val.ident

                if parser.debugDomm:
                    print("DEBUG PropertyAction After RefObj (prop): {}\n"\
                            .format(prop.relationship))
            elif type(val) is SpecsObj:
                for x in val.specs:
                    prop.add_constraint_spec(x)

            elif type(val) is NamedElement:
                if prop.type_def is None:
                    prop.type_def = TypeDef()

                prop.type_def.set_descs(val)

        if parser.debugDomm:
            print("DEBUG PropertyAction returns: ", prop)
            print("DEBUG PropertyAction returns prop.relationship", \
                    prop.relationship)

        return prop

    def second_pass(self, parser, node):
        # TODO containement, opposite ends
        if not parser.skip_crossref:
            model = node._parent_model
            qual_str = model.get_qid(node.type_def.type)

            if qual_str in model.qual_elems:
                bound_elem = model.qual_elems[qual_str]
                node.type_def._bound = bound_elem
                # If types aren't simple make a relation
                if type(bound_elem) is not DataType \
                    and type(bound_elem) is not Enumeration:
                    if node.relationship:
                        node.relationship = Relationship()
            else:
                raise TypeNotFoundError(qual_str)


class ExceptionAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG Entered ExceptionAction")

        exception = ExceptionType()

        # We filter for strings to remove all `{` `}`
        # and keywords strings from children
        filter_children =  (x for x in children if type(x) is not str)

        for val in filter_children:
            if type(val) is Id:
                exception.name = val._id
            elif type(val) is NamedElement:
                exception.set_descs(val)
            elif type(val) is Property:
                exception.add_prop(val)

        if parser.debugDomm:
            print("DEBUG  ExceptionAction returns ", exception)

        return exception

class ExtObj(object):
    """Helper object that carries a single reference"""
    def __init__(self, ref):
        super(ExtObj, self).__init__()
        self.ref = ref

    def __repr__(self):
        return " ExtObj (%s)" % self.ref

class ExtDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG ExtDefAction enter (children) ", children)
        # there are only two elements keyword and identifer
        for val in children:
            if type(val) is Qid:
                retVal = ExtObj(ref = CrossRef(\
                                        ref = val,
                                        ref_type = Ref.Entity))

                if parser.debugDomm:
                    print("DEBUG ExtDefAction returned ", retVal)

                return retVal

class DepObj(object):
    """Helper object that carries list of dependecies"""
    def __init__(self, rels):
        super(DepObj, self).__init__()
        assert type(rels) is list
        self.rels = rels

    def __repr__(self):
        retStr =  " DepObj ( "
        for val in self.rels:
            retStr += " %s " % val
        retStr += ")"
        return retStr

class DepDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        list_qid = []

        if parser.debugDomm:
            print("DEBUG Entered DepDefAction (children)", children)

        for val in children:
            if type(val) is Qid:
                if val in list_qid:
                    raise DuplicateDependsError(val)
                list_qid.append(val)

        retVal = DepObj(rels = [CrossRef(ref = x) for x in list_qid])

        if parser.debugDomm:
            print("DEBUG Entered DepDefAction returns ", retVal)

        return retVal

class OpParamAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG Entered OpParamAction (children)", children)

        param = OpParam()

        for val in children:
            if type(val) is TypeDef:
                param.type_def = val
            elif type(val) is NamedElement:
                param.set_descs(val)
            elif type(val) is SpecsObj:
                for x in val:
                    param.constraints.add(x)
            elif val == "ordered":
                param.ordered = True
            elif val == "required":
                param.required = True
            elif val == "unique":
                param.unique = True

        if parser.debugDomm:
            print("DEBUG Entered OpParamAction returns ", param)

        return param

class OperationAction(SemanticAction):
    def first_pass(self, parser, node, children):
        filter_children = (x for x in children \
                            if x != "(" and x != ")" and x != "{" and x != "}")

        if parser.debugDomm:
            print("DEBUG Entered OperationAction (children)", children)

        oper = Operation()
        for val in filter_children:
            if parser.debugDomm:
                print("DEBUG OperationAction loop val: ", val)
            if type(val) is TypeDef:
                oper.type_def = val
            elif type(val) is NamedElement:
                oper.set_descs(val)
            elif val == "ordered":
                oper.ordered = True
            elif val == "unique":
                oper.unique = True
            elif val == "required":
                oper.required = True
            elif type(val) is OpParam:
                oper.add_param(val)
            elif type(val) is SpecsObj:
                for x in val.specs:
                    oper.add_constraint_spec(x)
            elif type(val) is Qid:
                exc = CrossRef(ref = val, \
                               ref_type = Ref.ExceptType)
                oper.add_throws_exception(exc)

        if parser.debugDomm:
            print("DEBUG OperationAction returns", oper)
        return oper

    def second_pass(self, parser, node):
        if not parser.skip_crossref:
            # TODO Check rest of operations
            if parser.debugDomm:
                print("DEBUG2: Entered OperationAction, node ", node)
            model = node._parent_model
            if parser.debugDomm:
                print("DEBUG2: Entered OperationAction, model ", model.name)
            for exception in node.throws:
                if parser.debugDomm:
                    print("DEBUG2: Entered OperationAction, exception ",\
                            exception)
                model.get_elem_by_crosref(exception)


class CompartmentAction(SemanticAction):

    def __init__(self, is_op = True):
        self.is_op = is_op

    def first_pass(self, parser, node, children):
        comp = Compartment(is_op = self.is_op)

        filter_children = (x for x in children if type(x) is not str)

        if parser.debugDomm:
            print("DEBUG Entered CompartmentAction (children)", children)

        for val in filter_children:
            if type(val) is Id:
                comp.name = val._id
            elif type(val) is NamedElement:
                comp.set_descs(val)
            elif type(val) is Operation and self.is_op:
                comp.add_elem(val)
            elif type(val) is Property and not self.is_op:
                comp.add_elem(val)

        if parser.debugDomm:
            print("DEBUG CompartmentAction returns", comp)
        return comp

class ServiceAction(SemanticAction):
    def first_pass(self, parser, node, children):

        # We filter for strings to remove all `{` `}`
        # and keywords strings from children
        filter_children =  (x for x in children if type(x) is not str)

        if parser.debugDomm:
            print("DEBUG Entered ServiceAction (children)", children)

        service = Service()

        for val in filter_children:
            if type(val) is Id:
                service.name = val._id
            elif type(val) is NamedElement:
                service.set_descs(val)
            elif type(val) is ExtObj:
                if parser.debugDomm:
                    print("DEBUG Entered ServiceAction extends ", service)
                service.set_extends(val.ref)
            elif type(val) is DepObj:
                service.set_dependencies(val.rels)
            elif type(val) is SpecsObj:
                for x in val.specs:
                    service.add_constraint_spec(x)
            elif type(val) is Operation:
                service.add_operation(val)
            elif type(val) is Compartment:
                service.add_op_compartment(val)

        if parser.debugDomm:
            print("DEBUG Entered ServiceAction returns ", service)

        return service

    def second_pass(self, parser, node):
        if not parser.skip_crossref:
            if parser.debugDomm:
                print("DEBUG2: Entered ServiceAction, node ", node)
            model = node._parent_model
            if parser.debugDomm:
                print("DEBUG2: Entered ServiceAction, parent model ", \
                            model.name)
            # Bind extending CrossRef if they exist
            if node.extends:
                model.get_elem_by_crosref(node.extends)
            # Bind dependencies if they exist
            if node.dependencies and len(node.dependencies) > 0:
                for dep in node.dependencies:
                    model.get_elem_by_crosref(dep)
                    if parser.debugDomm:
                        print("DEBUG2: Entered ServiceAction, dep found ", \
                            dep)


class ValueObjectAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG Entered ServiceAction (children)", children)

        filter_children = (x for x in children if type(x) is not str)

        val_obj = ValueObject()

        for val in filter_children:
            if type(val) is Id:
                val_obj.name = val._id
            elif type(val) is NamedElement:
                val_obj.set_descs(val)
            elif type(val) is ExtObj:
                val_obj.set_extends(val.ref)
            elif type(val) is DepObj:
                val_obj.set_dependencies(val.rels)
            elif type(val) is SpecsObj:
                for x in val.specs:
                    val_obj.add_constraint_spec(x)
            elif type(val) is Property:
                val_obj.add_prop(val)

        if parser.debugDomm:
            print("DEBUG ServiceAction returns ", val_obj)

        return val_obj

    def second_pass(self, parser, node):
        if not parser.skip_crossref:
            if parser.debugDomm:
                print("DEBUG2: Entered ValueObjectAction, node ", node)
            model = node._parent_model
            if parser.debugDomm:
                print("DEBUG2: Entered ValueObjectAction, parent model ",\
                        model.name)
             # Bind extending CrossRef if they exist
            if node.extends:
                model.get_elem_by_crosref(node.extends)
            # Bind dependencies if they exist
            if node.dependencies and len(node.dependencies) > 0:
                for dep in node.dependencies:
                    model.get_elem_by_crosref(dep)
                    if parser.debugDomm:
                        print("DEBUG2: Entered ValueObjectAction, dep found ", \
                            dep)

            # Check constraints
            if node.constraints and len(node.constraints) > 0:
                for constr in node.constraints:
                    if parser.debugDomm:
                        print("DEBUG2: Entered ValueObjectAction, constr found"\
                                    ,constr)
                    qid = model.get_qid(constr.ident)
                    if parser.debugDomm:
                        print("DEBUG2: Entered ValueObjectAction, qid found "\
                                    ,qid)
                    const_spec = model.qual_elems[qid]
                    if parser.debugDomm:
                        print("DEBUG2: Entered Found constr "\
                                    ,const_spec)
                    const_spec.check_applies(node, node.name)
                    const_spec.check_params(constr)



class KeyAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG KeyAction children  ", children)

        key = Key()

        filter_children = (x for x in children if type(x) is Property)

        for x in filter_children:
            key.add_prop(x)

        if parser.debugDomm:
            print("DEBUG KeyAction returns ", key)

        return key

class RelIdAction(SemanticAction):
    def first_pass(self, parser, node, children):
        retval = None
        if type(children[0]) is Id:
            retval = Qid([children[0]._id])
        elif type(children[0]) is Qid:
            retval = children[0]
        return retval

class PropRefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG PropRefAction children  ", children)
        retVal = CrossRef(ref = Id(node.value),\
            ref_type = Ref.Property)

        if parser.debugDomm:
            print("DEBUG PropRefAction returns  ", retVal)

        return retVal


class ReprAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG ReprAction children ", children)

        rep = Repr()

        filter_children = (x for x in children if x != "+")

        for val in filter_children:
            rep.add_elem(val)

        if parser.debugDomm:
            print("DEBUG ReprAction returns ", rep)

        return rep

class EntityAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG Entered EntityAction (children)", children)

        ent = Entity()

        for val in children:
            if type(val) is Id:
                ent.name = val._id
            elif type(val) is NamedElement:
                ent.set_descs(val)
            elif type(val) is Key:
                ent.set_key(val)
            elif type(val) is Repr:
                ent.set_repr(val)
            elif type(val) is ExtObj:
                ent.set_extends(val.ref)
            elif type(val) is DepObj:
                ent.set_dependencies(val.rels)
            elif type(val) is SpecsObj:
                for x in val.specs:
                    ent.add_constraint_spec(x)
            elif type(val) is Compartment:
                ent.add_comparment(val)
            elif type(val) is Operation or type(val) is Property:
                ent.add_feature(val)

        if parser.debugDomm:
            print("DEBUG Entered EntityAction returns", ent)

        return ent

    def second_pass(self, parser, node):
        if not parser.skip_crossref:
            if parser.debugDomm:
                print("DEBUG2: Entered ValueObjectAction, node ", node)
            model = node._parent_model
            if parser.debugDomm:
                print("DEBUG2: Entered ValueObjectAction, parent model ",\
                        model.name)
            # Bind extending CrossRef if they exist
            if node.extends:
                model.get_elem_by_crosref(node.extends)
            # Bind dependencies if they exist
            if node.dependencies and len(node.dependencies) > 0:
                for dep in node.dependencies:
                    model.get_elem_by_crosref(dep)
                    if parser.debugDomm:
                        print("DEBUG2: Entered ServiceAction, dep found ", \
                            dep)
