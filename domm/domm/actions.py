from arpeggio import SemanticAction
from metamodel import *

class ModelAction(SemanticAction):
    """
    Represents semantic action Model in DOMMLite
    """
    def first_pass(self, parser, node, children):
        name = children[1]._name
        short_desc = None
        long_desc = None
        # ID should been always present

        if len(children) >=3 and type(children[2]) == NamedElement:
            short_desc = children[2].short_desc
            long_desc  = children[2].long_desc

        model = Model(name, short_desc, long_desc)

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
        print("Found string {}".format(children[1]))
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

class DataTypeAction(SemanticAction):
    """
    Returns evaluated DataType
    """
    def first_pass(self, parser, node, children):
        pass