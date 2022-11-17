from persistent.datastructure.list import LIST

if __name__ == "__main__":
    from .graph_property import GraphProperty
    from .graph import Graph, Edge, Node, ConstraintNotFulfilled

    g = Graph(int, None, (GraphProperty.Directed,))
    nodelist = [3, 4, 1, 5, 9, 12, 100, 435, 999]
    nodes = [g.add_node(x) for x in nodelist]
    edgelist = [(0, 1), (1, 3), (3, 5), (5, 7), (7, 6), (6, 4), (4, 1), (3, 2), (2, 0), (8, 5)]
    edges = [g.add_link(nodes[a], nodes[b]) for a, b in edgelist]

    g2 = Graph(int, None, (GraphProperty.NonDirected,))
    nodes2 = [g2.add_node(x) for x in nodelist]
    edges2 = [g2.add_link(nodes2[a], nodes2[b]) for a, b in edgelist]


    from datastream.converter.from_graph.to_graphviz import graph_to_graphviz
    from datastream.converter.from_graphviz.to_fs import graphviz_to_fs

    #graphviz_to_fs(graph_to_graphviz(g), 'doctest-output/output', True)
    graphviz_to_fs(graph_to_graphviz(g), 'doctest-output/output_directed')
    graphviz_to_fs(graph_to_graphviz(g2), 'doctest-output/output_nondirected')

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
    graphviz_to_fs(graph_to_graphviz(g), 'doctest-output/output_directed2')

    print("\nthen back to normal")
    g.del_edge(Edge(nodes[5], nodes[8]))
    print(g.edges_number())
    print(strongly_connected_constraint(g))

    print("\nadding node")
    g.add_node(1298)
    print(weakly_connected_constraint(g))


    def generate_graph(node_min, node_max, edge_per_node_min, edge_per_node_max):
        import random
        g = Graph(int, str, (GraphProperty.Directed,))
        n_nodes = random.randint(node_min, node_max)
        nodes = [g.add_node(x) for x in range(n_nodes)]
        edges = []
        for n in nodes:
            n_edges = random.randint(edge_per_node_min, edge_per_node_max)
            edges.extend([g.add_link(n, nodes[random.randint(0, len(nodes)-1)], f"link[{n.nodeval}-{i}]") for i in range(n_edges)])
        return g



    from persistent.model.interact.answers.yes_no_unknown import YesNoUnknown

    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy import String, Integer, Column, Text


    columns = {
        "id": Column(Integer, primary_key=True),
        "question": Column(String(STRING_SIZE), unique=True),
    }

    Question = BasicEntity("GraphPropertyQuestion", columns)

    columns = {
        "id": Column(Integer, primary_key=True),
        "graph_json_as_string": Column(Text, unique=True),
    }

    QuestionedObject = BasicEntity("GraphJson", columns)

    from interact.server.web.json.flask.simple_flask_web_query_controller import SimpleFlaskWebQueryServer
    from datastream.converter.from_any.to_json import any_to_json
    from persistent.model.interact.query import QUERY

    session = create_session()

    randomG = generate_graph(2, 20, 0, 3)
    graphviz_to_fs(graph_to_graphviz(randomG), 'doctest-output/output_random')
    print(randomG)

    questions = []
    for checkfunc, cname in T[GraphProperty.Directed]:
        questions.append(Question.GET_CREATE(session, question=f"Is constraint {cname} verified? (evaluated to {checkfunc(randomG)})"))

    qobj = QuestionedObject.GET_CREATE(session, graph_json_as_string=any_to_json(randomG))

    QUERY_TYPE = QUERY(QuestionedObject, Question)
    for q in questions:
        new_query = QUERY_TYPE.GET_CREATE(session, questioned_object=qobj, question=q)
        print(new_query)




    GroupedObject = LIST(QuestionedObject)
    grouped_couple = GroupedObject(session, name="grouped per couple graphs progression")


    import random

    def generate_random(nnodes, minedges, maxedges):
        Tedges = [(i,j) for i in range(0, nnodes) for j in range(0, i+1)]
        random.shuffle(Tedges)
        chosen = Tedges[:random.randint(minedges, maxedges)]
        nodes = [Node(i) for i in range(nnodes)]
        edges = [Edge(nodes[i], nodes[j], f"n{i}->n{j}") for i,j in chosen]
        return nodes + edges

    found_for_property = {}
    while True:
        bad = False
        basegraph = generate_random(4, 0, 16)
        print(basegraph)
        print([p for p in GraphProperty if p not in found_for_property])
        for p in GraphProperty:
            if p not in found_for_property:
                try:
                    g = Graph.reconstruct(basegraph, additional_properties=[p], check=True)
                    found_for_property[p] = g
                except ConstraintNotFulfilled as e:
                    print(e)
                    bad = True
        if not bad:
            break

    for p in found_for_property:
        print(p)
        print(any_to_json(found_for_property[p]))

        q = Question.GET_CREATE(session, question=f"Is constraint {p} verified? (evaluated to true)")
        qobj = QuestionedObject.GET_CREATE(session, graph_json_as_string=any_to_json(found_for_property[p]))

        new_query = QUERY_TYPE.GET_CREATE(session, questioned_object=qobj, question=q)
        print(new_query)

    exit()

    g.add(session, i1)
    g.add(session, i2)
    g2 = GroupedObject(session, name="test grouped 2")


    controller = SimpleFlaskWebQueryServer(QuestionedObject, Question, YesNoUnknown, 1, create_session)
    controller.run()
