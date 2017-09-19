import itertools
from log import get_logger, prefix_logger

LOGGER = get_logger(__name__)


def route_permutations(graph, start, target,
                       trace=None, history=None, pb=None,
                       allow_dep=None, dep=None):
    routes = []
    nodes_map = graph[start]

    if not trace:
        new_trace = set([start])
    else:
        new_trace = set(trace)
        new_trace.add(start)

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
        if node in new_trace:
            continue
        if node in history.keys():
            ret = history[node]
        else:
            if node == target:
                routes.append([opaque])
                continue
            else:
                ret = route_permutations(graph,
                    node, target, new_trace, history,
                    pb, allow_dep, dep)
        if ret:
            for sub_route in ret:
                tmp_route = [opaque]
                tmp_route.extend(sub_route)
                routes.append(tmp_route)

    del(new_trace)
    history[start] = routes
    if pb:
        pb.update(len(history) + 1)
    # LOGGER.info("Trace: %s", trace)
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
