##############################################################################
# Name: test_metamode.py
# Purpose: Test for correct metamodel behavior
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
from  domm.metamodel import Qid, Package, Property, ValueObject, Operation,\
    ExceptionType, Key, Entity, TypeDef, Service, Model, DataType

def test_qid():
    qid_from_str = Qid("test.x.a")
    qid = Qid(["test", "x", "a"])
    assert qid_from_str == qid
    assert qid_from_str.depth() == 3

    qid_outer = Qid(qid.path).add_outer_level("out")
    assert qid_outer == Qid(["out", "test", "x", "a"])
    assert qid_outer.depth() == 4

def test_namespace_package():
    pack1 = Package(name = "test")
    prop1 = Property(type_def = TypeDef(name = "X", type_of = "string"))
    vobj1 = ValueObject(name = "vo").add_prop(prop1)
    pack1.add_elem(vobj1)

    expected1elems = {Qid("test.vo"): vobj1}
    expected1imprt = {Qid("test.vo.X") : prop1}
    assert expected1elems == pack1.elems
    assert expected1imprt == pack1._imported


    pack2 = Package(name = "test")
    prop2 = Property(type_def = TypeDef(name = "X", type_of = "string"))
    excp2 = ExceptionType(name = "except").add_prop(prop2)
    pack2.add_elem(excp2)

    expected2elems = {Qid("test.except") : excp2}
    expected2imprt = {Qid("test.except.X") : prop2}
    assert expected2elems == pack2.elems
    assert expected2imprt == pack2._imported

    pack3 = Package(name = "test")
    oper3 = Operation(type_def = TypeDef(name = "X", type_of = "int"))
    serv3 = Service(name = "service").add_operation(oper3)
    pack3.add_elem(serv3)

    expected3elems = {Qid("test.service"): serv3}
    expected3imprt = {Qid("test.service.X") : oper3}
    assert expected3elems == pack3.elems
    assert expected3imprt == pack3._imported

    pack4 = Package(name = "test")
    prop4 = Property(type_def = TypeDef(name = "id", type_of = "int"))
    key4  = Key().add_prop(prop4)
    enti4 = Entity(name = "ent").set_key(key4)
    pack4.add_elem(enti4)

    expected4elems = {Qid("test.ent"): enti4}
    expected4imprt = {Qid("test.ent.id") : prop4}
    assert expected4elems == pack4.elems
    assert expected4imprt == pack4._imported

    pack5 = Package(name = "ex")
    pack5.add_elem(pack4)

    expected5elems = {Qid("ex.test"): pack4}
    expected5imprt = {Qid("ex.test.ent") : enti4, Qid("ex.test.ent.id"): prop4}
    print("pack5._imported ", pack5._imported)
    print("pack5.elems ", pack5.elems)
    assert expected5elems == pack5.elems
    assert expected5imprt == pack5._imported

def test_model_unique():
    model = Model(name = "test")
    data  = DataType(name = "id")
    pack1 = Package(name = "dup").add_elem(data)
    pack2 = Package(name = "dup").add_elem(data)
    pack1.add_elem(pack2)

    model.add_package(pack1)
    print('model.unique["id"] ',model.unique["id"])
    assert model.unique["id"] == False
