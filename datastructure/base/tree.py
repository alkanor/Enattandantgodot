from dataclasses import dataclass


def tree(nodeType=None, edgeType=None):

    @dataclass
    class Node:
        __basetype__ = nodeType

        def add_child(self, child):
            return self.tree.add_child(self, child)

        def delete_child(self, child):
            return self.tree.delete_child(self, child)

    @dataclass
    class Edge:
        __basetype__ = edgeType


    class Tree:

        __nodetype__ = Node
        __edgetype__ = Edge

        def get_root(self):
            raise NotImplementedError

        def add_child(self, node1, node2, edgeval=None):
            raise NotImplementedError

        def add_children(self, node, children_iterable_with_edgeval):
            raise NotImplementedError

        def delete_child(self, node1, node2):
            raise NotImplementedError

        def delete_children(self, node, children_iterable):
            raise NotImplementedError

        def delete_from(self, node):
            raise NotImplementedError

        def iterate(self, from_node=None):
            raise NotImplementedError

    return Tree