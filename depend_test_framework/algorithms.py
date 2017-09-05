import itertools
from log import get_logger, prefix_logger
from utils import ProgressBar

LOGGER = get_logger(__name__)

def route_permutations(graph, start, target, trace=None, history=None):
    routes = []
    nodes_map = graph[start]

    if not trace:
        new_trace = set([start])
    else:
        new_trace = set(trace)
        new_trace.add(start)

    if history is None:
        history = {}

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
                ret = route_permutations(graph, node, target, new_trace, history)
        if ret:
            for sub_route in ret:
                tmp_route = [opaque]
                tmp_route.extend(sub_route)
                routes.append(tmp_route)

    history[start] = routes
    ProgressBar.next_step(len(history), len(graph))
    # LOGGER.info("Trace: %s", trace)
    # LOGGER.info("Map: %s", nodes_map)
    # LOGGER.info("Start: %s", start)
    # LOGGER.info("routes: %s", routes)
    return routes

class hashable_list(list):
    def __hash__(self):
        return hash(str(self))

def unit_test():
    G = {'s': {'u':10, 'x':5},
         'u': {'v':1, 'x':2},
         'v': {'y':4},
         'x': {'u':3,'v':9,'y':2},
         'y': {'s':7,'v':6}}
    LOGGER.info(route_permutations(G, 's', 'u'))
    LOGGER.info(route_permutations(G, 'x', 'y'))

if __name__ == '__main__':
    unit_test()
