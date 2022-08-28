from .directed import bfs as bfs_directed, dfs as dfs_directed, ancestors, descendants, children_number, parents_number
from .nondirected import bfs as bfs_undirected, dfs as dfs_undirected, closure, direct_neighbors_size

from ..graph_property import GraphProperty


properties_extensions = {
    GraphProperty.Directed: [
        ("bfs", bfs_directed),
        ("dfs", dfs_directed),
        ("ancestors", ancestors),
        ("descendants", descendants),
        ("children_number", children_number),
        ("parents_number", parents_number),
    ],
    GraphProperty.NonDirected: [
        ("bfs", bfs_undirected),
        ("dfs", dfs_undirected),
        ("closure", closure),
        ("direct_neighbors_size", direct_neighbors_size),
    ],
}


def property_extensions(properties):
    for property in properties:
        yield from properties_extensions[property]
