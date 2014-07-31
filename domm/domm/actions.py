from arpeggio import SemanticAction
from metamodel import *

class DommAction(SemanticAction):
    """
    Simple action that returns a dictionary of models
    """
    def first_pass(self, parser, node, children):
        model_map = dict()

        filter_children = [x for x in children if type(x) != str]

        for x in filter_children:
            model_map[x.name] = x
        return model_map

class ModelAction(SemanticAction):
    """
    Represents semantic action Model in DOMMLite
    """
    def first_pass(self, parser, node, children):
        # ID should been always present
        name = children[1]._id
        model = Model()

        for ind, val in enumerate(children):
            if type(val) == Id:
                model.name = val._id
            elif type(val) == NamedElement:
                model.set_desc(val.short_desc, val.long_desc)
            elif type(val) == DataType or type(val) == Enumeration:
                model.add_type(val)
            elif type(val) == Constraint:
                model.add_constraint(val)
            elif type(val) == Package:
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
        # If we encounter two child nodes it means there are exactly two strings
        # of which first is the short and second is long description.
        if len(children) == 2:
            return NamedElement(short_desc=children[0], long_desc=children[1])
        # If we encounter three child nodes it means there is exaclty one string
        # i.e. only short description, becauser there will be following nodes
        #   "(0)  text(1) "(2)
        # We obviously only want the second node that contains text
        # TODO See why this happens
        elif len(children) == 3:
            return NamedElement(short_desc=children[1])


class StringAction(SemanticAction):
    """
    Represents the basic string identified in programm
    """
    def first_pass(self, parser, node, children):
        return children[1]

class IdAction(SemanticAction):
    """
    Represents actions done when identifier is found
    """
    def first_pass(self, parser, node, children):
        return Id(node.value, namespace = parser.namespace)

class IntAction(SemanticAction):
    """
    Returns an integer represenetation
    """
    def first_pass(self, parser, node, children):
        return int(node.value)

class TypesAction(SemanticAction):
    """
    Evaluates value of given type
    """
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("Entered TypesAction")
            print("Entered children = ", children)
        # First keyword can only be
        #   enum
        #   buildinDataType/dataType
        #   tagType/buildinTagType
        #   validator/buildinValidator
        if children[0] == "enum" :
            return EnumAction().first_pass(parser, node, children)
        elif children[0] == "buildinDataType" or children[0] == "dataType":
            return DataTypeAction().first_pass(parser, node, children)
        elif children[0] == "buildinValidator" or children[0] == "validatorType" or children [0] == "buildinTagType" or children[0] == "tagType":
            if parser.debugDomm:
                print("DEBUG validator branch (children): ", children)
            return ConstraintAction().first_pass(parser, node, children)

class EnumAction(SemanticAction):
    """
    Evaluates value of enumeration
    """
    def first_pass(self, parser, node, children):
        enum = Enumeration(name = children[1]._id, namespace = parser.namespace)

        for i in range(1, len(children)):
            if type(children[i]) == NamedElement:
                enum.short_desc = children[i].short_desc
                enum.long_desc = children[i].long_desc
            elif type(children[i]) == EnumLiteral:
                enum.add_literal(children[i])
        return enum

class CommonTagAction(SemanticAction):
    """
    Evaluates value of (buildin)validatorType/tagType
    """
    def first_pass(self, parser, node, children):
        name = children[0]._id
        short_desc = None
        long_desc = None
        constr_def = None
        apply_def = None

        if parser.debugDomm:
            print("DEBUG CommonTagAction children: ", children)

        for value in children:

            if type(value) == ConstrDef:
                constr_def = value
            elif type(value) == ApplyDef:
                apply_def = value
            elif type(value) == NamedElement:
                if parser.debugDomm:
                    print("DEBUG CommonTagAction NamedElement: ", value)
                long_desc = value.long_desc
                short_desc = value.short_desc

        tag = CommonTag(name, short_desc = short_desc, long_desc = long_desc, constr_def = constr_def, applies = apply_def)

        if parser.debugDomm:
            print("DEBUG CommonTagAction returns: ", tag)
        return tag

class ApplyDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        app_def = ApplyDef()

        for i in range(1, len(children)):
            app_def.add_apply(children[i])

        if parser.debugDomm:
            print("DEBUG ApplyDefAction returns: ", app_def)
        return app_def

class ConstrDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        constr_def = ConstrDef()

        # Filter all irrelevant strings from query
        filter_children = [x for x in children if x != "(" and x != ")" and x != ',']

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
    def first_pass(self, parser, node, children):
        if children[0] == "buildinDataType":
            builtin = True
        elif children[0] == "dataType":
            builtin = False

        name = children[1]._id
        short_desc = None
        long_desc = None

        if len(children)== 3:
            short_desc = children[2].short_desc
            long_desc = children[2].long_desc

        data_type = DataType(name, built_in = builtin, short_desc= short_desc,
            long_desc= long_desc, namespace= parser.namespace)
        return data_type

class ConstraintAction(SemanticAction):
    """
    Returns evaluated constraint type
    """
    def first_pass(self, parser, node, children):
        builtin = None
        types = None
        tag = None

        if children[0] == "buildinValidator":
            builtin = True
            types = ConstraintType.Validator
        elif children[0] == "validatorType":
            builtin = False
            types = ConstraintType.Validator
        elif children[0] == "buildinTagType":
            builtin = True
            types = ConstraintType.Tag
        elif children[0] == "tagType":
            builtin = False
            types = ConstraintType.Tag


        if type(children[1]) == CommonTag:
            tag = children[1]
        # If only id is present the arpeggio will first identify id instead of Common tag
        elif type(children[1]) == Id:
            tag = CommonTag(name = children[1]._id)

        constraint = Constraint(tag = tag, built_in = builtin, constr_type = types,
            namespace = parser.namespace)

        if parser.debugDomm:
            print("DEBUG ConstraintAction returns: ", constraint)

        return constraint

class PackageElemAction(SemanticAction):
    """
    Since package element can be multiple elements and the arpeggio
    parser parses package_elem not as one of matching elements
    but as package element, this action just recognizes the right
    element based on keyword and lets the appropriate action take
    care of it
    """
    def first_pass(self, parser, node, children):
        if children[0] == "buildinDataType" or children[0] == "dataType":
            return DataTypeAction().first_pass(parser, node, children)
        elif children[0] == "buildinValidator" or children[0] == "validator" or children[0] == "buildinTagType" or children[0] == "tagType" :
            return ConstraintAction().first_pass(parser, node, children)
        elif children[0] == "package":
            return PackageAction().first_pass(parser, node, children)

class PackageAction(SemanticAction):
    def first_pass(self, parser, node, children):
        package = Package()

        if parser.debugDomm:
            print("DEBUG PackageAction (children)", children)

        for ind, val in enumerate(children):
            if type(val) == Id:
                #print("Id found: {}".format(val))
                package.set_name(val._id)
            elif type(val) == NamedElement:
                package.set_desc(short_desc = val.short_desc, long_desc = val.long_desc)
            elif type(val) == DataType:
                package.add_elem(val)
            elif type(val) == Enumeration:
                package.add_elem(val)
            elif type(val) == Constraint:
                package.add_elem(val)
            elif type(val) == Package:
                package.add_elem(val)

        return package

class TypeDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        type_def = TypeDef()

        for ind, val in enumerate(children):
            if type(val) == Id and ind == 0:
                type_def.set_type(val._id)
            elif type(val) == Id and ind != 0:
                type_def.name = val._id
            elif val == "[":
                type_def.container = True
            elif type(val) == int:
                type_def.set_multi(val)

        if parser.debugDomm:
            print("DEBUG TypeDefAction returns: ", type_def)

        return type_def

class ConstraintSpecAction(SemanticAction):
    def first_pass(self, parser, node, children):
        spec = ConstraintSpec()

        filter_children = [x for x in children if x != "(" and x != ")"]

        for ind, val in enumerate(filter_children):
            if type(val) == Id and ind == 0:
                spec.ident = val
            elif type(val) == Id and ind != 0:
                spec.add_param(val)
            elif type(val) == str :
                spec.add_param(val)
            elif type(val) == int:
                spec.add_param(val)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecAction returns: ", spec)

        return spec

class SpecsObj(object):
    """Helper class for ConstrainSpecsAction"""
    def __init__(self, list):
        super(SpecsObj, self).__init__()
        filter_list = [x for x in list if x != "[" and x != "]" and type(x)==ConstrSpec]
        self.list_specs = filter_list

class ConstraintSpecsAction(SemanticAction):
    def first_pass(self, parser, node, children):
        return SpecsObj(children)

class RefObj(object):
    """Helper class for RefAction SemanticAction"""
    def __init__(self, ident):
        super(RefObj, self).__init__()
        self.ident = ident


class RefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        for val in children:
            if type(val) == Id:
                return RefObj(val)

class PropertyAction(SemanticAction):
    def first_pass(self, parser, node, children):
        prop = Property()

        for val in children:
            if val == "unique":
                prop.unique = True

            elif val == "ordered":
                prop.ordered = True

            elif val == "readonly":
                prop.readonly = True

            elif val == "required":
                prop.required = True

            elif type(val) == TypeDef:
                prop.type_def = val

            elif val == "+":
                if prop.relationship is None:
                    rel = Relationship()
                    prop.relationship = rel

                prop.relationship.containment = True
            elif type(val) == RefObj:
                if prop.relationship is None:
                    rel = Relationship()
                    prop.relationship = rel

                prop.relationship.opposite_end = val.ident
            elif type(val) == SpecsObj:
                for x in val.list_specs:
                    prop.add_constraint_spec(x)

            elif type(val) == NamedElement:
                prop.set_desc(val.short_desc, val.long_desc)

        return prop

    def second_pass(self, parser, node):
        pass

class ExceptionAction(SemanticAction):
    def first_pass(self, parser, node, children):
        exception = ExceptionType()

