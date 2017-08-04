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
    assert e.struct_table() == '{ a: { c: {},},}'
    e.set_data('a.c', False)
    assert e.struct_table() == '{}'
