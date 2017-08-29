import pytest
import os
import sys

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.isdir(os.path.join(BASEDIR, 'depend_test_framework')):
    os.environ['PATH'] += ":" + os.path.join(BASEDIR, 'tests')
    sys.path.insert(0, BASEDIR)

from depend_test_framework import case

def test_case():
    c1 = case.Case([1,2,3])
    c2 = case.Case([10,4])

    assert c1 > c2
    assert c1 >= c2
    assert not c1 <= c2
    assert not c1 < c2

    assert list(c1.steps) == [1,2,3]
    assert c1.step_num == 3
    c3 = c1 + c2
    assert list(c3.steps) == [1,2,3,10,4]
    assert list(c1.steps) == [1,2,3]
    assert list(c2.steps) == [10, 4]
