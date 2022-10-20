from dataclasses import dataclass


def tree(nodeType=None, edgeType=None):

    @dataclass
    class Node:

        def __init__(self, tree, value: nodeType):
            assert(isinstance(tree, Tree))
            assert(nodeType is None or isinstance(value, nodeType))
            self.value = value
            self.tree = tree

        def add_child(self, l):
            pass

    @dataclass
    class Edge:

        def __init__(self, tree, node1, node2, edgeval):
            assert (isinstance(tree, Tree))

            match node1:
                case Node():
                    print("Node1 OK")
                    self.parent = node1
                case nodeType() | None:
                    print("Node1 constructed from nodetype")
                    self.parent = Node(tree, node1)
                case _:
                    raise Exception("Bad node1 type")

            match node2:
                case Node():
                    print("Node2 OK")
                    self.child = node2
                case nodeType() | None:
                    print("Node2 constructed from nodetype")
                    self.parent = Node(tree, node2)
                case _:
                    raise Exception("Bad node2 type")

            assert ((edgeType is None and edgeval is None) or isinstance(edgeval, edgeType))
            self.value = edgeval


    class Tree:
        __nodetype__ = Node
        __edgetype__ = Edge

        def __init__(self):
            pass

    return Tree


if __name__ == "__main__":
    TREE = tree(int, str)
    NODE = TREE.__nodetype__
    EDGE = TREE.__edgetype__

    t = TREE()
    n1 = NODE(t, 12)
    n2 = NODE(t, 13)

    e = EDGE(t, n1, n2, "oo")
    e = EDGE(t, 1, n2, "oo")
    e = EDGE(t, n1, 99, "oo")
    e = EDGE(t, 1, 12, "oo")
