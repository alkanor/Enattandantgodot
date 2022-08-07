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


def acyclic_oriented_constraint(current_graph, elements_to_add=None):
    assert type(current_graph) == Graph, "Expected a graph for 1st argument of acyclic_constraint"
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
                yield from current_graph.iterate()
                yield from elements_to_add
            new_graph = Graph.reconstruct(full_graph_generator)
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


def acyclic_non_oriented_constraint(current_graph, elements_to_add=None):
    assert type(current_graph) == Graph, "Expected a graph for 1st argument of acyclic_constraint"
    match elements_to_add:
        case current_graph.__nodetype__():                 # passed argument is node
            return True
        case current_graph.__edgetype__():                 # passed argument is edge
            for descendant in elements_to_add.child.bfs(): # non oriented implies bfs
                if descendant == elements_to_add.parent:
                    return False
            return True
        case object(__iter__=_):  # iterable
            def full_graph_generator():
                yield from current_graph.iterate()
                yield from elements_to_add
            new_graph = Graph.reconstruct(full_graph_generator)
            return acyclic_non_oriented_constraint(new_graph)
        case None:  # check the current graph is acyclic
            pass


weakly_connected_constraint
strongly_connected_constraint
connected_constraint
max_parents_per_vertice_constraint(1)
parents_per_vertice_constraint(1)
max_children_per_vertice_constraint(2)
max_vertice_degree_constraint(1)
