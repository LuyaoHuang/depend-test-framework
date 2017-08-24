"""
Test Engine
"""
import inspect
import itertools
import random
from collections import OrderedDict
from core import is_Action, is_CheckPoint, Container, is_Hybrid, Env, get_all_depend, Params, get_func_params_require, Provider, Consumer, TestObject, is_TestObject, MistDeadEndException, MistClearException
from utils import pretty
from log import get_logger, prefix_logger, get_file_logger, make_timing_logger
from algorithms import route_permutations
from case import Case

LOGGER = get_logger(__name__)
time_log = make_timing_logger(LOGGER)


class Engine(object):
    def __init__(self, modules, doc_modules):
        self.modules = modules
        self.doc_modules = doc_modules
        self.checkpoints = Container()
        self.actions = Container()
        self.hybrids = Container()
        # TODO: not use dict
        self.doc_funcs = {}
        self.env = Env()
        self.params = Params()
        self.dep_map = None

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

        # TODO: maybe we should allow the same name func
        for module in self.doc_modules:
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if name in self.doc_funcs.keys():
                    raise Exception("Use the same func %s in the module %s" % (name, module.__name__))
                self.doc_funcs[name] = func

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

    def find_suit_envs(self, env, dep=None):
        if not self.dep_map:
            raise Exception('Need gen depend map first')
        for key_env in self.dep_map.keys():
            if env <= key_env:
                if dep and (len(key_env) - len(env)) > dep:
                    continue
                yield key_env

    def compute_route_permutations(self, target_env, cleanup=False, src_env=None):
        if not self.dep_map:
            raise Exception('Need gen depend map first')
        base_env = src_env if src_env else self.env
        if cleanup:
            routes = route_permutations(self.dep_map, target_env, base_env)
        else:
            routes = route_permutations(self.dep_map, base_env, target_env)
        ret_routes = []
        for route in routes:
            ret_routes.extend(itertools.product(*route))
        return ret_routes

    @property
    def all_funcs(self):
        return self.hybrids | self.checkpoints | self.actions

    def _cb_filter_with_param(self, func):
        param_req = get_func_params_require(func)
        if not param_req:
            return False
        if not self.params >= param_req.param_depend:
            return True
        else:
            return False

    def filter_all_func_custom(self, cb):
        self.filter_func_custom(self.actions, cb)
        self.filter_func_custom(self.checkpoints, cb)
        self.filter_func_custom(self.hybrids, cb)

    def filter_func_custom(self, container, cb):
        need_remove = Container()
        for func in container:
            if cb(func):
                LOGGER.debug('Remove func ' + str(func))
                need_remove.add(func)
        container -= need_remove

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
        LOGGER.info('Depend map is %d x %d size',
                    len(dep_map), len(dep_map))
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

    def full_logger(self, msg):
        #TODO
        LOGGER.info(msg)
        self.params.doc_logger.info(msg)

    def _check_mists(self, mists, env, func):
        if not mists:
            return
        for mist in mists:
            if mist.reach(env, func):
                return mist

    def gen_one_step_doc(self, func, step_index=None, check=False, mists=None):
        if getattr(func, '__name__', None):
            doc_func_name = func.__name__
        else:
            doc_func_name = func.__class__.__name__

        if step_index is not None:
            #TODO: move doc_logger definition in basic engine
            self.params.doc_logger.info('%d.\n' % step_index)
            step_index += 1

        if doc_func_name not in self.doc_funcs.keys():
            self.params.doc_logger.info("Not define %s name in doc modules" % doc_func_name)
        doc_func = self.doc_funcs[doc_func_name]

        mist = self._check_mists(mists, self.env, func)
        if mist:
            if mist.__doc__:
                self.params.doc_logger.info("Desciption: %s" % mist.__doc__)
            # TODO: here will raise a exception which require the caller handle this
            try:
                mist(doc_func, self.params, self.env)
            except MistClearException:
                mists.remove(mist)
            # TODO: mist in the mist
            ret = None
        else:
            if doc_func.__doc__:
                self.params.doc_logger.info("Desciption: %s" % doc_func.__doc__)

            ret = doc_func(self.params, self.env)
        self.env = self.env.gen_transfer_env(func)
        LOGGER.debug("Env: %s, func: %s", self.env, func)

        if ret and mists is not None:
            LOGGER.info('Add a new mist')
            mists.append(ret)

        if not check or is_CheckPoint(func):
            return step_index

        checkpoints = self.find_checkpoints()
        for i, checkpoint in enumerate(checkpoints):
            step_index = self.gen_one_step_doc(checkpoint,
                step_index=step_index, mists=mists)

        return step_index

    def run_one_step(self, func, check=True, doc=False):
        # TODO: merge this method and find_all_way_to_target to one method
        with prefix_logger(LOGGER, "\033[94mAction:\033[0m", new_name=func.__module__):
            # TODO
            if is_TestObject(func):
                func = func()

            if func.__doc__:
                self.full_logger("Desciption: %s" % func.__doc__)
            func(self.params, self.env)
        self.env = self.env.gen_transfer_env(func)
        LOGGER.debug("Env: %s, func: %s", self.env, func)
        if not check:
            return
        checkpoints = self.find_checkpoints()
        for i, checkpoint in enumerate(checkpoints):
            with prefix_logger(LOGGER, "\033[92mCheckpoint%s:\033[0m" % str(i+1),
                               new_name=checkpoint.__module__):
                if checkpoint.__doc__:
                    self.full_logger("Desciption: %s" % checkpoint.__doc__)
                checkpoint(self.params, self.env)

    def find_all_way_to_target(self, target_env, random_cleanup=True):
        for tgt_env in self.find_suit_envs(target_env, 2):
            cases = self.compute_route_permutations(tgt_env)
            cleanups = self.compute_route_permutations(tgt_env, True)
            if cleanups:
                if random_cleanup:
                    cleanup_steps = random.choice(cleanups)
                else:
                    # TODO use the shortest way
                    raise NotImplementedError
            else:
                cleanup_steps = None

            LOGGER.debug("env: %s case num: %d" % (tgt_env, len(cases)))
            for case in cases:
                case_obj = Case(case, tgt_env=tgt_env,
                                cleanups=cleanup_steps)
                yield case_obj


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
    def __init__(self, basic_modules, test_modules=None,
                 test_funcs=None, doc_modules=None):
        self.test_modules = test_modules
        self.test_funcs = test_funcs
        tmp_modules = []
        tmp_modules.extend(basic_modules)
        if self.test_modules:
            tmp_modules.extend(test_modules)
        super(Demo, self).__init__(tmp_modules, doc_modules)

    def _prepare_test_funcs(self):
        if not self.test_modules and not self.test_funcs:
            raise Exception('Need give a test object !')
        if self.test_modules:
            test_funcs = []
            for module in self.test_modules:
                for _, func in inspect.getmembers(module, (is_Action, is_Hybrid)):
                    test_funcs.add(func)
        else:
            test_funcs = self.test_funcs
        return test_funcs

    def _excute_test(self, test_func):
        if getattr(test_func, 'func_name', None):
            title = getattr(test_func, 'func_name')
        else:
            title = str(test_func)

        self.full_logger("=" * 8 + " %s " % title + "=" * 8)
        self.full_logger("")
        target_env = Env.gen_require_env(test_func)
        i = 1
        for tgt_env in self.find_suit_envs(target_env, 2):
            cases = self.compute_route_permutations(tgt_env)
            cleanup = self.compute_route_permutations(tgt_env, True)
            for case in cases:
                # TODO
                self.full_logger("=" * 8 + " case %d " % i + "=" * 8)
                for func in case:
                    self.run_one_step(func)
                self.run_one_step(test_func)
                i += 1
                if not cleanup:
                    LOGGER.info("Cannot find clean up way")
                else:
                    cleanup_case = random.choice(cleanup)
                    for func in cleanup_case:
                        self.run_one_step(func, False)
                LOGGER.info("Current Env: %s", self.env)
                LOGGER.info("")
                self.env = Env()

    def _gen_test_case_doc(self, test_func, need_cleanup=False, full_matrix=True):
        if getattr(test_func, 'func_name', None):
            title = getattr(test_func, 'func_name')
        else:
            title = str(test_func)

        self.full_logger("=" * 8 + " %s " % title + "=" * 8)
        self.full_logger("")
        target_env = Env.gen_require_env(test_func)
        i = 1
        with time_log('Compute case permutations'):
            case_matrix = list(self.find_all_way_to_target(target_env))

        if not full_matrix:
            LOGGER.info('Find %d route, and use the shortest one', len(case_matrix))
            case = min(case_matrix)
            case_matrix = [case]

        while case_matrix:
            case = case_matrix.pop()
            step_index = 1
            mists = []
            self.full_logger("=" * 8 + " case %d " % i + "=" * 8)
            try:
                for func in case.steps:
                    step_index = self.gen_one_step_doc(func,
                        step_index=step_index, mists=mists)
                step_index = self.gen_one_step_doc(test_func,
                    step_index=step_index, check=True, mists=mists)
            except MistDeadEndException:
                # TODO: maybe need clean up
                pass
            else:
                if need_cleanup:
                    if not case.cleanups:
                        LOGGER.info("Cannot find clean up way")
                        LOGGER.info("Current Env: %s", self.env)
                    else:
                        for func in case.clean_ups:
                            step_index = self.run_one_step(func, step_index=step_index)
            i += 1
            self.env = Env()

    def run(self, params, doc_file=None):
        self.params = params
        LOGGER.debug(self.params.pretty_display())
        # TODO
        self.params.logger = LOGGER
        doc_path = 'doc.file' if not doc_file else doc_file
        self.params.doc_logger = get_file_logger(doc_path, doc_path)
        self.filter_all_func_custom(self._cb_filter_with_param)
        with time_log('Gen the depend map'):
            self.gen_depend_map()

        tests = []
        test_funcs = self._prepare_test_funcs()

        while test_funcs:
            # TODO
            self.env = Env()

            test_case = []
            order = []
            test_func = random.choice(test_funcs)
            test_funcs.remove(test_func)
            if self.params.test_case:
                self._gen_test_case_doc(test_func, full_matrix=self.params.full_matrix)
            else:
                self._excute_test(test_func)

        LOGGER.info('Write all case to %s', doc_path)
        LOGGER.info('')
