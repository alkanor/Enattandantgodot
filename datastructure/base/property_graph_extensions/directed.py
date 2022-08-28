"""
For any directed graph, define ancestors and descendants methods

These expect:
 * a directed graph as first argument
 * as well as an origin node
 * and an optional depth (if < 0, will yield all the reachable nodes from the provided one)
"""


def recursive_traversal(self, basenode, depth=-1, direction=True, bfs=True, state=None):
    if not depth:
        yield basenode
        return
    if state is None:
        state = set()
        state.add(basenode)
    if bfs:
        yield basenode
    for node, edgeval in self._Graph__per_node[basenode] if direction else self._Graph__reverse_per_node[basenode]: # trickery to access "private like" member of Graph (called from this dynamically added func)
        if node not in state:
            state.add(node)
            yield from recursive_traversal(self, node, depth - 1, direction, bfs, state)
    if not bfs:
        yield basenode


def bfs(self, basenode, depth=-1, direction=True):
    return recursive_traversal(self, basenode, depth, direction, True)

def dfs(self, basenode, depth=-1, direction=True):
    return recursive_traversal(self, basenode, depth, direction, False)


# expecting the graph to be directed
def ancestors(self, node, depth=-1):
    assert node in self._Graph__nodes, "Expecting the origin node for ancestors to be in the graph nodes"   # trickery to access "private like" member of Graph (called from this dynamically added func)
    yield from bfs(self, node, depth, False)

def descendants(self, node, depth=-1):
    assert node in self._Graph__nodes, "Expecting the origin node for descendants to be in the graph nodes"   # trickery to access "private like" member of Graph (called from this dynamically added func)
    yield from bfs(self, node, depth, True)


def children_number(self, node):
    return len(set(map(lambda x: x[0], self._Graph__per_nodes.get(node, [])))) # trickery to access "private like" member of Graph (called from this dynamically added func)

def parents_number(self, node):
    return len(set(map(lambda x: x[0], self._Graph__reverse_per_node.get(node, []))))  # trickery to access "private like" member of Graph (called from this dynamically added func)
