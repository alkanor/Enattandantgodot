from .graph_property import GraphProperty


# properties partition, any graph can only have one property for each property type
GraphPropertiesPartition = [
    (GraphProperty.Directed, GraphProperty.NonDirected,),
    (GraphProperty.AcyclicDirected, GraphProperty.AcyclicNonDirected, GraphProperty.NonAcyclic,),
    (GraphProperty.WeaklyConnected, GraphProperty.StronglyConnected, GraphProperty.Connected, GraphProperty.NonConnected,),
    tuple([property for property in GraphProperty if
            property.value >= GraphProperty.LessThanOneParent.value and property.value <= GraphProperty.NoParentConstraint.value]),
    tuple([property for property in GraphProperty if
            property.value >= GraphProperty.Binary.value and property.value <= GraphProperty.NoChildConstraint.value]),
    tuple([property for property in GraphProperty if
            property.value >= GraphProperty.VerticeDegreeOne.value and property.value <= GraphProperty.NoVerticeDegreeConstraint.value]),
]

partitionedProperties = set([i for x in GraphPropertiesPartition for i in x])

GraphPropertyTypes = {
    property: [index for index, prop_tuple in enumerate(GraphPropertiesPartition) if property in prop_tuple][0]
    for property in GraphProperty if property in partitionedProperties
}

GraphPropertyDependancies = {
    prop: None for prop in GraphProperty
}

GraphPropertyDependancies[GraphProperty.AcyclicDirected] = (GraphProperty.Directed,)
GraphPropertyDependancies[GraphProperty.AcyclicNonDirected] = (GraphProperty.NonDirected,)

GraphPropertyDependancies[GraphProperty.WeaklyConnected] = (GraphProperty.Directed,)
GraphPropertyDependancies[GraphProperty.StronglyConnected] = (GraphProperty.Directed,)
GraphPropertyDependancies[GraphProperty.Connected] = (GraphProperty.NonDirected,)

GraphPropertyDependancies[GraphProperty.LessThanOneParent] = (GraphProperty.Directed,)
GraphPropertyDependancies[GraphProperty.OneParentExactly] = (GraphProperty.Directed,)
GraphPropertyDependancies[GraphProperty.LessThanTwoParents] = (GraphProperty.Directed,)
GraphPropertyDependancies[GraphProperty.NoParentConstraint] = (GraphProperty.Directed,)

GraphPropertyDependancies[GraphProperty.Binary] = (GraphProperty.Directed,)
GraphPropertyDependancies[GraphProperty.NoChildConstraint] = (GraphProperty.Directed,)

GraphPropertyDependancies[GraphProperty.VerticeDegreeOne] = (GraphProperty.NonDirected,)
GraphPropertyDependancies[GraphProperty.VerticeDegreeTwo] = (GraphProperty.NonDirected,)
GraphPropertyDependancies[GraphProperty.VerticeDegreeThree] = (GraphProperty.NonDirected,)
GraphPropertyDependancies[GraphProperty.NoVerticeDegreeConstraint] = (GraphProperty.NonDirected,)

GraphPropertyDependancies[GraphProperty.Forest] = (GraphProperty.AcyclicNonDirected,)
#GraphPropertyDependancies[GraphProperty.PolyForest] = (GraphProperty.AcyclicDirected, GraphProperty.EquivalentTreeAcyclic)
GraphPropertyDependancies[GraphProperty.PolyArborescence] = (GraphProperty.AcyclicDirected, GraphProperty.LessThanOneParent)
GraphPropertyDependancies[GraphProperty.DAG] = (GraphProperty.AcyclicDirected, GraphProperty.WeaklyConnected)
GraphPropertyDependancies[GraphProperty.Tree] = (GraphProperty.AcyclicNonDirected, GraphProperty.Connected)
GraphPropertyDependancies[GraphProperty.Arborescence] = (GraphProperty.AcyclicDirected, GraphProperty.WeaklyConnected, GraphProperty.LessThanOneParent)
#GraphPropertyDependancies[GraphProperty.PolyTree] = (GraphProperty.AcyclicDirected, GraphProperty.WeaklyConnected, GraphProperty.EquivalentTreeAcyclic)
