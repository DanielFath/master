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
            if type(val) is Id:
                model.name = val._id
            elif type(val) is NamedElement:
                model.set_desc(val.short_desc, val.long_desc)
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
            if type(children[i]) is NamedElement:
                enum.short_desc = children[i].short_desc
                enum.long_desc = children[i].long_desc
            elif type(children[i]) is EnumLiteral:
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

            if type(value) is ConstrDef:
                constr_def = value
            elif type(value) is ApplyDef:
                apply_def = value
            elif type(value) is NamedElement:
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


        if type(children[1]) is CommonTag:
            tag = children[1]
        # If only id is present the arpeggio will first identify id instead of Common tag
        elif type(children[1]) is Id:
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
        elif children[0] == "exception":
            return ExceptionAction().first_pass(parser, node, children)
        elif children[0] == "service":
            return ServiceAction().first_pass(parser, node, children)

    def second_pass(self, parser, node):
        pass

class PackageAction(SemanticAction):
    def first_pass(self, parser, node, children):
        package = Package()

        filter_children = [x for x in children if type(x) is not str]

        if parser.debugDomm:
            print("DEBUG PackageAction (filter_children)", filter_children)

        for val in filter_children:
            if type(val) is Id:
                package.set_name(val._id)
            elif type(val) is NamedElement:
                package.set_desc(short_desc = val.short_desc, long_desc = val.long_desc)
            else:
                package.add_elem(val)

        return package

class TypeDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        type_def = TypeDef()

        for ind, val in enumerate(children):
            if type(val) is Id and ind == 0:
                type_def.set_type(val._id)
            elif type(val) is Id and ind != 0:
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
        filter_children = [x for x in children if type(x) is not str]

        if parser.debugDomm:
            print("DEBUG ConstraintSpecAction enter (filter_children): ", filter_children)

        for ind, val in enumerate(filter_children):
            if type(val) is Id and ind == 0:
                temp_spec.ident = val
            elif type(val) is Id and ind != 0:
                temp_spec.add_param(val)
            elif type(val) is StrObj :
                temp_spec.add_param(val.content)
            elif type(val) is int:
                temp_spec.add_param(val)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecAction returns: ", temp_spec)

        return temp_spec

class StrObj(object):
    """Helper class for string in StrObj"""
    def __init__(self, content = ""):
        super(StrObj, self).__init__()
        self.content = content

    def __repr__(self):
        return "StrObj[%s]" % self.content


class ConstraintParamAction(SemanticAction):
    """
    This action is used to get string content of a ConstraintSpec without
    getting comma or quotation marks.
    """
    def first_pass(self, parser, node, children):
        # Since this only appears when string is involved, we
        # just assume the second child is the strings content
        # Parse tree looks a bit like this:
        #   (") (string) (")
        string_param = StrObj(children[1])

        if parser.debugDomm:
            print("DEBUG ConstraintParamAction returns: ", string_param)

        return string_param

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

        filter_children = [x for x in children if type(x) is ConstraintSpec or type(x) is Id]

        if parser.debugDomm:
            print("DEBUG ConstraintSpecListAction enter (filter_children): ", filter_children)

        for val in filter_children:
            if type(val) is ConstraintSpec:
                list_specs.specs.add(val)
            elif type(val) is Id:
                temp = ConstraintSpec(ident = val)
                list_specs.specs.add(temp)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecListAction returns (list_specs): ", list_specs)

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
            if type(val) is Id:
                retVal = RefObj(val)

        if parser.debugDomm:
            print("DEBUG RefAction returns: ", retVal)

        return retVal



class PropertyAction(SemanticAction):
    def first_pass(self, parser, node, children):
        prop = Property()

        if parser.debugDomm:
            print("DEBUG PropertyAction entered (children): {}\n".format(children))

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
                    print("DEBUG PropertyAction  RefObj on enter: {}\n".format(prop.relationship))

                if prop.relationship is None:
                    prop.relationship = Relationship()

                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj (prop): {}\n".format(prop.relationship))

                prop.relationship.containment = True
            elif type(val) is RefObj:
                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj on enter: {}\n".format(prop.relationship))

                if prop.relationship is None:
                    prop.relationship = Relationship()

                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj (prop): {}\n".format(prop.relationship))

                prop.relationship.opposite_end = val.ident

                if parser.debugDomm:
                    print("DEBUG PropertyAction After RefObj (prop): {}\n".format(prop.relationship))
            elif type(val) is SpecsObj:
                for x in val.specs:
                    prop.add_constraint_spec(x)

            elif type(val) is NamedElement:
                if prop.type_def is None:
                    prop.type_def = TypeDef()

                prop.type_def.set_desc(val.short_desc, val.long_desc)

        if parser.debugDomm:
            print("DEBUG PropertyAction returns: ", prop)
            print("DEBUG PropertyAction returns prop.relationship", prop.relationship)

        return prop

class ExceptionAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG Entered ExceptionAction")

        exception = ExceptionType()

        # We filter for strings to remove all `{` `}` and keywords strings from children
        filter_children = [x for x in children if type(x) is not str]

        for val in filter_children:
            if type(val) is Id:
                exception.name = val._id
            elif type(val) is NamedElement:
                exception.set_desc(short_desc = val.short_desc, long_desc = val.long_desc)
            elif type(val) is Property:
                exception.add_prop(val)

        if parser.debugDomm:
            print("DEBUG  ExceptionAction returns ", exception)

        return exception

class ServiceAction(SemanticAction):
    def first_pass(self, parser, node, children):

        # We filter for strings to remove all `{` `}` and keywords strings from children
        filter_children = [x for x in children if type(x) is not str]

        if parser.debugDomm:
            print("DEBUG Entered ServiceAction (children)", children)


class ExtObj:
    """Helper object that carries a single reference"""
    def __init__(self, ref):
        self.ref = ref

    def __repr__(self):
        return " ExtObj (%s)" % self.ref


class ExtDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        # there are only two elements keyword and identifer
        retVal = ExtObj(ref = ClassifierBound(ref = children[1], type_of = ClassType.Entity))

        if parser.debugDomm:
            print("DEBUG ExtDefAction returned ", retVal)

        return retVal
