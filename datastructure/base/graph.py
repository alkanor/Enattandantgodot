
@duplicate_methods_with_iterables({"child", "children"}, {"edge", "edges"}, {"node", "nodes"})
class Graph:

    def __init__(self, nodeType=None, edgeType=None, constraints=None):
        pass

    def add_child(self, base, child):
        self.check_constraints(Graph.add_child.__name__, base, child)
        pass

    def add_edge(self, edge):
        self.check_constraints(Graph.add_edge.__name__, edge)
        pass

    def add_node(self, node):
        self.check_constraints(Graph.add_ndoe.__name__, node)
        pass

    def del_child(self, base, child):
        self.check_constraints(Graph.del_child.__name__, base, child)
        pass

    def del_edge(self, edge):
        self.check_constraints(Graph.del_edge.__name__, edge)
        pass

    def del_node(self, node):
        self.check_constraints(Graph.del_node.__name__, node)
        pass


def connex(graph):
    reachable_nodes = {node: set(node) for node in graph.nodes}
    for edges in graph.edges:
