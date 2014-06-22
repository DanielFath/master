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
class Model(object):
    """
    This class represents the meta model for DOMMLite model
    object. DOMMLite model is a container for other objects.
    """
    def __init__(self, name, short_desc = None, long_desc = None):
        super(Model, self).__init__()
        self._name = name
        self._short_desc = short_desc
        self._long_desc = long_desc
        self._types = []
        self._packages = []

    def add_types(self, type_def):
        self._types.append(type_def)

    def set_types(self, types):
        self._types = types

    def add_package(self, package):
        self._packages.append(package)

    def set_types(self, packages):
        self._packages = packages

    def first_pass(self, parser, node, children):
        print("First pass node {}".format(node))
        print("First pass children {}".format(children))

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
