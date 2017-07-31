"""
Test Engine
"""
import inspect
import itertools
import random
from collections import OrderedDict
from core import is_Action, is_CheckPoint, Container, is_Hybrid, Env, get_all_depend, Params, get_func_params_require, Provider, Consumer, TestObject, is_TestObject
from utils import pretty
from log import get_logger, prefix_logger
from algorithms import route_permutations

LOGGER = get_logger(__name__)


class Engine(object):
    def __init__(self, modules):
        self.modules = modules
        self.checkpoints = Container()
        self.actions = Container()
        self.hybrids = Container()
        self.env = Env()
        self.params = Params()

        def _handle_func(func, conatiner):
            if is_TestObject(func):
                inst_func = func()
                conatiner.add(inst_func)
            else:
                conatiner.add(func)

        for module in modules:
            for _, func in inspect.getmembers(module, is_Action):
                # TODO: remove dup code
                _handle_func(func, self.actions)
            for _, func in inspect.getmembers(module, is_CheckPoint):
                _handle_func(func, self.checkpoints)
            for _, func in inspect.getmembers(module, is_Hybrid):
                _handle_func(func, self.hybrids)

        self.dep_map = None

    def run(self):
        """
        need implement
        """
        raise NotImplementedError

    def compute_depend_items(self, func):
        """
        broken
        """
        pos_items = []
        requires = get_all_depend(func, depend_cls=Consumer)
        # print "requires of func %s : %s" % (func, requires)
        for require in requires:
            if self.env.hit_require(require):
                continue
            # print "try to find some func to fit require"
            funcs = self.get_all_depend_provider(require)
            cases = []
            for func in funcs:
                cases.extend(self.compute_depend_items(func))
            pos_items.append(cases)

        if not pos_items: 
            return [func]
        return list(itertools.product(*pos_items))

    def compute_steps_order(self, items):
        pass

    def compute_full_steps(self, steps):
        pass

    def compute_route_permutations(self, func, cleanup=False):
        target_env = Env.gen_require_env(func)
        if not self.dep_map:
            raise Exception('Need gen depend map first')
        if cleanup:
            routes = route_permutations(self.dep_map, target_env, self.env)
        else:
            routes = route_permutations(self.dep_map, self.env, target_env)
        ret_routes = []
        for route in routes:
            ret_routes.extend(itertools.product(*route))
        return ret_routes

    @property
    def all_funcs(self):
        return self.hybrids | self.checkpoints | self.actions

    def filter_func(self):
        # TODO
        need_remove = Container()
        for func in self.actions:
            param_req = get_func_params_require(func)
            if not param_req:
                continue
            if not self.params >= param_req.param_depend:
                LOGGER.info('Remove func ' + str(func))
                need_remove.add(func)
        self.actions -= need_remove

        need_remove = Container()
        for func in self.checkpoints:
            param_req = get_func_params_require(func)
            if not param_req:
                continue
            if not self.params >= param_req.param_depend:
                LOGGER.info('Remove func ' + str(func))
                need_remove.add(func)
        self.checkpoints -= need_remove

        need_remove = Container()
        for func in self.hybrids:
            param_req = get_func_params_require(func)
            if not param_req:
                continue
            if not self.params >= param_req.param_depend:
                LOGGER.info('Remove func ' + str(func))
                need_remove.add(func)
        self.hybrids -= need_remove

    def get_all_depend_provider(self, depend):
        providers = []
        if depend.type == Consumer.REQUIRE:
            req_types = [Provider.SET]
        elif depend.type == Consumer.REQUIRE_N:
            req_types = [Provider.CLEAR]
        else:
            return providers
        for func in self.actions:
            tmp_depends = get_all_depend(func, req_types, ret_list=False)
            if depend.env_depend in tmp_depends.keys():
                providers.append(func)
        return providers

    def find_checkpoints(self):
        ret = []
        for func in self.checkpoints:
            requires = get_all_depend(func, depend_cls=Consumer)
            if self.env.hit_requires(requires):
                ret.append(func)
        return ret

    def gen_depend_map(self):
        requires = Container()
        for func in self.actions|self.hybrids:
            tmp_requires = get_all_depend(func, [Provider.SET], depend_cls=Provider)
            requires |= Container(tmp_requires)

        nodes = []
        dep_map = {}
        for i in range(len(requires) + 1):
            nodes.extend(itertools.combinations(requires, i))

        for node in nodes:
            tmp_e = Env()
            tmp_e.set_from_depends(node)
            dep_map[tmp_e] = {}

        for func in self.actions|self.hybrids:
            for env_key in dep_map.keys():
                tmp_e = env_key.gen_transfer_env(func)
                if tmp_e is None:
                    continue
                data = dep_map[env_key]
                data.setdefault(tmp_e, []).append(func)
        LOGGER.debug(pretty(dep_map))
        self.dep_map = dep_map

    def replace_depend_with_param(self, depend):
        pass

    def get_all_depend_consumer(self, depend):
        consumers = []
        if depend.type == Provider.SET:
            req_types = [Consumer.REQUIRE]
        elif depend.type == Provider.CLEAR:
            req_types = [Consumer.REQUIRE_N]
        else:
            return consumers
        for func in self.actions:
            tmp_depends = get_all_depend(func, req_types, ret_list=False)
            if depend.env_depend in tmp_depends.keys():
                consumers.add(func)
        return consumers

    def run_one_case(self, func):
        func(self.params, self.env)
        self.env = self.env.gen_transfer_env(func)
        checkpoints = self.find_checkpoints()
        for checkpoint in checkpoints:
            checkpoint(self.params, self.env)

class Template(Engine):
    pass

class StaticTemplate(Template):
    pass

class MatrixTemplate(Template):
    pass

class Fuzz(Engine):
    pass

class AI(Engine):
    pass


class Demo(Engine):
    def __init__(self, basic_modules, test_modules=None, test_funcs=None):
        self.test_modules = test_modules
        self.test_funcs = test_funcs
        tmp_modules = []
        tmp_modules.extend(basic_modules)
        if self.test_modules:
            tmp_modules.extend(test_modules)
        super(Demo, self).__init__(tmp_modules)

    def run(self, params):
        self.params = params
        self.filter_func()
        self.gen_depend_map()

        tests = []
        if not self.test_modules and not self.test_funcs:
            raise Exception('Need give a test object !')
        if self.test_modules:
            test_funcs = []
            for module in self.test_modules:
                for _, func in inspect.getmembers(module, (is_Action, is_Hybrid)):
                    test_funcs.add(func)
        else:
            test_funcs = self.test_funcs

        while test_funcs:
            # TODO
            self.env = Env()

            test_case = OrderedDict()
            order = []
            test_func = random.choice(test_funcs)
            test_funcs.remove(test_func)

            LOGGER.info("=" * 8 + " %s " % test_func.func_name + "=" * 8)
            LOGGER.info("")
            cases = self.compute_route_permutations(test_func)
            cleanup = self.compute_route_permutations(test_func, True)
            i = 1
            for case in cases:
                # TODO
                self.env = Env()

                LOGGER.info("=" * 8 + " case %d " % i + "=" * 8)
                for func in case:
                    self.run_one_case(func)
                self.run_one_case(test_func)
                i += 1
                if not cleanup:
                    LOGGER.info("no clean up")
                else:
                    cleanup_case = random.choice(cleanup)
                    for func in cleanup_case:
                        func(self.params, self.env)
                        self.env = self.env.gen_transfer_env(func)
                LOGGER.info("Current Env: %s", self.env)
                LOGGER.info("")
