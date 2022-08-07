from .graph import Graph
from enum import Enum


class GraphProperty(Enum):

    Oriented = 2,
    NonOriented = 3,         # default case related to orientation

    AcyclicOriented = 4,
    AcyclicNonOriented = 5,
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


# properties partition, any graph can only have one property for each property type
GraphPropertiesPartition = [
    (GraphProperty.Oriented, GraphProperty.NonOriented,),
    (GraphProperty.AcyclicOriented, GraphProperty.AcyclicNonOriented, GraphProperty.NonAcyclic,),
    (GraphProperty.WeaklyConnected, GraphProperty.StronglyConnected, GraphProperty.Connected, GraphProperty.NonConnected,),
    (*[property for property in GraphProperty if
       property.value >= GraphProperty.LessThanOneParent.value and property.value <= GraphProperty.NoParentConstraint]),
    (*[property for property in GraphProperty if
       property.value >= GraphProperty.Binary.value and property.value <= GraphProperty.NoChildConstraint]),
    (*[property for property in GraphProperty if
       property.value >= GraphProperty.VerticeDegreeOne.value and property.value <= GraphProperty.NoVerticeDegreeConstraint]),
]

GraphPropertyTypes = {
    property: [index for index, prop_tuple in enumerate(GraphPropertiesPartition) if property in prop_tuple][0]
    for property in GraphProperty
}

GraphPropertyDependancies = {
    prop: None for prop in GraphProperty
}

GraphPropertyDependancies[GraphProperty.AcyclicOriented] = (GraphProperty.Oriented,)
GraphPropertyDependancies[GraphProperty.AcyclicNonOriented] = (GraphProperty.NonOriented,)

GraphPropertyDependancies[GraphProperty.WeaklyConnected] = (GraphProperty.Oriented,)
GraphPropertyDependancies[GraphProperty.StronglyConnected] = (GraphProperty.Oriented,)
GraphPropertyDependancies[GraphProperty.Connected] = (GraphProperty.NonOriented,)

GraphPropertyDependancies[GraphProperty.LessThanOneParent] = (GraphProperty.Oriented,)
GraphPropertyDependancies[GraphProperty.OneParentExactly] = (GraphProperty.Oriented,)
GraphPropertyDependancies[GraphProperty.LessThanTwoParents] = (GraphProperty.Oriented,)
GraphPropertyDependancies[GraphProperty.NoParentConstraint] = (GraphProperty.Oriented,)

GraphPropertyDependancies[GraphProperty.Binary] = (GraphProperty.Oriented,)
GraphPropertyDependancies[GraphProperty.NoChildConstraint] = (GraphProperty.Oriented,)

GraphPropertyDependancies[GraphProperty.VerticeDegreeOne] = (GraphProperty.NonOriented,)
GraphPropertyDependancies[GraphProperty.VerticeDegreeTwo] = (GraphProperty.NonOriented,)
GraphPropertyDependancies[GraphProperty.VerticeDegreeThree] = (GraphProperty.NonOriented,)
GraphPropertyDependancies[GraphProperty.NoVerticeDegreeConstraint] = (GraphProperty.NonOriented,)


class ConstraintException(Exception):
    def __init__(self, property):
        super().__init__(f"{property.name} constraint not fullfilled")


GraphPropertyConstraints = {

    GraphProperty.Oriented: None,
    GraphProperty.NonOriented: None,

    GraphProperty.AcyclicOriented: ((Graph.add_edge.__name__,
                                     Graph.add_child.__name__,),
                                    acyclic_oriented_constraint),
    GraphProperty.AcyclicNonOriented: ((Graph.add_edge.__name__,
                                     Graph.add_child.__name__,),
                                    acyclic_non_oriented_constraint),
    GraphProperty.NonAcyclic: None,

    GraphProperty.WeaklyConnected: ((Graph.del_child.__name__,
                                     Graph.del_edge.__name__,
                                     Graph.del_node.__name__,),
                                    weakly_connected_constraint),
    GraphProperty.StronglyConnected: ((Graph.del_child.__name__,
                                       Graph.del_edge.__name__,
                                       Graph.del_node.__name__,),
                                      strongly_connected_constraint),
    GraphProperty.Connected: ((Graph.del_child.__name__,
                               Graph.del_edge.__name__,
                               Graph.del_node.__name__,),
                              connected_constraint),
    GraphProperty.NonConnected: None,

    GraphProperty.LessThanOneParent: ((Graph.add_child.__name__,
                                       Graph.add_edge.__name__,),
                                      max_parents_per_vertice_constraint(1)),
    GraphProperty.OneParentExactly: ((Graph.add_child.__name__,
                                      Graph.add_edge.__name__,
                                      Graph.add_node.__name__,
                                      Graph.del_child.__name__,
                                      Graph.del_edge.__name__,
                                      Graph.del_node.__name__,),
                                     parents_per_vertice_constraint(1)),
    GraphProperty.LessThanTwoParents: ((Graph.add_child.__name__,
                                       Graph.add_edge.__name__,),
                                      max_parents_per_vertice_constraint(2)),
    GraphProperty.NoParentConstraint: None,

    GraphProperty.Binary: ((Graph.add_child.__name__,
                            Graph.add_edge.__name__,),
                           max_children_per_vertice_constraint(2)),
    GraphProperty.NoChildConstraint: None,

    GraphProperty.VerticeDegreeOne: ((Graph.add_child.__name__,
                                      Graph.add_edge.__name__,),
                                     max_vertice_degree_constraint(1)),
    GraphProperty.VerticeDegreeTwo: ((Graph.add_child.__name__,
                                      Graph.add_edge.__name__,),
                                     max_vertice_degree_constraint(2)),
    GraphProperty.VerticeDegreeThree: ((Graph.add_child.__name__,
                                        Graph.add_edge.__name__,),
                                       max_vertice_degree_constraint(3)),
    GraphProperty.NoVerticeDegreeConstraint: None,
}
