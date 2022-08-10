
"""
Base Graph object, which will be the core of many other ones

It is composed of:
 * a node base type  X
 * a node type       N<X>
 * an edge base type Y
 * an edge type      E<N<X>, Y>
 * some constraint that will be fulfilled at anytime (example: acyclic graph)

3 base functions can be called to create some data:
 * add_node (waiting for an element of exact type X) -> will create N<X>
 * add_edge (waiting for two elements of type N<X> and an element of type Y) -> will create E<N<X>, Y>
 * add_child (waiting for a Node<X> and an element of exact type X) -> will create N<X> et E<N<X>, Y>

2 base functions can be called to remove some data:
 * del_node (waiting for an element of exact type N<X>) -> will delete N<X> and all related edges
 * del_edge (waiting for an element of exact type E<N<X>, Y>) -> will delete the edge E<N<X>, Y>

Same functions are defined for iterable instead of alone elements.

The following functions are added to dump and load graphs:
 * iterate -> yield X, Y, properties, then all nodes then edges of the graph
 * reconstruct -> consumes X, Y, (properties), and all graph elements that must have type N<X> or E<N<X>, Y>

All other functions will be defined according to graph properties: most of them are only coherent in case of properties
being satisfied (cf. graph_constraints.py and graph_property.py)

"""

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


    def del_edge(self, edge):
        self.check_constraints(Graph.del_edge.__name__, edge)
        pass

    def del_node(self, node):
        self.check_constraints(Graph.del_node.__name__, node)
        pass


    def iterate(self):
        pass

    @staticmethod
    def reconstruct(check=False):
        pass


from .graph_properties_constraints import GraphPropertyConstraints  # to dispose of the properties constraint that depends on Graph without circular dependancy

