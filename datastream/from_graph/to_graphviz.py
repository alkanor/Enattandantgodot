from datastructure.base.graph_property import GraphProperty
from datastructure.base.graph import Node, Edge
import graphviz


def process_node(node_to_index, nodes, G, node):
    if node not in node_to_index:
        node_to_index[node] = len(node_to_index)
        nodes.append(G.node(str(node_to_index[node]), str(node.nodeval)))
    return node_to_index[node]


def graph_to_graphviz(graph, engine='sfdp'):
    if graph.has_property(GraphProperty.Directed):
        g = graphviz.Digraph(engine=engine)
    else:
        g = graphviz.Graph(engine=engine)

    node_to_index = {}
    nodes = []
    edges = []
    for element in graph.iterate():
        match element:
            case Node():
                process_node(node_to_index, nodes, g, element)
            case Edge():
                n1 = process_node(node_to_index, nodes, g, element.source)
                n2 = process_node(node_to_index, nodes, g, element.target)
                if element.edgeval is not None:
                    edges.append(g.edge(str(n1), str(n2), str(element.edgeval)))
                else:
                    edges.append(g.edge(str(n1), str(n2)))
            case _:
                assert type(element) == type or element is None, f"Expecting at least a type when not node nor edge for {type(element)}"

    return g
