"""
Helper classes to help generate case
"""

import itertools
import random
import copy

from progressbar import ProgressBar, SimpleProgress, Counter, Timer

from .log import get_logger
from .env import Env
from .utils import pretty
from .case import Case
from .algorithms import route_permutations

LOGGER = get_logger(__name__)


class DependGraphCaseGenerator(object):
    """
    Case generator which use a directed graph to describe
    the dependency of the work items
    """
    def __init__(self, suit_env_limit=20, allow_dep=8, use_map=True):
        self.dep_graph = None
        self._allow_dep = allow_dep
        self._suit_env_limit = suit_env_limit

        # graph objs mapping
        self._use_map = use_map
        self._nodes_map = []
        self._edge_map = []
        self._v_graph = None

    def find_suit_envs(self, env):
        env_list = env if type(env) is list else [env]
        if not self.dep_graph:
            raise Exception('Need gen depend graph first')
        env_record = []
        for tmp_env in env_list:
            tmp_list = []
            for key_env in self.dep_graph.keys():
                if tmp_env <= key_env:
                    tmp_list.append(key_env)

            for i, tgt_env in enumerate(sorted(tmp_list, key=len)):
                if i <= self._suit_env_limit and tgt_env not in env_record:
                    env_record.append(tgt_env)
                    yield tgt_env

    def compute_route_permutations(self, src_env, target_env, cleanup=False):
        if not self.dep_graph:
            raise Exception('Need gen depend graph first')

        LOGGER.info("Compute route from %s to %s", src_env, target_env)
        # TODO encapsulation the ProgressBar in utils
        widgets = ['Processed: ', Counter(), ' of %d (' % len(self.dep_graph), Timer(), ')']
        pbar = ProgressBar(widgets=widgets, maxval=len(self.dep_graph)).start()
        graph = self._v_graph if self._use_map else self.dep_graph
        src_node = self._nodes_map.index(src_env) if self._use_map else src_env
        tgt_node = self._nodes_map.index(target_env) if self._use_map else target_env
        if cleanup:
            routes = route_permutations(graph, tgt_node, src_node, pb=pbar, allow_dep=self._allow_dep)
        else:
            routes = route_permutations(graph, src_node, tgt_node, pb=pbar, allow_dep=self._allow_dep)
        pbar.finish()

        ret_routes = []
        for route in routes:
            ret_routes.extend(itertools.product(*route))
        return ret_routes

    def gen_cases(self, test_func, random_cleanup=False, need_cleanup=False, src_env=None):
        if not src_env:
            src_env = Env()
        target_env = list(Env.gen_require_env(test_func))
        for tgt_env in self.find_suit_envs(target_env):
            cases = self.compute_route_permutations(src_env, tgt_env)
            if not tgt_env.gen_transfer_env(test_func):
                LOGGER.info('Cannot use env %s for testing', tgt_env)
                continue

            if need_cleanup:
                new_tgt_env = tgt_env.gen_transfer_env(test_func)
                cleanup_steps = self.gen_cleanups(new_tgt_env, src_env, random_cleanup)
            else:
                cleanup_steps = None

            LOGGER.debug("env: %s case num: %d" % (tgt_env, len(cases)))
            for case in cases:
                tmp_case = self.restore_onigin_data(case)
                case_obj = Case(tmp_case, tgt_env=tgt_env,
                                cleanups=cleanup_steps)
                yield case_obj

    def gen_cleanups(self, src_env, tgt_env, random_cleanup=False):
        cleanups = self.compute_route_permutations(tgt_env, src_env, True)
        if cleanups:
            if random_cleanup:
                cleanup_steps = random.choice(cleanups)
            else:
                cleanup_steps = min(cleanups, key=len)
            return self.restore_onigin_data(cleanup_steps)

    def gen_cases_special(self, src_env, start_env, end_env):
        """
        Support find cases reach mutli target env
        """
        # TODO: this is tied to mist to close
        for tgt_start_env in self.find_suit_envs(start_env):
            if tgt_start_env == src_env:
                cases = None
            else:
                cases = self.compute_route_permutations(src_env, tgt_start_env)
                if not cases:
                    continue
            for tgt_end_env in self.dep_graph[tgt_start_env].keys():
                if end_env <= tgt_end_env:
                    funcs = self.dep_graph[tgt_start_env][tgt_end_env]
                    if cases:
                        for data in itertools.product(cases, funcs):
                            case = list(data[0])
                            case = self.restore_onigin_data(case)

                            case.append(data[1])
                            case_obj = Case(case, tgt_env=tgt_end_env)
                            yield case_obj
                    else:
                        for func in funcs:
                            case_obj = Case([func], tgt_env=tgt_end_env)
                            yield case_obj

    def gen_multi_test_objects_cases(self, test_funcs, random_cleanup=False, need_cleanup=False, src_env=None, no_extra=True):
        # TODO: merge this method with gen_cases
        if src_env is None:
            src_env = Env()

        rets = list()
        def _find_next_steps(int_test_funcs, cur_env, exist_steps, old_env):
            if int_test_funcs:
                test_func = int_test_funcs[0]
                rest_func = int_test_funcs[1:]
                new_env = cur_env.gen_transfer_env(test_func)
                if no_extra and new_env is not None:
                    # this means current env is okay
                    # python3: new_exist_steps = exist_steps.copy()
                    new_exist_steps = copy.deepcopy(exist_steps)
                    new_exist_steps.append(test_func)
                    _find_next_steps(rest_func, new_env, new_exist_steps, cur_env)
                else:
                    # sigh, need find a route
                    target_env = list(Env.gen_require_env(test_func))
                    for tgt_env in self.find_suit_envs(target_env):
                        steps_list = self.compute_route_permutations(cur_env, tgt_env)
                        new_env = tgt_env.gen_transfer_env(test_func)
                        if not new_env:
                            # BUG: this should not happen
                            LOGGER.info('Cannot use env %s for testing', tgt_env)
                            continue
                        for steps in steps_list:
                            # python3: new_exist_steps = exist_steps.copy()
                            new_exist_steps = copy.deepcopy(exist_steps)
                            new_exist_steps.extend(steps)
                            new_exist_steps.append(test_func)
                            _find_next_steps(rest_func, new_env, new_exist_steps, tgt_env)
            else:
                # this is the end of the test_funcs
                # drop last test func
                final_steps = exist_steps[:-1]
                if need_cleanup:
                    cleanup_steps = self.gen_cleanups(cur_env, src_env, random_cleanup)
                else:
                    cleanup_steps = None
                # pass old_env since we drop last test func
                rets.append((final_steps, old_env, cleanup_steps))

        _find_next_steps(test_funcs, src_env, [], None)
        for steps, tgt_env, cleanup_steps in rets:
            tmp_case = self.restore_onigin_data(steps)
            case_obj = Case(tmp_case, tgt_env=tgt_env,
                            cleanups=cleanup_steps)
            yield case_obj

    def gen_depend_map(self, test_funcs, drop_env=None, start_node=None):
        dep_graph = {}
        if not start_node:
            start_node = Env()
        dep_graph.setdefault(start_node, {})
        nodes = [start_node]
        widgets = ['Processed: ', Counter(), ' nodes (', Timer(), ')']
        LOGGER.info("Start gen depend map...")
        try:
            pbar = ProgressBar(widgets=widgets, max_value=100000)
        except TypeError:
            # python3 ProgressBar
            pbar = ProgressBar(widgets=widgets, maxval=100000)
        pbar.start()
        while nodes:
            node = nodes.pop()
            LOGGER.debug('Start check node %s', node)
            for func in test_funcs:
                new_node = node.gen_transfer_env(func)
                LOGGER.debug('posible New Node: %s func: %s', new_node, func)
                if new_node is None:
                    continue
                if drop_env and len(new_node) > drop_env:
                    continue
                if new_node not in dep_graph.keys():
                    LOGGER.debug('New Node: %s func: %s', new_node, func)
                    dep_graph.setdefault(new_node, {})
                    nodes.append(new_node)
                data = dep_graph[node]
                data.setdefault(new_node, set())
                data[new_node].add(func)
            pbar.update(len(dep_graph))

        LOGGER.debug(pretty(dep_graph))
        LOGGER.info('Depend map is %d x %d size',
                    len(dep_graph), len(dep_graph))
        self.dep_graph = dep_graph
        if self._use_map:
            self.build_graph_map()

    def build_graph_map(self):
        if not self.dep_graph:
            return

        self._nodes_map = list(self.dep_graph.keys())
        v_graph = {}

        for node in self._nodes_map:
            sub_map = {}
            for tgt_node, datas in self.dep_graph[node].items():
                tmp_datas = set()
                for data in datas:
                    if data not in self._edge_map:
                        self._edge_map.append(data)
                    tmp_datas.add(self._edge_map.index(data))
                sub_map[self._nodes_map.index(tgt_node)] = tmp_datas
            v_graph[self._nodes_map.index(node)] = sub_map

        self._v_graph = v_graph

    def restore_onigin_data(self, datas):
        if self._use_map:
            return [self._edge_map[data] if type(data) is int else data for data in datas]
        else:
            return datas

    def save_dep_graph(self, path=None):
        raise NotImplementedError

    def load_dep_graph(self, path=None):
        raise NotImplementedError
