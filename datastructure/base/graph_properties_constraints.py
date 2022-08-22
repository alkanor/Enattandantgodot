from .graph_constraints import acyclic_oriented_constraint, acyclic_non_oriented_constraint, \
                               weakly_connected_constraint, strongly_connected_constraint, connected_constraint, \
                               max_parents_per_vertice_constraint, parents_per_vertice_constraint, \
                               max_children_per_vertice_constraint, \
                               max_vertice_degree_constraint
from .graph_property import GraphProperty
from .graph import Graph


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

    GraphProperty.WeaklyConnected: ((Graph.add_node.__name__,
                                     Graph.del_edge.__name__,
                                     Graph.del_node.__name__,),
                                    weakly_connected_constraint),
    GraphProperty.StronglyConnected: ((Graph.add_node.__name__,
                                       Graph.del_edge.__name__,
                                       Graph.del_node.__name__,),
                                      strongly_connected_constraint),
    GraphProperty.Connected: ((Graph.add_node.__name__,
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
