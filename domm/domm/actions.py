from arpeggio import SemanticAction
from metamodel import *

class ModelAction(SemanticAction):
    """
    Represents semantic action Model in DOMMLite
    """
    def first_pass(self, parser, node, children):
        # ID should been always present
        name = children[1]._id
        model = Model(name)

        for i in range(1, len(children)):
            if type(children[i]) == NamedElement:
                model.short_desc = children[i].short_desc
                model.long_desc = children[i].long_desc
            elif type(children[i]) == DataType or type(children[i]) == Enumeration:
                model.add_types(children[i])

        #print("DEBUG Model: node  {} \n\n children {}".format(node, children))
        print("DEBUG {}".format(model))
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
        return Id(node.value)

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
        # First keyword can only be
        #   enum
        #   buildinDataType/dataType
        #   tagType/buildinTagType
        #   validator/buildinValidator
        if children[0] == "enum" :
            return EnumAction().first_pass(parser, node, children)
        elif children[0] == "buildinDataType" or children[0] == "dataType":
            return DataTypeAction().first_pass(parser, node, children)

class EnumAction(SemanticAction):
    """
    Evaluates value of enumeration
    """
    def first_pass(self, parser, node, children):
        enum = Enumeration(name = children[1]._id)

        for i in range(1, len(children)):
            if type(children[i]) == NamedElement:
                enum.short_desc = children[i].short_desc
                enum.long_desc = children[i].long_desc
            elif type(children[i]) == EnumLiteral:
                enum.add_literal(children[i])
        return enum

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

        data_type = DataType(name, built_in = builtin, short_desc= short_desc, long_desc= long_desc)
        return data_type
