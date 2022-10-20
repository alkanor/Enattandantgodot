from ..from_type.to_string import type_to_string
from ..from_any.to_dict import any_to_dict
from datastructure.base.graph import Node, Edge

from itertools import islice


def graph_to_dict(graph, ctxt=None):
    properties = graph.properties()
    edgetype = graph.edgetype

    res = {
        "metadata": {
            "properties": [p.name for p in properties],
            "nodetype": type_to_string(graph.nodetype),
            "edgetype": type_to_string(edgetype) if edgetype else None,
        },
       "data": {
           "nodes": [],
           "edges": [],
       }
    }

    max_elems = ctxt.get("max_elems", None) if ctxt else None
    offset = ctxt.get("offset", 0 if max_elems else None) if ctxt else None

    graph_generator = islice(graph.iterate(), offset, offset+max_elems) if offset is not None else graph.iterate()

    updated_index_nodes = {n: index for n, index in graph.indexed_nodes()}
    nodes = []
    edges = []
    at_least_one = False
    for element in graph_generator:
        at_least_one = True
        match element:
            case Node():
                assert element in updated_index_nodes, "Iterated node not in all graph.indexed_nodes computed previously"
                nodes.append({"id": updated_index_nodes[element], "obj": any_to_dict(element.nodeval)})
            case Edge():
                if element.edgeval is not None:
                    edges.append({"src": updated_index_nodes[element.source], "dst": updated_index_nodes[element.target], "obj": any_to_dict(element.edgeval)})
                else:
                    edges.append({"src": updated_index_nodes[element.source], "dst": updated_index_nodes[element.target]})
            case _:
                assert type(element) == type or element is None, f"Expecting at least a type when not node nor edge for {type(element)}"

    if not at_least_one:
        res["data"] = None
    else:
        res["data"]["nodes"] = nodes
        res["data"]["edges"] = edges
    return res


if __name__ == "__main__":
    from datastructure.base.graph_property import GraphProperty
    from datastructure.base.graph import Graph, Edge

    g = Graph(int, None, (GraphProperty.Directed,))
    nodelist = [3, 4, 1, 5, 9, 12, 100, 435, 999, 3]
    nodes = [g.add_node(x) for x in nodelist]
    edgelist = [(0, 1), (1, 3), (3, 5), (5, 7), (7, 6), (6, 4), (4, 1), (3, 2), (2, 0), (8, 5)]
    edges = [g.add_link(nodes[a], nodes[b]) for a, b in edgelist]

    print(graph_to_dict(g))

    ctxt = {"max_elems": 3}
    print(graph_to_dict(g, ctxt))

    offset = 0
    while True:
        ctxt.update({"offset": offset})
        tmp = graph_to_dict(g, ctxt)
        offset += 3
        print(tmp, "data" in tmp)
        if not "data" in tmp or not tmp["data"]:
            break
