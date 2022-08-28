if __name__ == "__main__":
    from .graph_property import GraphProperty
    from .graph import Graph, Edge

    g = Graph(int, None, (GraphProperty.Directed,))
    nodelist = [3, 4, 1, 5, 9, 12, 100, 435, 999]
    nodes = [g.add_node(x) for x in nodelist]
    edgelist = [(0, 1), (1, 3), (3, 5), (5, 7), (7, 6), (6, 4), (4, 1), (3, 2), (2, 0), (8, 5)]
    edges = [g.add_link(nodes[a], nodes[b]) for a, b in edgelist]

    g2 = Graph(int, None, (GraphProperty.NonDirected,))
    nodes2 = [g2.add_node(x) for x in nodelist]
    edges2 = [g2.add_link(nodes2[a], nodes2[b]) for a, b in edgelist]


    from datastream.from_graph.to_graphviz import Graph_to_graphviz
    from datastream.from_graphviz.to_fs import Graphviz_to_fs

    #Graphviz_to_fs(Graph_to_graphviz(g), 'doctest-output/output', True)
    Graphviz_to_fs(Graph_to_graphviz(g), 'doctest-output/output_directed')
    Graphviz_to_fs(Graph_to_graphviz(g2), 'doctest-output/output_nondirected')

    from .graph_constraints import acyclic_directed_constraint, acyclic_non_directed_constraint, \
        weakly_connected_constraint, strongly_connected_constraint, connected_constraint, \
        max_parents_per_vertice_constraint, parents_per_vertice_constraint, \
        max_children_per_vertice_constraint, \
        max_vertice_degree_constraint

    T = {
        GraphProperty.Directed: [
            (acyclic_directed_constraint, "acyclic_directed_constraint"),
            (weakly_connected_constraint, "weakly_connected_constraint"),
            (strongly_connected_constraint, "strongly_connected_constraint"),
            (max_parents_per_vertice_constraint(1), "max_parents_per_vertice_constraint(1)"),
            (max_parents_per_vertice_constraint(2), "max_parents_per_vertice_constraint(2)"),
            (parents_per_vertice_constraint(2), "parents_per_vertice_constraint(2)"),
            (max_children_per_vertice_constraint(1), "max_children_per_vertice_constraint(1)"),
            (max_children_per_vertice_constraint(2), "max_children_per_vertice_constraint(2)"),
        ],
        GraphProperty.NonDirected: [
            (acyclic_non_directed_constraint, "acyclic_non_directed_constraint"),
            (connected_constraint, "connected_constraint"),
            (max_vertice_degree_constraint(2), "max_vertice_degree_constraint(2)"),
            (max_vertice_degree_constraint(3), "max_vertice_degree_constraint(3)"),
        ],
    }

    print("Directed")
    for func, name in T[GraphProperty.Directed]:
        print(name)
        print(func(g))

    print("For non directed")
    for func, name in T[GraphProperty.NonDirected]:
        print(name)
        print(func(g2))

    print("\nthen with 12 -> 999 -> strongly connected")
    g.add_link(nodes[5], nodes[8])
    print(g.edges_number())
    print(strongly_connected_constraint(g))

    print("\nthen without 4 -> 5 -> not connected at all")
    g.del_edge(Edge(nodes[1], nodes[3]))
    print(g.edges_number())
    print(strongly_connected_constraint(g))
    print(weakly_connected_constraint(g))
    Graphviz_to_fs(Graph_to_graphviz(g), 'doctest-output/output_directed2')

    print("\nthen back to normal")
    g.del_edge(Edge(nodes[5], nodes[8]))
    print(g.edges_number())
    print(strongly_connected_constraint(g))

    print("\nadding node")
    g.add_node(1298)
    print(weakly_connected_constraint(g))