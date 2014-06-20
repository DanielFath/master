﻿##############################################################################
# Name: domm_peg.py
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
from arpeggio import SemanticAction


# This class represents the meta model of the DOMMLite structure
class Model(SemanticAction):
    """
    This class represents the meta model for DOMMLite model
    object. DOMMLite model is a container for other objects.
    """
    def __init__(self, name, short_desc = "", long_desc=""):
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