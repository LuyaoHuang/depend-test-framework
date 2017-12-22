"""
Helper classes to help generate case
"""

import itertools
import random
from progressbar import ProgressBar, SimpleProgress, Counter, Timer

from log import get_logger
from env import Env
from utils import pretty
from case import Case
from algorithms import route_permutations

LOGGER = get_logger(__name__)


class DependGraphCaseGenerator(object):
    """
    Case generator which use a directed graph to describe
    the dependency of the work items
    """
    def __init__(self, suit_env_limit=20, allow_dep=8):
        self.dep_graph = None
        self._allow_dep = allow_dep
        self._suit_env_limit = suit_env_limit

    def find_suit_envs(self, env):
        if not self.dep_graph:
            raise Exception('Need gen depend graph first')
        tmp_list = []
        for key_env in self.dep_graph.keys():
            if env <= key_env:
                tmp_list.append(key_env)

        for i, tgt_env in enumerate(sorted(tmp_list, key=len)):
            if i <= self._suit_env_limit:
                yield tgt_env

    def compute_route_permutations(self, src_env, target_env, cleanup=False):
        if not self.dep_graph:
            raise Exception('Need gen depend graph first')

        LOGGER.info("Compute route from %s to %s", src_env, target_env)
        # TODO encapsulation the ProgressBar in utils
        widgets = ['Processed: ', Counter(), ' of %d (' % len(self.dep_graph), Timer(), ')']
        pbar = ProgressBar(widgets=widgets, maxval=len(self.dep_graph)).start()
        if cleanup:
            routes = route_permutations(self.dep_graph, target_env, src_env, pb=pbar, allow_dep=self._allow_dep)
        else:
            routes = route_permutations(self.dep_graph, src_env, target_env, pb=pbar, allow_dep=self._allow_dep)
        pbar.finish()

        ret_routes = []
        for route in routes:
            ret_routes.extend(itertools.product(*route))
        return ret_routes

    def gen_cases(self, test_func, random_cleanup=True, need_cleanup=False, src_env=None):
        if not src_env:
            src_env = Env()
        target_env = Env.gen_require_env(test_func)
        for tgt_env in self.find_suit_envs(target_env):
            cases = self.compute_route_permutations(src_env, tgt_env)
            cleanup_steps = None
            if need_cleanup:
                cleanups = self.compute_route_permutations(src_env, tgt_env, True)
                if cleanups:
                    if random_cleanup:
                        cleanup_steps = random.choice(cleanups)
                    else:
                        cleanup_steps = min(cleanups)

            LOGGER.debug("env: %s case num: %d" % (tgt_env, len(cases)))
            for case in cases:
                case_obj = Case(case, tgt_env=tgt_env,
                                cleanups=cleanup_steps)
                yield case_obj

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
                            case.append(data[1])
                            case_obj = Case(case, tgt_env=tgt_end_env)
                            yield case_obj
                    else:
                        for func in funcs:
                            case_obj = Case([func], tgt_env=tgt_end_env)
                            yield case_obj

    def gen_depend_map(self, test_funcs, drop_env=None, start_node=None):
        dep_graph = {}
        if not start_node:
            start_node = Env()
        dep_graph.setdefault(start_node, {})
        nodes = [start_node]
        widgets = ['Processed: ', Counter(), ' nodes (', Timer(), ')']
        LOGGER.info("Start gen depend map...")
        pbar = ProgressBar(widgets=widgets, max_value=100000)
        pbar.start()
        while nodes:
            node = nodes.pop()
            for func in test_funcs:
                new_node = node.gen_transfer_env(func)
                if new_node is None:
                    continue
                if drop_env and len(new_node) > drop_env:
                    continue
                if new_node not in dep_graph.keys():
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

    def save_dep_graph(self, path=None):
        raise NotImplementedError

    def load_dep_graph(self, path=None):
        raise NotImplementedError
