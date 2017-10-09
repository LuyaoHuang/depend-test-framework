"""
Helper classes to help generate case
"""

import itertools
from progressbar import ProgressBar, SimpleProgress, Counter, Timer

from log import get_logger
from utils import pretty
from algorithms import route_permutations

LOGGER = get_logger(__name__)


class DependGraphCaseGenerator(object):
    """
    Case generator which use a directed graph to describe
    the dependency of the work items
    """
    def __init__(self):
        self.dep_graph = None

    def find_suit_envs(self, env, dep=None):
        if not self.dep_graph:
            raise Exception('Need gen depend graph first')
        tmp_list = []
        for key_env in self.dep_graph.keys():
            if env <= key_env:
                tmp_list.append(key_env)

        for i, tgt_env in enumerate(sorted(tmp_list, key=len)):
            if i <= dep:
                yield tgt_env

    def compute_route_permutations(self, src_env, target_env, cleanup=False):
        if not self.dep_graph:
            raise Exception('Need gen depend graph first')

        LOGGER.info("Compute route from %s to %s", src_env, target_env)
        # TODO encapsulation the ProgressBar in utils
        widgets = ['Processed: ', Counter(), ' of %d (' % len(self.dep_graph), Timer(), ')']
        pbar = ProgressBar(widgets=widgets, maxval=len(self.dep_graph)).start()
        if cleanup:
            routes = route_permutations(self.dep_graph, target_env, src_env, pb=pbar, allow_dep=8)
        else:
            routes = route_permutations(self.dep_graph, src_env, target_env, pb=pbar, allow_dep=8)
        pbar.finish()

        ret_routes = []
        for route in routes:
            ret_routes.extend(itertools.product(*route))
        return ret_routes

    def gen_depend_map(self, start_node, test_funcs, drop_env=None):
        dep_graph = {}
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
