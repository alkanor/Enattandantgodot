"""
For any non directed graph, define the closure method

It expects:
 * a non directed graph as first argument
 * as well as an origin node
 * and an optional depth (if < 0, will yield all the reachable nodes from the provided one)
"""


def recursive_traversal(self, basenode, depth=-1, bfs=True, state=None, base_depth=-1, return_origin=False):
    if not depth:
        yield basenode
        return
    if state is None:
        state = set()
        #state.add(basenode)
    if bfs and (return_origin or base_depth == depth):
        yield basenode
    for node, edgeval in self._Graph__per_node[basenode]+self._Graph__reverse_per_node[basenode]:  # trickery to access "private like" member of Graph (called from this dynamically added func)
        if node not in state:
            state.add(node)
            yield from recursive_traversal(self, node, depth - 1, bfs, state, base_depth, return_origin)
    if not bfs and (return_origin or base_depth == depth):
        yield basenode


def iterative_traversal(self, basenode, max_depth=-1, bfs=True, return_origin=False):
    stack = [(basenode, 0)]
    traversed = set()
    while stack:
        node, depth = stack.pop() if not bfs else stack.pop(0)
        if depth <= max_depth or max_depth < 0:
            if depth > 0 or return_origin:
                yield node
            for child, edgeval in self._Graph__per_node[node]+self._Graph__reverse_per_node[basenode]:  # trickery to access "private like" member of Graph (called from this dynamically added func)
                if child not in traversed:
                    stack.append((child, depth+1))
                    traversed.add(child)


def bfs(self, basenode, depth=-1, direction=True):
    return iterative_traversal(self, basenode, depth, True)

def dfs(self, basenode, depth=-1, direction=True):
    return iterative_traversal(self, basenode, depth, False)


# expecting the graph to not be directed
def closure(self, node, depth=-1):
    assert node in self._Graph__nodes, "Expecting the origin node for ancestors to be in the graph nodes"  # trickery to access "private like" member of Graph (called from this dynamically added func)
    yield from bfs(self, node, depth, False)


def direct_neighbors_size(self, node):
    return len(set(map(lambda x: x[0], self._Graph__per_node.get(node, [])+self._Graph__reverse_per_node.get(node, []))))  # trickery to access "private like" member of Graph (called from this dynamically added func)