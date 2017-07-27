import itertools
from log import get_logger, prefix_logger

LOGGER = get_logger(__name__)

def route_permutations(graph, start, target, trace=None):
    routes = []
    # routes = {}
    nodes_map = graph[start]
    if not trace:
        trace = set([start])
    else:
        trace.add(start)
    # LOGGER.info("Trace: ", trace)
    # LOGGER.info("Target: ", target)
    # LOGGER.info("Map: ", nodes_map)
    for node, opaque in nodes_map.items():
        if trace and node in trace:
            continue
        if node == target:
            # LOGGER.info("route: ", route)
            routes.append([opaque])
            # routes.extend(route)
            # routes[route] = True
        else:
            ret = route_permutations(graph, node, target, trace)
            if ret:
                #LOGGER.info(list(itertools.product([opaque], ret)))
                #routes.extend(itertools.product([opaque], ret))
                for sub_route in ret:
                    tmp_route = [opaque]
                    tmp_route.extend(sub_route)
                    routes.append(tmp_route)
                # routes[route] = ret
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
