from .graph_property import GraphProperty


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
