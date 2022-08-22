if __name__ == "__main__":
    #from .graph_constraints import acyclic_oriented_constraint, acyclic_non_oriented_constraint, \
    #    weakly_connected_constraint, strongly_connected_constraint, connected_constraint, \
    #    max_parents_per_vertice_constraint, parents_per_vertice_constraint, \
    #    max_children_per_vertice_constraint, \
    #    max_vertice_degree_constraint
    #from .graph import Graph

    #g = Graph(int, str)
    nodelist = [3, 4, 1, 3, 9, 12, 100, 435, 999]
    #nodes = [g.add_node(x) for x in nodelist]
    edgelist = [(0,1),(1,3),(3,5),(5,7),(7,6),(6,4),(4,1),(3,2),(2,0),(8,5)]
    #edges = [g.add_edge(nodes[a], nodes[b]) for a,b in edgelist]

    import graphviz

    Graphs = [
        ('sfdp_graph', graphviz.Graph(engine='sfdp')),
        ('fdp_graph', graphviz.Graph(engine='fdp')),
        ('sfdp_digraph', graphviz.Digraph(engine='sfdp')),
        ('fdp_digraph', graphviz.Digraph(engine='fdp')),
    ]

    for name, G in Graphs:
        nodes = [G.node(str(index), str(val)) for index, val in enumerate(nodelist)]
        edges = [G.edge(str(a), str(b)) for a, b in edgelist]

        print(G.source)
        G.format = 'svg'
        G.render(directory='doctest-output', view=True)

        input()
