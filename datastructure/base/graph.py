
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


class Node:
    __slots__ = ['__value']

    def __init__(self, val=None):
        self.__value = val

    @property
    def nodeval(self):
        return self.__value

    @nodeval.setter
    def nodeval(self, val):
        assert type(val) == type(self.__value), "Node value type can't change once fixed"  # ensure the node type always remain the same
        self.__value = val


class Edge:
    __slots__ = ['__source', '__target', '__value']

    def __init__(self, source, target, val=None):
        self.__source = source
        self.__target = target
        self.__value = val

    @property
    def edgeval(self):
        return self.__value

    @edgeval.setter
    def edgeval(self, val):
        assert type(val) == type(self.__value), "Edge value type can't change once fixed"  # ensure the edge type always remain the same
        self.__value = val

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, val):
        raise AttributeError("Source node in a given edge is immutable")

    @property
    def target(self):
        return self.__source

    @target.setter
    def target(self, val):
        raise AttributeError("Target node in a given edge is immutable")



class ConstraintNotFulfilled(Exception):
    def __init__(self, constraint):
        super().__init__(f"Constraint {constraint} not fulfilled")


class Graph:

    def __init__(self, nodeType=None, edgeType=None, constraints=None):
        self.__nodetype = nodeType
        self.__edgetype = edgeType
        self.__constraints = constraints
        self.__nodes = set()
        self.__per_node = {}
        self.__reverse_per_node = {}


    def check_constraints(self, *args):
        for constraint in self.constraints:
            if not constraint(self, *args):
                raise ConstraintNotFulfilled(constraint)


    def check_node(self, node):
        assert type(node) == Node, "Expecting real node type as argument"
        assert not self.__nodetype or type(node.__value) == self.__nodetype, "Expecting node base type to be of type graph node type which is not none"

    def check_edge(self, edge):
        assert type(edge) == Edge, "Expecting real edge type as argument"
        assert not self.__edgetype or type(edge.__value) == self.__edgetype, "Expecting node base type to be of type graph edge type which is not none"
        # self.check_node(edge.source) # overkill because we check nodes are in nodes set
        # self.check_node(edge.target)  # overkill because we check nodes are in nodes set
        assert edge.source in self.__nodes, "Edge composed of nodes that are not in the graph node set (source)"
        assert edge.target in self.__nodes, "Edge composed of nodes that are not in the graph node set (target)"

    def check_target(self, target):
        assert not self.__nodetype or type(target) == self.__nodetype, "Expecting target to be of type graph node type or graph node type to be none"

    def check_edgeval(self, edgeval):
        assert not self.__edgetype or type(edgeval) == self.__edgetype, "Expecting edge value to be of type graph edge type or graph edge type to be none"



    def add_child(self, base, childval=None, edgeval=None):
        self.check_node(base)
        self.check_target(childval)
        self.check_edgeval(edgeval)

        node = Node(childval if self.__nodetype else None)
        edge = Edge(base, node, edgeval)
        self.check_constraints(Graph.add_child.__name__, [node, edge])

        self.__nodes.add(node)
        self.__per_node.setdefault(base, []).append((node, edgeval))
        self.__reverse_per_node.setdefault(node, []).append((base, edgeval))
        return node


    def add_edge(self, edge):
        self.check_edge(edge)
        self.check_constraints(Graph.add_edge.__name__, edge)

        self.per_node.setdefault(edge.source, []).append((edge.target, edge.__value))
        self.reverse_per_node.setdefault(edge.target, []).append((edge.source, edge.__value))


    def add_link(self, source, target, edgeval=None): # same that add_edge but with no edge struct
        self.check_node(source)
        self.check_node(target)
        assert source in self.__nodes, "Attempt to add an edge composed of nodes that are not in the graph node set (source)"
        assert target in self.__nodes, "Attempt to add an edge composed of nodes that are not in the graph node set (target)"

        edge = Edge(source, target, edgeval)
        self.check_constraints(Graph.add_edge.__name__, edge)

        self.per_node.setdefault(source, []).append((target, edgeval))
        self.reverse_per_node.setdefault(target, []).append((source, edgeval))
        return edge


    def add_node(self, nodeval):
        self.check_target(nodeval)

        node = Node(nodeval if self.__nodetype else None)
        self.check_constraints(Graph.add_ndoe.__name__, node)

        self.__nodes.add(node)
        return node


    def del_edge(self, edge):
        self.check_edge(edge)
        assert edge.source in self.__per_node, "Edge source to delete is not in current graph edges"
        assert edge.target in self.__reverse_per_node, "Edge target to delete is not in current graph edges"
        self.check_constraints(Graph.del_edge.__name__, edge)

        previous_size = len(self.__per_node[edge.source])
        previous_size_rev = len(self.__reverse_per_node[edge.target])
        self.__per_node[edge.source] = [(node, edgeval) for node, edgeval in self.__per_node[edge.source] if
                                            node != edge.target or (edge.edgeval is not None and edge.edgeval != edgeval)]
        self.__reverse_per_node[edge.target] = [(node, edgeval) for node, edgeval in self.__reverse_per_node[edge.target] if
                                                    node != edge.source or (edge.edgeval is not None and edge.edgeval == edgeval)]
        new_size = len(self.__per_node[edge.source])
        new_size_rev = len(self.__reverse_per_node[edge.target])
        assert new_size-previous_size == new_size_rev-previous_size_rev, \
            f"Major symetry issue during edge deletion {new_size-previous_size} edges removed in base and {new_size_rev-previous_size_rev} edges removed in reverse"

        return new_size-previous_size


    def del_node(self, node):
        self.check_node(node)
        assert node in self.__nodes, "Node to delete not in graph nodes"
        self.check_constraints(Graph.del_node.__name__, node)

        to_remove = self.__per_node.get(node, None)
        if to_remove:
            n_removed = 0
            for linked, _ in to_remove:
                prev_size = len(self.__reverse_per_node[linked])
                self.__reverse_per_node[linked] = [(n, e) for n, e in self.__reverse_per_node[linked] if n != node]
                new_size = len(self.__reverse_per_node[linked])
                n_removed += prev_size - new_size
            assert n_removed == len(to_remove), f"Major symetry issue during node deletion {n_removed} edges removed instead of {len(to_remove)} expected"
            self.__per_node.remove(node)
        self.__nodes.remove(node)




    def add_children(self, base, children_edgevals):
        self.check_node(base)
        nodevals_and_edgevals = list(children_edgevals)  # handle generator
        for child, edgeval in nodevals_and_edgevals:
            self.check_target(child)
            self.check_edgeval(edgeval)
        nodes = [Node(child if self.__nodetype else None) for child, _ in nodevals_and_edgevals]
        edges = [Edge(base, node, edgeval) for node, (_, edgeval) in zip(nodes, nodevals_and_edgevals)]

        self.check_constraints(Graph.add_child.__name__, [nodes, edges])

        self.__nodes.update(set(nodes))
        self.__per_node.setdefault(base, []).extend([(node, edgeval) for node, (_, edgeval) in zip(nodes, nodevals_and_edgevals)])
        for node, (_, edgeval) in zip(nodes, nodevals_and_edgevals):
            self.__reverse_per_node.setdefault(node, []).append((base, edgeval))
        return nodes


    def add_edges(self, edges):
        edges_list = list(edges)  # handle generator
        for edge in edges_list:
            self.check_edge(edge)
        self.check_constraints(Graph.add_edge.__name__, edges_list)

        for edge in edges_list:
            self.per_node.setdefault(edge.source, []).append((edge.target, edge.__value))
            self.reverse_per_node.setdefault(edge.target, []).append((edge.source, edge.__value))
        return edges_list


    def add_links(self, sources_targets_edgevals): # same that add_edge but with no edge struct
        sources_targets_edgevals_list = list(sources_targets_edgevals)  # handle generator
        for source, target, edgeval in sources_targets_edgevals_list:
            self.check_node(source)
            self.check_node(target)
            assert source in self.__nodes, "Attempt to add an edge composed of nodes that are not in the graph node set (source)"
            assert target in self.__nodes, "Attempt to add an edge composed of nodes that are not in the graph node set (target)"

        edges = [Edge(source, target, edgeval) for source, target, edgeval in sources_targets_edgevals_list]
        self.check_constraints(Graph.add_edge.__name__, edges)

        for source, target, edgeval in sources_targets_edgevals_list:
            self.per_node.setdefault(source, []).append((target, edgeval))
            self.reverse_per_node.setdefault(target, []).append((source, edgeval))
        return edges


    def add_nodes(self, nodevals):
        nodevals_list = list(nodevals)  # handle generator
        for nodeval in nodevals_list:
            self.check_target(nodeval)

        nodes = [Node(nodeval if self.__nodetype else None) for nodeval in nodevals_list]
        self.check_constraints(Graph.add_ndoe.__name__, nodes)

        self.__nodes.update(nodes)
        return nodes


    def del_edges(self, edges):
        edges_list = list(edges)  # handle generator
        for edge in edges_list:
            self.check_edge(edge)
            assert edge.source in self.__per_node, "Edge source to delete is not in current graph edges"
            assert edge.target in self.__reverse_per_node, "Edge target to delete is not in current graph edges"
        self.check_constraints(Graph.del_edge.__name__, edges_list)

        per_source = {}
        per_target = {}
        for edge in edges_list:
            per_source.setdefault(edge.source, []).append((edge.target, edge.edgeval))
            per_target.setdefault(edge.target, []).append((edge.source, edge.edgeval))

        previous_size = 0
        new_size = 0
        for source in per_source:
            previous_size += len(self.__per_node[source])
            self.__per_node[source] = [(node, edgeval) for node, edgeval in self.__per_node[source] if
                                           (node, edgeval) not in per_source[source]
                                           and
                                           (node, None) not in per_source[source]
                                       ]
            new_size += len(self.__per_node[source])

        previous_size_rev = 0
        new_size_rev = 0
        for target in per_target:
            previous_size_rev += len(self.__reverse_per_node[target])
            self.__reverse_per_node[target] = [(node, edgeval) for node, edgeval in self.__reverse_per_node[target] if
                                                   (node, edgeval) not in per_target[target]
                                                   and
                                                   (node, None) not in per_target[target]
                                               ]
            new_size_rev += len(self.__reverse_per_node[target])

        assert new_size-previous_size == new_size_rev-previous_size_rev, \
            f"Major symetry issue during edge deletion {new_size-previous_size} edges removed in base and {new_size_rev-previous_size_rev} edges removed in reverse"

        return new_size-previous_size


    def del_nodes(self, nodes):
        nodes_set = set(nodes)  # handle generator
        for node in nodes_set:
            self.check_node(node)
            assert node in self.__nodes, "Node to delete not in graph nodes"
        self.check_constraints(Graph.del_node.__name__, nodes_set)

        to_remove_lists = [(node, self.__per_node[node]) for node in nodes_set if node in self.__per_node]
        if to_remove_lists:
            accumulated = {}
            n_to_remove = 0
            for node, to_remove in to_remove_lists:
                n_to_remove += len(to_remove)
                for linked, _ in to_remove:
                    accumulated.setdefault(linked, set()).add(node)
            n_removed = 0
            for linked in accumulated:
                prev_size = len(self.__reverse_per_node[linked])
                self.__reverse_per_node[linked] = [(n, e) for n, e in self.__reverse_per_node[linked] if n not in accumulated[linked]]
                new_size = len(self.__reverse_per_node[linked])
                n_removed += prev_size - new_size
            assert n_removed == n_to_remove, f"Major symetry issue during node deletion {n_removed} edges removed instead of {n_to_remove} expected"
            for node, _ in to_remove_lists:
                self.__per_node.remove(node)
        self.__nodes.difference_update(node)



    def iterate(self):
        yield self.__nodetype
        yield self.__edgetype
        yield from self.__nodes
        for node in self.__per_node:
            yield from [Edge(node, target, edgeval) for target, edgeval in self.__per_node[node]]

    """
    Reconstructing a graph:
     * graph_generator must return all nodes and edges of the graph to reconstruct
     * additional_properties are used to augment the graph with functions related to properties
     * check will check constraints regarding additional_properties if true
    """
    @staticmethod
    def reconstruct(graph_generator, additional_properties=None, check=False):
        pass


def full_graph_generator():
    yield current_graph.__nodetype__
    yield current_graph.__edgetype__
    yield from current_graph.iterate()
    yield from elements_to_add


new_graph = Graph.reconstruct(full_graph_generator(), properties=iterable_property, check=False)

from .graph_properties_constraints import GraphPropertyConstraints  # to dispose of the properties constraint that depends on Graph without circular dependancy

