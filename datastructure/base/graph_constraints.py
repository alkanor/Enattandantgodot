from .graph_property import GraphProperty
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


def construct_default_behavior(nodetype_match=None, edgetype_match=None, iterable=None, iterable_property=None):
    def decorator(f):
        def sub(current_graph, elements_to_add=None):
            match elements_to_add:
                case current_graph.__nodetype__():
                    if nodetype_match == True:
                        return True
                    elif nodetype_match == False:
                        return False
                    return f(current_graph, elements_to_add)
                case current_graph.__edgetype__():
                    if edgetype_match == True:
                        return True
                    elif edgetype_match == False:
                        return False
                    return f(current_graph, elements_to_add)
                case object(__iter__=_):  # iterable -> recreate the full graph and check the overall acyclic property
                    if iterable == True:
                        return True
                    elif iterable == False:
                        return False
                    elif iterable == "fullgraph_check":
                        def full_graph_generator():
                            yield current_graph.__nodetype__
                            yield current_graph.__edgetype__
                            yield from current_graph.iterate()
                            yield from elements_to_add
                        new_graph = Graph.reconstruct(full_graph_generator(), properties=iterable_property, check=False)
                        return f(new_graph)
                    return f(current_graph, elements_to_add)
                case None:
                    return f(current_graph)
                case _:
                    raise BadConstraintArgument(type(elements_to_add))
        return sub
    return decorator


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=True, iterable="fullgraph_check", iterable_property=(GraphProperty.Oriented,))
def acyclic_oriented_constraint(current_graph, elements_to_add=None):
    match elements_to_add:
        case current_graph.__edgetype__():                         # passed argument is edge -> if target has children,
            for descendant in elements_to_add.target.descendants(): # oriented implies descendants
                if descendant == elements_to_add.source:
                    return False
            return True
        case None:                                                 # check the current graph is acyclic
            nodes_from_root = [(node, set()) for node in current_graph.nodes() if len(node.ancestors(1)) == 0]   # oriented implies ancestors
            if not nodes_from_root and len(current_graph.edges()):   # we have no node without parent and some edges -> implies cycle (easy check)
                return False

            while nodes_from_root:
                current_node, path_from_base = nodes_from_root.pop(0)
                set_cpy = set(path_from_base)
                set_cpy.add(current_node)
                for child in current_node.descendants(1):          # oriented implies descendants
                    if child in path_from_base:                    # if we come back on an already traveled node from the base, we have a cycle
                        return False
                    nodes_from_root.append((child, set_cpy))
            return True
        case _:
            raise Exception(f"Should not happen, error within construct_default_behavior in acyclic_oriented_constraint")


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=True, iterable="fullgraph_check", iterable_property=(GraphProperty.NonOriented,))
def acyclic_non_oriented_constraint(current_graph, elements_to_add=None):
    match elements_to_add:
        case current_graph.__edgetype__():                     # passed argument is edge
            for descendant in elements_to_add.target.closure(): # non oriented implies closure (should be a bfs)
                if descendant == elements_to_add.source:
                    return False
            return True
        case None:  # check the current graph is acyclic
            if len(current_graph.edges()) >= len(current_graph.nodes()): # at least one cycle if n_edges >= n_vertices
                return False

            connected_per_node = {node: set([node]) for node in current_graph.nodes()}
            for edge in current_graph.edges():
                base_size = len(connected_per_node[edge.source])
                connected_per_node[edge.source] = connected_per_node[edge.source].union(connected_per_node[edge.target])
                if base_size == len(connected_per_node[edge.source]):    # if size did not increase, we have a cycle
                    return False
                connected_per_node[edge.target] = connected_per_node[edge.source]
            return True
        case _:
            raise Exception(f"Should not happen, error within construct_default_behavior in acyclic_non_oriented_constraint")


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=False, edgetype_match=True, iterable="fullgraph_check", iterable_property=(GraphProperty.Oriented,)) # adding a node alone breaks connectivity
                                                                                                                                                # adding an edge alone has no effect on connectivity if base graph already weakly connected
def weakly_connected_constraint(current_graph, elements_to_add=None):
    assert elements_to_add==None, "elements_to_add not None should not happen in weakly_connected_constraint with decorator"
    connected_per_node = {node: set([node]) for node in current_graph.nodes()}
    for edge in current_graph.edges():
        connected_per_node[edge.source] = connected_per_node[edge.source].union(connected_per_node[edge.target])
        connected_per_node[edge.target] = connected_per_node[edge.source]
        if len(connected_per_node[edge.source]) == len(connected_per_node):             # onlu one clique that gathers all, gg
            return True
    return False


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=False, edgetype_match=True, iterable="fullgraph_check", iterable_property=(GraphProperty.Oriented,)) # adding a node alone breaks connectivity
                                                                                                                                                # adding an edge alone has no effect on connectivity if base graph already strongly connected
def strongly_connected_constraint(current_graph, elements_to_add=None):
    assert elements_to_add == None, "elements_to_add not None should not happen in strongly_connected_constraint with decorator"

    nodes_set = set(current_graph.nodes())
    first_node = nodes_set.__iter__().__next__()
    traveled_nodes = set([first_node])
    for node in first_node.descendants():              # descendants exists because of strongly connected -> oriented
        traveled_nodes.add(node)
    if len(traveled_nodes) != len(nodes_set):          # we did not even travel all nodes from our starting point, it can't be strongly connected
        return False

    def reverse_graph_generator():
        for elem in current_graph.iterate():
            match elem:
                case current_graph.__edgetype__():
                    yield current_graph.__edgetype__(elem.target, elem.source)
                case _:        # should be current_graph.__nodetype__ or current_graph.__edgetype__ or current_graph.__nodetype__()
                    yield elem

    reverse_graph = Graph.reconstruct(reverse_graph_generator, properties=(GraphProperty.Oriented,), check=False)

    traveled_nodes = set([first_node])
    for node in first_node.descendants():
        traveled_nodes.add(node)
    if len(traveled_nodes) != len(nodes_set):           # we did not travel all nodes from our starting point in reverse graph, it can't be strongly connected
        return False
    return True


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=False, edgetype_match=True, iterable="fullgraph_check", iterable_property=(GraphProperty.NonOriented,))
def connected_constraint(current_graph, elements_to_add=None):
    assert elements_to_add==None, "elements_to_add not None should not happen in connected_constraint with decorator"
    connected_per_node = {node: set([node]) for node in current_graph.nodes()}
    for edge in current_graph.edges():
        connected_per_node[edge.source] = connected_per_node[edge.source].union(connected_per_node[edge.target])
        connected_per_node[edge.target] = connected_per_node[edge.source]
        if len(connected_per_node[edge.source]) == len(connected_per_node):             # onlu one clique that gathers all, gg
            return True
    return False


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=True)
def max_parents_per_vertice_constraint(max_parents):
    def sub(current_graph, elements_to_add=None):
        match elements_to_add:
            case current_graph.__edgetype__():                      # passed argument is edge
                parents = elements_to_add.target.ancestors(1)        # parent implies oriented so ancestors
                if elements_to_add.source in parents:
                    return True
                elif len(parents) + 1 > max_parents:
                    return False
                return True
            case object(__iter__=_):
                parents_per_child = {}
                for obj in elements_to_add:
                    if type(obj) == current_graph.__edgetype__:
                        if obj.target in parents_per_child:
                            parents_per_child[obj.target].add(obj.source)
                        else:
                            parents_per_child[obj.target] = set(obj.source)
                    else:
                        assert type(obj) == current_graph.__nodetype__, f"Waiting for a nodetype {current_graph.__nodetype__} while itering"

                for node in current_graph.nodes():
                    if node in parents_per_child:
                        parents_per_child[node].update(node.ancestors(1))

                for node in parents_per_child:
                    if len(parents_per_child[node]) > max_parents:
                        return False
                return True
            case None:
                for node in current_graph.nodes():
                    if len(node.ancestors(1)) > max_parents:
                        return False
                return True
            case _:
                raise Exception(
                    f"Should not happen, error within construct_default_behavior in max_parents_per_vertice_constraint")
    return sub


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=False, edgetype_match=False, iterable="fullgraph_check", iterable_property=(GraphProperty.Oriented,))
def parents_per_vertice_constraint(exact_parents):
    def sub(current_graph, elements_to_add=None):
        assert elements_to_add==None, "elements_to_add not None should not happen in parents_per_vertice_constraint with decorator"
        for node in current_graph.nodes():
            if len(node.ancestors(1)) != exact_parents:
                return False
        return True
    return sub


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=True, iterable="fullgraph_check", iterable_property=(GraphProperty.Oriented,))
def max_children_per_vertice_constraint(max_children):
    def sub(current_graph, elements_to_add=None):
        match elements_to_add:
            case current_graph.__edgetype__():  # passed argument is edge
                base_node = elements_to_add.source
                children = set(base_node.descendants(1))
                if elements_to_add.target in children:
                    return True
                if len(children) + 1 > max_children:
                    return False
                return True
            case None:
                for node in current_graph.nodes():
                    if len(node.descendants(1)) > max_children:
                        return False
                return True
            case _:
                raise Exception(
                    f"Should not happen, error within construct_default_behavior in max_children_per_vertice_constraint")
    return sub


@assert_first_arg_is_graph_decorator
@construct_default_behavior(nodetype_match=True, iterable="fullgraph_check", iterable_property=(GraphProperty.NonOriented,))
def max_vertice_degree_constraint(max_neighbours):
    def sub(current_graph, elements_to_add=None):
        match elements_to_add:
            case current_graph.__edgetype__():  # passed argument is edge
                base_node1 = elements_to_add.source
                children1 = set(base_node1.closure(1))
                base_node2 = elements_to_add.target
                children2 = set(base_node2.closure(1))
                if elements_to_add.target in children1:
                    assert elements_to_add.source in children2, "Should really never happen, closure are supposed to be reflexive"
                    return True                 # already an edge between base_node1 and base_node2
                if len(children1) + 1 > max_neighbours:
                    return False
                if len(children2) + 1 > max_neighbours:
                    return False
                return True
            case None:
                for node in current_graph.nodes():
                    if len(node.closure(1)) > max_neighbours:
                        return False
                return True
            case _:
                raise Exception(
                    f"Should not happen, error within construct_default_behavior in max_vertice_degree_constraint")
    return sub
