from enum import Enum


class GraphProperty(Enum):

    Directed = 2,
    NonDirected = 3,         # default case related to orientation

    AcyclicDirected = 4,
    AcyclicNonDirected = 5,
    NonAcyclic = 7,          # default case related to cycles

    WeaklyConnected = 8,     # for Oriented graph, weakly connected = associated non oriented graph is connected
    StronglyConnected = 9,   # for Oriented graph, like connected for a non oriented graph
    Connected = 10,          # for NonOriented graph, there is a path from every node to any node
    NonConnected = 15,       # default case related to connectivity

    # for oriented graph properties about number of children / parent
    LessThanOneParent = 16,
    OneParentExactly = 17,
    LessThanTwoParents = 18,
    NoParentConstraint = 31, # default case related to parent constraints

    Binary = 32,
    NoChildConstraint = 63,

    # for non oriented graph properties about vertice degree
    VerticeDegreeOne = 64,
    VerticeDegreeTwo = 65,
    VerticeDegreeThree = 66,
    NoVerticeDegreeConstraint = 127,
