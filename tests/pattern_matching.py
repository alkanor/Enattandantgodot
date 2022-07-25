

def tree(nodeType=None, edgeType=None):

    class Node:

        def __init__(self, value: nodeType):
            assert(nodeType is None or isinstance(value, nodeType))
            self.value = value

    class Edge:

        def __init__(self, node1: Node, node2: Node, edgeval: edgeType):
            match node1:
                case Node:
                    self.parent = node1
                case nodeType | None:
                    self.parent = Node(node1)
                case _:
                    raise Exception("Bad node1 type")

            match node2

            assert (isinstance(node1, nodeType))
            assert (isinstance(node2, nodeType))
            assert (edgeType is None or isinstance(edgeval, nodeType))

def parse_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except:
        return None