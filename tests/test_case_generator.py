import pytest
import os
import sys

from utils import ResourceWatcher

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.isdir(os.path.join(BASEDIR, 'depend_test_framework')):
    os.environ['PATH'] += ":" + os.path.join(BASEDIR, 'tests')
    sys.path.insert(0, BASEDIR)

from depend_test_framework.case_generator import DependGraphCaseGenerator
from depend_test_framework.env import Env
from depend_test_framework.test_object import Action, CheckPoint, TestObject
from depend_test_framework.dependency import Provider, Consumer


@Action.decorator(1)
@Consumer.decorator('test.obj1', Consumer.REQUIRE)
@Provider.decorator('test.obj2', Provider.SET)
def mock_func1(params, env):
    pass


@Action.decorator(1)
@Provider.decorator('test.obj1', Provider.SET)
def mock_func2(params, env):
    pass


@Action.decorator(1)
@Provider.decorator('test.obj1', Provider.CLEAR)
def mock_func3(params, env):
    pass


@Action.decorator(1)
@Consumer.decorator('test.obj1', Consumer.REQUIRE)
@Consumer.decorator('test.obj2', Consumer.REQUIRE)
@Provider.decorator('test.obj3', Provider.SET)
def mock_func4(params, env):
    pass


@Action.decorator(1)
@Provider.decorator('test.obj2', Provider.CLEAR)
def mock_func5(params, env):
    pass


@Action.decorator(1)
@Consumer.decorator('test.obj3', Consumer.REQUIRE)
def mock_func6(params, env):
    pass


def test_gen_cases_method():
    test_funcs = [mock_func1, mock_func2, mock_func3, mock_func4, mock_func5, mock_func6]
    case_generator = DependGraphCaseGenerator()
    case_generator.gen_depend_map(test_funcs)

    cases = list(case_generator.gen_cases(mock_func4))
    assert len(cases) == 2
    for case in cases:
        e = Env()
        for step in case.steps:
            e = e.gen_transfer_env(step)
        result = e.gen_transfer_env(mock_func4)
        assert result.struct_table() == "{ test|False: { obj1|True: {}, obj2|True: {}, obj3|True: {},},}"

    cases = list(case_generator.gen_cases(mock_func6))
    assert len(cases) == 6


def test_gen_cases_special_method():
    test_funcs = [mock_func1, mock_func2, mock_func3, mock_func4, mock_func5, mock_func6]
    case_generator = DependGraphCaseGenerator()
    case_generator.gen_depend_map(test_funcs)

    src_env = Env()
    start_env = list(Env.gen_require_env(mock_func1))
    end_env = list(Env.gen_require_env(mock_func6))[0]
    cases = list(case_generator.gen_cases_special(src_env, start_env, end_env))
    assert len(cases) == 17
    for case in cases:
        e = Env()
        hit_start = 0
        for step in case.steps:
            e = e.gen_transfer_env(step)
            if e >= start_env[0]:
                hit_start += 1
        assert e >= end_env
        assert hit_start > 0


def test_mapping_perfermance():

    test_funcs = [mock_func1, mock_func2, mock_func3, mock_func4, mock_func5, mock_func6]
    g1 = DependGraphCaseGenerator()
    g1.gen_depend_map(test_funcs)
    g2 = DependGraphCaseGenerator(use_map=False)
    g2.gen_depend_map(test_funcs)

    with ResourceWatcher() as rw1:
        for _ in range(10):
            list(g1.gen_cases(mock_func6))

    with ResourceWatcher() as rw2:
        for _ in range(10):
            list(g2.gen_cases(mock_func6))

    # assert rw1.run_time < rw2.run_time
