##############################################################################
# Name: export.py
# Purpose: Exporter for DOMMLite parser
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
from metamodel import *

class DommExport(object):
    """docstring for DommExport"""
    def __init__(self,):
        super(DommExport, self).__init__()

    def render_enum(self, f, enum):
        """
        This method renders Enumeration in dot format and writes into f buffer.

        It adds every literal name into a special cell of enumeration.
        """
        str_val = '%s[label="   |{%s|' % (id(enum), enum.name)
        for lit in enum.literals:
            str_val += "%s\l" % lit.name
        str_val += '}"]\n'
        f.write(str_val)

    def render_prop(self, prop):
        """
        This method returns a string represenatation of property.
        """
        str_val = ''
        # Add required information
        if prop.required == True:
            str_val += '+ '
        else:
            str_val += '? '

        # Add name
        str_val += '%s: ' % prop.name

        # Add type information but check if type is qualified
        if type(prop.type_def.type) is Qid:
            str_val += '%s ' % prop.type_def.type._id
        else:
            str_val += '%s ' % prop.type_def.type
        # Add multiplicity information
        if prop.type_def.container == True:
            str_val += "["
            if prop.type_def.multi:
                str_val += prop.type_def.multi.__str__()
            str_val += "]"

        str_val += '\l'
        return str_val

    def render_param(self, param):
        """
        This method returns string represenatation of parameter
        """
        # Add name
        str_val = '%s: ' % param.type_def.name

        # Add type information but check if type is qualified
        if type(param.type_def.type) is Qid:
            str_val += '%s ' % param.type_def.type._id
        else:
            str_val += '%s ' % param.type_def.type
        # Add multiplicity information
        if param.type_def.container == True:
            str_val += "["
            if param.type_def.multi:
                str_val += param.type_def.multi.__str__()
            str_val += "]"

        return str_val

    def render_op(self, op):
        """
        This method returns a string represenatation of an operation
        and it's parameters.
        """
        str_val = op.op_name.__str__()
        str_val += '('

        type_name =''
        if type(op.type_def.type) is Qid:
            type_name = '%s ' % op.type_def.type._id
        else:
            type_name = '%s ' % op.type_def.type

        for i, param in enumerate(op.params):
            if i > 0:
                str_val += ","
            str_val += self.render_param(param)


        str_val += ') : %s\l' % type_name
        return str_val

    def render_vo(self, f, vo):
        """
        This method renders Enumeration in dot format.
        """
        str_val = '%s[style=rounded, label="{%s|' % (id(vo), vo.name)
        for prop in vo.props.itervalues():
            str_val += self.render_prop(prop)
        str_val += '}"]\n'
        f.write(str_val)

    def render_excp(self, f, excp):
        """
        This method renders ExceptionType.
        """
        str_val = '%s[style=dashed, label="{%s|' % (id(excp), excp.name)
        for prop in excp.props.itervalues():
            str_val += self.render_prop(prop)
        str_val += '}"]\n'
        f.write(str_val)

    def render_service(self, f, serv):
        """
        Renders a service to a buffer - `f`
        """
        str_val = '%s[style = diagonals, label = "{%s|' % (id(serv), serv.name)

        for op in serv.operations:
            str_val += self.render_op(serv.elems[op])

        for comp in serv.op_compartments.itervalues():
            comp_name = comp.name
            if comp.short_desc:
                comp_name = comp.short_desc
            str_val += "|%s|" % comp_name
            for op in comp.elements:
                str_val += self.render_op(op)

        str_val += '}"]\n'
        f.write(str_val)

    def render_entity(self, f, ent):
        """
        Renders a service to a buffer - `f`
        """
        str_val = '%s[label = "{%s|' % (id(ent), ent.name)

        for feature in ent.features:
            feat = ent.elems[feature]
            if type(feat) is Operation:
                str_val += self.render_op(feat)
            elif type(feat) is Property:
                str_val += self.render_prop(feat)

        for comp in ent.compartments.itervalues():
            comp_name = comp.name
            if comp.short_desc:
                comp_name = comp.short_desc
            str_val += "|%s|" % comp_name
            for el in comp.elements:
                if type(el) is Operation:
                    str_val += self.render_op(el)
                elif type(el) is Property:
                    str_val += self.render_prop(el)

        str_val += '}"]\n'
        f.write(str_val)

    def export_model(self, model, file_name):
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
    edge[dir=black,arrowtail=empty]\n""" % (model.name)

        with open(file_name, 'w') as f:
            f.write(header)

            for elem in model.qual_elems.itervalues():
                if type(elem) is DataType:
                    # Print dataType
                    data = '%s[label="   |%s"]\n' % (id(elem), elem.name)
                    f.write(data)
                elif type(elem) is Enumeration:
                    self.render_enum(f, elem)
                elif type(elem) is ValueObject:
                    self.render_vo(f, elem)
                elif type(elem) is ExceptionType:
                    self.render_excp(f, elem)
                elif type(elem) is Service:
                    self.render_service(f, elem)
                elif type(elem) is Entity:
                    self.render_entity(f, elem)

            # Filter relationships that aren't part of another
            filtered_rels = (x for x in model._rels if x._super_rel is None)
            for rel in filtered_rels:
                print("rel ", rel)
                if rel.rel_type == RelType.Extends:
                    rel_str = '%s -> %s [arrowhead = empty]\n'\
                            % (id(rel.elem_a), id(rel.elem_b))
                    f.write(rel_str)
                elif rel.rel_type == RelType.Depends:
                    rel_str = '%s -> %s [style = dashed]\n'\
                            % (id(rel.elem_a), id(rel.elem_b))
                    f.write(rel_str)
                elif rel.rel_type == RelType.Composite:
                    rel_str = '%s -> %s [dir = both, arrowtail=diamond]\n'\
                            % (id(rel.elem_a), id(rel.elem_b))
                    f.write(rel_str)

            f.write('\n}\n')