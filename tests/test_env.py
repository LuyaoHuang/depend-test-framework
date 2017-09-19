import pytest
import os
import sys

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.isdir(os.path.join(BASEDIR, 'depend_test_framework')):
    os.environ['PATH'] += ":" + os.path.join(BASEDIR, 'tests')
    sys.path.insert(0, BASEDIR)

from depend_test_framework.core import Env


def test_env():
    e = Env()
    e.set_data('a.c', 1)
    assert e['a']['c'].data == 1
    assert e.get_data('a.c').data == 1
    assert e.struct_table() == '{ a|False: { c|True: {},},}'
    e.set_data('a.c', False)
    assert e.struct_table() == '{}'

    e2 = Env()
    e2.set_data('a.b', 1)
    e.set_data('a.c', 1)
    assert not e2 <= e
    assert not e2 >= e
    assert e2 is not e
    e2.set_data('a.c', 1)
    assert not e2 <= e
    assert e2 >= e
    assert e2.__repr__() == "<Env path='' data='None'>"
    assert e2['a']['c'].__repr__() == "<Env path='a.c' data='1'>"

    e3 = Env()
    e3.set_data('a.c', False)
    assert not e3.get_data('a.c').data
    e4 = Env()
    e4.set_data('d', True)
    e3.set_data('a.c', e4)
    assert e3.struct_table() == "{ a|False: { c|False: { d|True: {},},},}"
    assert e3.get_data('a.c.d').__repr__() == "<Env path='a.c.d' data='True'>"
