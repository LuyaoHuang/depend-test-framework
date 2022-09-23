"""
Some small algorithms
"""

from depend_test_framework.log import get_logger

LOGGER = get_logger(__name__)


def route_permutations(graph, start, target, history=None, pb=None,
                       allow_dep=None, dep=None, sr_graph=None,
                       edge_trace=None, node_trace=None):
    """
    Help to compute all the permutations of the way in the graph
    TODO: Use some package which related to graph based machine learning
    """
    routes = []
    nodes_map = graph[start]

    if not node_trace:
        new_node_trace = [start]
    else:
        new_node_trace = list(node_trace)
        new_node_trace.append(start)

    if history is None:
        history = {}

    # TODO better way to limit the table
    if allow_dep:
        dep = dep or 0
        if dep >= allow_dep:
            return routes
        else:
            dep += 1

    for node, opaque in nodes_map.items():
        fin_node = node

        if not edge_trace:
            tmp_edge_trace = [opaque]
        else:
            tmp_edge_trace = list(edge_trace)
            tmp_edge_trace.append(opaque)

        if node in sr_graph:
            for new_node, sr in sr_graph[node].items():
                if sr.check_require(new_node_trace, tmp_edge_trace):
                    fin_node = new_node
                    break

        if fin_node in new_node_trace:
            continue
        if fin_node in history.keys():
            ret = history[fin_node]
        else:
            if fin_node == target:
                routes.append([opaque])
                continue
            else:
                ret = route_permutations(graph,
                    fin_node, target, history,
                    pb, allow_dep, dep, sr_graph,
                    tmp_edge_trace, new_node_trace)
        if ret:
            for sub_route in ret:
                tmp_route = [opaque]
                tmp_route.extend(sub_route)
                routes.append(tmp_route)

    del(new_node_trace)
    if not sr_graph:
        # Cannot use history when there are special routes
        history[start] = routes
        if pb:
            pb.update(len(history))
    # LOGGER.info("Node Trace: %s", node_trace)
    # LOGGER.info("Map: %s", nodes_map)
    # LOGGER.info("Start: %s", start)
    # LOGGER.info("routes: %s", routes)
    return routes


class hashable_list(list):
    def __hash__(self):
        return hash(str(self))


def unit_test():
    G = {'s': {'u': 10, 'x': 5},
         'u': {'v': 1, 'x': 2},
         'v': {'y': 4},
         'x': {'u': 3, 'v': 9, 'y': 2},
         'y': {'s': 7, 'v': 6}}
    LOGGER.info(route_permutations(G, 's', 'u'))
    LOGGER.info(route_permutations(G, 'x', 'y'))


if __name__ == '__main__':
    unit_test()
