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
