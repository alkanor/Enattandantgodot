"""
For any non directed graph, define the closure method

It expects:
 * a non directed graph as first argument
 * as well as an origin node
 * and an optional depth (if < 0, will yield all the reachable nodes from the provided one)
"""


def recursive_traversal(self, basenode, depth=-1, bfs=True, state=None):
    if not depth:
        yield basenode
        return
    if state is None:
        state = set()
        state.add(basenode)
    if bfs:
        yield basenode
    for node, edgeval in self._Graph__per_nodes[basenode]+self._Graph__reverse_per_node[basenode]:  # trickery to access "private like" member of Graph (called from this dynamically added func)
        if node not in state:
            state.add(node)
            yield from recursive_traversal(self, node, depth - 1, bfs, state)
    if not bfs:
        yield basenode


def bfs(self, basenode, depth=-1, direction=True):
    return recursive_traversal(self, basenode, depth, direction, True)

def dfs(self, basenode, depth=-1, direction=True):
    return recursive_traversal(self, basenode, depth, direction, False)


# expecting the graph to not be directed
def closure(self, node, depth=-1):
    assert node in self._Graph__nodes, "Expecting the origin node for ancestors to be in the graph nodes"  # trickery to access "private like" member of Graph (called from this dynamically added func)
    yield from bfs(self, node, depth, False)


def direct_neighbors_size(self, node):
    return len(set(map(lambda x: x[0], self._Graph__per_nodes.get(node, [])+self._Graph__reverse_per_node.get(node, []))))  # trickery to access "private like" member of Graph (called from this dynamically added func)