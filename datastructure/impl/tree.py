from datastructure.base import tree as _tree
from dataclasses import dataclass


def tree(nodeType=None, edgeType=None, noneNodeAllowed=False, noneEdgeAllowed=False):

    @dataclass
    class Node:
        def __init__(self, tree, value=None):
            assert isinstance(tree, Tree), f"Tree passed in Node constructor not instance of Tree {Tree}"
            assert ((noneNodeAllowed or nodeType is None) and value is None) or isinstance(value, nodeType), f"Node constructed with {type(value)} instead of {nodeType}"
            self.tree = tree
            self.value = value
            self.parent = None
            self.parent_edge_val = None
            self.children = set()

        def add_child(self, child):
            return self.tree.add_child(self, child)

        def delete_child(self, child):
            return self.tree.delete_child(self, child)

    @dataclass
    class Edge:
        def __init__(self, node1, node2, edgeval):
            self.parent = node1
            self.child = node2
            self.value = edgeval


    def match_type_against_node(tree, elem):
        match elem:
            case Node():
                return elem
            case nodeType() | None:
                return Node(tree, elem)
            case _:
                raise AssertionError(f"Bad node1 type {type(elem)} instead of {Node} or {nodeType}")


    class Tree:

        __nodetype__ = Node
        __edgetype__ = Edge

        def __init__(self, default_val=None):
            self.nodes = set()
            self.edges = set()
            self.root = None
            self.default_val = default_val

        def get_root(self):
            if not self.root:
                self.root = Node(self, self.default_val)
                self.nodes.add(self.root)
                self.root.parent = self.root
            return self.root

        def add_child(self, node1, node2, edgeval=None):
            assert node1 in self.nodes, "Cannot add child to node not in tree"

            if node2 in self.nodes:
                assert node2.parent is None, "Adding child need the child to be an orphan"

            if not isinstance(node2, Node):
                node2 = match_type_against_node(node2)

            node1.children.add(node2)
            node2.parent = node1

            assert ((noneEdgeAllowed or edgeType is None) and edgeval is None) or isinstance(edgeval, edgeType), \
                                                        f"Edge constructed with {type(edgeval)} instead of {edgeType}"
            node2.parent_edge_val = edgeval

        def delete_child(self, node1, node2):
            assert node1 in self.nodes, "Cannot delete from child node not in tree"
            assert node2 in self.nodes, "Cannot delete a child node not in tree"
            assert node2 in node1.children, "Cannot delete a child which is not related to the parent"
            node1.remove(node2)
            self.nodes.remove(node2)

        def delete_from(self, node):
            assert node in self.nodes, "Cannot delete from child node not in tree"
            for x in node.children:
                self.delete_from(x)
            del node.children
            self.nodes.remove(node)

        def iterate(self, from_node=None):
            return self.bfs(from_node)

        def bfs(self, from_node=None):
            return self.dfs(from_node, 0)

        def dfs(self, from_node=None, dfs=True):
            if not from_node:
                from_node = self.get_root()
            stack = [from_node]
            while stack:
                node = stack.pop() if dfs else stack.pop(0)
                yield node
                for x in node.children:
                    stack.append(x)

    return Tree