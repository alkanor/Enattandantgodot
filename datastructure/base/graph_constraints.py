from .graph import Graph


'''
Graph constraints currently supported:
 * Acyclic graph
 * Strongly / Weakly (for oriented graph) connected graph
 * Connected (for non oriented graph) graph
 * Parent / children constraints (max or exact)

The API is the following:
 * All (un-parametrized) constraints are waiting for a graph as first argument
 * If no additional argument are given, the passed graph will be checked against the constraint
 * Otherwise, the second argument can be one of the following:
    ** Graph node type
    ** Graph edge type
    ** Iterable of graph node or edge types
'''


class BadConstraintArgument(Exception):
    def __init__(self, *args):
        super().__init__(f"Bad constraint argument {args}")


def assert_first_arg_is_graph_decorator(f):
    def sub(arg1, *args):
        assert isinstance(arg1, Graph), f"Expected a graph for 1st argument of {f.__name__}"
        return f(arg1, *args)
    return sub


def construct_default_behavior(nodetype_match=None, edgetype_match=None, iterable=None):
    def decorator(f):
        
    return decorator


@assert_first_arg_is_graph_decorator
def acyclic_oriented_constraint(current_graph, elements_to_add=None):
    match elements_to_add:
        case current_graph.__nodetype__():                         # passed argument is node -> nothing to check
            return True
        case current_graph.__edgetype__():                         # passed argument is edge -> if target has children,
            for descendant in elements_to_add.child.descendants(): # oriented implies descendants
                if descendant == elements_to_add.parent:
                    return False
            return True
        case object(__iter__=_):                                   # iterable -> recreate the full graph and check the overall acyclic property
            def full_graph_generator():
                yield current_graph.__nodetype__
                yield current_graph.__edgetype__
                yield from current_graph.iterate()
                yield from elements_to_add
            new_graph = Graph.reconstruct(full_graph_generator, properties=(GraphProperty.Oriented,), check=False)
            return acyclic_oriented_constraint(new_graph)
        case None:                                                 # check the current graph is acyclic
            traveled_nodes = set()
            nodes_from_root = [node for node in current_graph.nodes if len(node.ancestors(1)) == 0]   # oriented implies ancestors
            if not nodes_from_root and len(current_graph.edges()): # we have no node without parent and some edges -> implies cycle
                return False
            while nodes_from_root:
                current_node = nodes_from_root.pop(0)
                traveled_nodes.add(current_node)
                for child in current_node.descendants(1):          # oriented implies descendants
                    if child in traveled_nodes:                    # if we come back on an already traveled node, we have a cycle
                        return False
                    nodes_from_root.append(child)
            return True
        case _:
            raise BadConstraintArgument(type(elements_to_add))


@assert_first_arg_is_graph_decorator
def acyclic_non_oriented_constraint(current_graph, elements_to_add=None):
    match elements_to_add:
        case current_graph.__nodetype__():                     # passed argument is node
            return True
        case current_graph.__edgetype__():                     # passed argument is edge
            for descendant in elements_to_add.child.closure(): # non oriented implies closure (should be a bfs)
                if descendant == elements_to_add.parent:
                    return False
            return True
        case object(__iter__=_):  # iterable
            def full_graph_generator():
                yield current_graph.__nodetype__
                yield current_graph.__edgetype__
                yield from current_graph.iterate()
                yield from elements_to_add
            new_graph = Graph.reconstruct(full_graph_generator, properties=(GraphProperty.NonOriented,), check=False)
            return acyclic_non_oriented_constraint(new_graph)
        case None:  # check the current graph is acyclic
            traveled_nodes = set()
            nodes_from_root = [node for node in current_graph.nodes if len(node.closure(1)) == 1]   # if len(closure) == 1 it is a "root"
            if not nodes_from_root and len(current_graph.edges()): # we have no node with only one edge to another node and some edges -> implies cycle
                return False
            while nodes_from_root:
                current_node = nodes_from_root.pop(0)
                traveled_nodes.add(current_node)
                for child in current_node.closure(1):              # non oriented implies closure
                    if child in traveled_nodes:                    # if we come back on an already traveled node, we have a cycle
                        return False
                    nodes_from_root.append(child)
            return True


@assert_first_arg_is_graph_decorator
def weakly_connected_constraint(current_graph, elements_to_add=None):
    match elements_to_add:
        case current_graph.__nodetype__():                     # adding a node alone breaks connectivity
            return False
        case current_graph.__edgetype__():                     # adding an edge alone has no effect on connectivity if base graph already weakly connected
            return True
        case object(__iter__=_):  # iterable
            def full_graph_generator():
                yield current_graph.__nodetype__
                yield current_graph.__edgetype__
                yield from current_graph.iterate()
                yield from elements_to_add
            new_graph = Graph.reconstruct(full_graph_generator)
            return weakly_connected_constraint(new_graph)
        case None:                                             # check the current graph is weakly connected
            connected_per_node = {node: set([node]) for node in current_graph.nodes}
            for edge in current_graph.edges:
                connected_per_node[edge.parent] = connected_per_node[edge.parent].union(connected_per_node[edge.child])
                connected_per_node[edge.child] = connected_per_node[edge.parent]
                if len(connected_per_node[edge.parent]) == len(connected_per_node): # onlu one clique that gathers all, gg
                    return True
            return False


@assert_first_arg_is_graph_decorator
def strongly_connected_constraint(current_graph, elements_to_add=None):
    match elements_to_add:
        case current_graph.__nodetype__():                     # adding a node alone breaks connectivity
            return False
        case current_graph.__edgetype__():                     # adding an edge alone has no effect on connectivity if base graph already weakly connected
            return True
        case object(__iter__=_):  # iterable
            def full_graph_generator():
                yield current_graph.__nodetype__
                yield current_graph.__edgetype__
                yield from current_graph.iterate()
                yield from elements_to_add
            new_graph = Graph.reconstruct(full_graph_generator)
            return weakly_connected_constraint(new_graph)
        case None:                                             # check the current graph is strongly connected: check if all vertices can be accessed from
                                                               # an arbitrary vertice in graph and reverse graph
            nodes_set = set(current_graph.nodes)
            first_node = nodes_set.__iter__().__next__()
            traveled_nodes = set([first_node])
            for node in first_node.descendants():              # descendants exists because of strongly connected
                traveled_nodes.add(node)
            if len(traveled_nodes) != len(nodes_set):          # we did not even travel all nodes from our starting point, it can't be strongly connected
                return False

            def reverse_graph_generator():
                for elem in current_graph.iterate():
                    match elem:
                        case current_graph.__nodetype__():
                            return elem
                        case current_graph.__edgetype__():
                            return current_graph.__edgetype__(elem.child, elem.parent)

            reverse_graph = Graph.reconstruct(reverse_graph_generator) # TODO : fix problem with constraint that is not in constructed graph

            traveled_nodes = set([first_node])
            for node in reverse_graph.descendants(first_node):  # we take descendants from the reverse graph and not from nodes because linked to the base graph
                traveled_nodes.add(node)
            if len(traveled_nodes) != len(nodes_set):           # we did not travel all nodes from our starting point in reverse graph, it can't be strongly connected
                return False
            return True


@assert_first_arg_is_graph_decorator
def connected_constraint(current_graph, elements_to_add=None):
    return weakly_connected_constraint(current_graph, elements_to_add)


max_parents_per_vertice_constraint(1)
parents_per_vertice_constraint(1)
max_children_per_vertice_constraint(2)
max_vertice_degree_constraint(1)
