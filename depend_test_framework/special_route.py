"""
Special Route classes
"""

from .log import get_logger

LOGGER = get_logger(__name__)


class BaseSpecialRoute(object):
    def compute_target_node(self, src_node):
        raise NotImplementedError

    def check_require(self, prev_nodes=None, prev_edges=None):
        raise NotImplementedError

    def update_params(self, edge_map, node_map):
        raise NotImplementedError


def is_SpecialRoute(obj):
    return isinstance(obj, BaseSpecialRoute)


class EdgeRequireRoute(BaseSpecialRoute):
    def __init__(self, prev_edges, extra_provider):
        self.prev_edges = prev_edges
        self._extra_provider = extra_provider
        raise NotImplementedError("This Special Route have a bug and cannot be used")

    def compute_target_node(self, src_node):
        tmp_node = src_node
        for func in self.prev_edges:
            tmp_node = tmp_node.gen_transfer_env(func)
            if not tmp_node:
                return
        old_node = tmp_node.copy()
        self._extra_provider.effect_env(tmp_node)
        return old_node, tmp_node

    def update_params(self, edge_map, node_map):
        self.prev_edges = [edge_map.index(edge) for edge in self.prev_edges]

    def check_require(self, prev_nodes=None, prev_edges=None):
        # TODO: BUG: prev_edges is a struct like this [{1}, {3, 0}]
        #            that make this method cannot be implemented
        if not prev_edges:
            return False
        if len(prev_edges) < len(self.prev_edges):
            return False
        return prev_edges[len(prev_edges) - len(self.prev_edges):] == self.prev_edges


class NodeRequireRoute(BaseSpecialRoute):
    def __init__(self, prev_node_requires, extra_provider):
        # prev_node_requires: [[req1, req2], [req3, req4]]
        self._prev_node_requires = prev_node_requires
        self._extra_provider = extra_provider
        self._node_map = None

    def compute_target_node(self, src_node):
        new_node = src_node.copy()
        self._extra_provider.effect_env(new_node)
        return src_node, new_node

    def update_params(self, edge_map, node_map):
        self._node_map = node_map

    def check_require(self, prev_nodes=None, prev_edges=None):
        if not prev_nodes:
            return False
        if len(prev_nodes) < len(self._prev_node_requires):
            return False
        tmp_list = prev_nodes[len(prev_nodes) - len(self._prev_node_requires):]
        for i, node_id in enumerate(tmp_list):
            node = self._node_map[node_id] if type(node_id) is int else node_id
            reqs = self._prev_node_requires[i]
            if not node.hit_requires(reqs):
                return False

        return True
