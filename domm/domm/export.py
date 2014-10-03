##############################################################################
# Name: export.py
# Purpose: Exporter for DOMMLite parser
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
from metamodel import Model

class DommExport(object):
    """docstring for DommExport"""
    def __init__(self,):
        super(DommExport, self).__init__()

    def export_model(self, model, file_name):
        processed_set = set()
        print("TYPE:",type(model))
        header = """
        digraph %s {
            fontname = "Bitstream Vera Sans"
            fontsize = 8
            node[
                shape=record,
                style=filled,
                fillcolor=aliceblue
            ]
            edge[dir=black,arrowtail=empty]
        """ % (model.name)


        with open(file_name, 'w') as f:
            f.write(header)
            f.write('\n}\n')