from .directed import bfs as bfs_directed, dfs as dfs_directed, ancestors, descendants, children_number, parents_number
from .nondirected import bfs as bfs_undirected, dfs as dfs_undirected, closure, direct_neighbors_size
from .strongly_connected import path_from_directed
from .weakly_connected import strong_components, strong_component_for
from .non_connected import components, component_for
from .connected import path_from_nondirected
from .family import parent, left, right, set_left, set_right

from ..graph_property import GraphProperty


properties_extensions = {
    GraphProperty.Directed: [
        ("bfs", bfs_directed),
        ("dfs", dfs_directed),
        ("ancestors", ancestors),
        ("descendants", descendants),
        ("children_number", children_number),
        ("parents_number", parents_number),
        ("parents", lambda graph, node: ancestors(graph, node, 1)),
        ("children", lambda graph, node: descendants(graph, node, 1)),
    ],
    GraphProperty.NonDirected: [
        ("bfs", bfs_undirected),
        ("dfs", dfs_undirected),
        ("closure", closure),
        ("direct_neighbors_size", direct_neighbors_size),
    ],
    GraphProperty.WeaklyConnected: [
        ("strong_components", strong_components),
        ("strong_component_for", strong_component_for),
    ],
    GraphProperty.StronglyConnected: [
        ("path_from", path_from_directed),
    ],
    GraphProperty.Connected: [
        ("path_from", path_from_nondirected),
    ],
    GraphProperty.NonConnected: [
        ("components", components),
        ("component_for", component_for),
    ],
    GraphProperty.LessThanOneParent: [
        ("parent", parent),
    ],
    GraphProperty.OneParentExactly: [
        ("parent", parent),
    ],
    GraphProperty.Binary: [
        ("left", left),
        ("right", right),
        ("set_left", set_left),
        ("set_right", set_right),
    ],
}


def property_extensions(properties):
    for property in properties:
        yield from properties_extensions[property]
