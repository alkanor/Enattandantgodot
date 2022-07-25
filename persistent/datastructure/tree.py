from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint, select
from sqlalchemy import and_, or_, delete, func
from sqlalchemy.orm import relationship

from persistent.metadata.named_date_metadata import NAMED_DATE_METADATA
from persistent.base.baseclass_metadata import baseclass_for_metadata
from persistent.base import BaseAndMetaChangeClassName
from persistent.utils.utcnow_compile import utcnow
from persistent.type_system import register_type


__objectname__ = "TREE"


def _metadata_default(MetadataType=None, *additional_args_to_construct_metadata):
    if not MetadataType:
        return NAMED_DATE_METADATA(__objectname__)
    return MetadataType(__objectname__, *additional_args_to_construct_metadata)


def _TREE_DEPENDANCIES(SQLAlchemyNodeType=None, SQLAlchemyEdgeType=None, MetadataType=None, closure_max_depth=4, store_time=False, *additional_args_to_construct_metadata):
    MetadataClass = _metadata_default(MetadataType, *additional_args_to_construct_metadata)

    metaclass_tablename = MetadataClass.__tablename__
    tree_tablename = f'{__objectname__}<{MetadataClass.__slug__},{SQLAlchemyNodeType.__tablename__ if SQLAlchemyNodeType else "NONODE"},' \
                     f'                                          {SQLAlchemyEdgeType.__tablename__ if SQLAlchemyEdgeType else "NOEDGE"},{closure_max_depth}>'

    return metaclass_tablename, tree_tablename


@register_type(__objectname__, _TREE_DEPENDANCIES)
def TREE(SQLAlchemyNodeType=None, SQLAlchemyEdgeType=None, MetadataType=None, closure_max_depth=4, store_time=False, *additional_args_to_construct_metadata):
    MetadataClass = _metadata_default(MetadataType, *additional_args_to_construct_metadata)

    class _TREE_NODE(BaseAndMetaChangeClassName(SQLAlchemyNodeType, MetadataClass)[0]):

        __tablename__ = f'{__objectname__}_NODE<{MetadataClass.__slug__}{","+SQLAlchemyNodeType.__tablename__ if SQLAlchemyNodeType else ""}>'
        __basetype__ = SQLAlchemyNodeType

        id = Column(Integer, primary_key=True)
        version = Column(Integer, default=True) # version column to indicate when tree node has been modified
        isroot = Column(Boolean, default=False)
        metadata_id = Column(Integer, ForeignKey(MetadataClass.id), nullable=False)

        if store_time:
            last_child_updated = Column(DateTime, default=utcnow(), onupdate=utcnow(), nullable=False)
            last_updated = Column(DateTime, default=utcnow(), onupdate=utcnow(), nullable=False)

        #__table_args__ = (UniqueConstraint('metadata_id', 'ancestor_id', 'descendant_id', name='unique_edge'),)

        @declared_attr
        def metadataobj(cls):
            return relationship(MetadataClass, foreign_keys=[cls.metadata_id])

        if SQLAlchemyNodeType:
            attribute_id = Column(Integer, ForeignKey(SQLAlchemyNodeType.id), nullable=False)

            @declared_attr
            def attribute(cls):
                return relationship(SQLAlchemyNodeType, foreign_keys=[cls.attribute_id])

            __table_args__ = (UniqueConstraint('metadata_id', 'attribute_id', name='unique_node'),)

        def __repr__(self):
            return f'NODE {self.id}{" = " + str(self.attribute) if SQLAlchemyNodeType else ""}'


    class _TREE_EDGE(BaseAndMetaChangeClassName(SQLAlchemyEdgeType, MetadataClass)[0]):

        __tablename__ = f'{__objectname__}_EDGE<{MetadataClass.__slug__}{","+SQLAlchemyNodeType.__tablename__ if SQLAlchemyNodeType else "NONODE"}' \
                                                                      f'{","+SQLAlchemyEdgeType.__tablename__ if SQLAlchemyEdgeType else ""},{closure_max_depth}>'
        __basetype__ = SQLAlchemyEdgeType

        id = Column(Integer, primary_key=True)
        ancestor_id = Column(Integer, ForeignKey(_TREE_NODE.id), nullable=False)
        descendant_id = Column(Integer, ForeignKey(_TREE_NODE.id), nullable=False)
        path_size = Column(Integer, default=1)

        __table_args__ = (UniqueConstraint('metadata_id', 'ancestor_id', 'descendant_id', name='unique_edge'),)

        @declared_attr
        def ancestor(cls):
            return relationship(_TREE_NODE, foreign_keys=[cls.ancestor_id])

        @declared_attr
        def descendant(cls):
            return relationship(_TREE_NODE, foreign_keys=[cls.descendant_id])

        if SQLAlchemyEdgeType:
            attribute_id = Column(Integer, ForeignKey(SQLAlchemyEdgeType.id), nullable=False)

            @declared_attr
            def attribute(cls):
                return relationship(SQLAlchemyEdgeType, foreign_keys=[cls.attribute_id])

        def __repr__(self):
            return f'Edge {self.id} : {self.ancestor} - {"-" if not SQLAlchemyEdgeType else self.attribute} > {self.descendant}'


    class TREE_NODE(_TREE_NODE):

        def __init__(self, session=None, autocommit=False, *args, **argv):
            if session:
                self._saved_session = session
            self.autocommit = autocommit
            super().__init__(*args, **argv)

        def _autocommit_if_enabled(self, session):
            if self.autocommit:
                session.commit()

        def _get_session(self, session):
            return session if session else self._saved_session

        def _get_nodes(self, session, nodeobj, allows_many=False):
            if type(nodeobj) == TREE_NODE and getattr(nodeobj, "id") and nodeobj.id:
                assert type(nodeobj.metadataobj) == type(self.metadataobj), "Node comparaison / get must be done within same metadata tree"
                return nodeobj
            else:
                if not allows_many:
                    return session.query(TREE_NODE).filter_by(metadataobj=self.metadataobj, attribute=nodeobj.attribute if type(nodeobj) == TREE_NODE else nodeobj).one_or_none()
                else:
                    return session.query(TREE_NODE).filter_by(metadataobj=self.metadataobj, attribute=nodeobj.attribute if type(nodeobj) == TREE_NODE else nodeobj).all()

        def add_child(self, child=None, session=None):
            session = self._get_session(session)
            assert (not child and not SQLAlchemyNodeType) or (type(child) == SQLAlchemyNodeType and SQLAlchemyNodeType) or (type(child) == TREE_NODE), \
                        "Tree node child must be either the provided Node type if not none else none"

            if not child:
                new_child = TREE_NODE(session, self.autocommit)
                session.add(new_child)
                new_edge = _TREE_EDGE(ancestor=self, descendant=new_child)
                session.add(new_edge)
                self._autocommit_if_enabled()
                return new_child

            check_no_parent = False
            if type(child) != TREE_NODE: # so type(child) == SQLAlchemyNodeType
                childnode = self._get_nodes(session, child) # multi node not authorized
                if not childnode:
                    childnode = TREE_NODE(session, self.autocommit, metadataobj=self.metadataobj, attribute=child)
                    session.add(childnode)
                else:
                    check_no_parent = True
            else:
                childnode = child
                check_no_parent = True

            if check_no_parent:
                existing = session.query(_TREE_EDGE).filter_by(descendant=childnode).one_or_none()
                assert not existing, "Setting node child implies the child has no parent yet"

            new_edge = _TREE_EDGE(ancestor=self, descendant=childnode)
            session.add(new_edge)
            self._autocommit_if_enabled()
            return childnode


        def add_children(self, children=1, session=None):
            if type(children) == int:
                return [self.add_child(None, session) for _ in range(children)]
            else:
                return [self.add_child(child, session) for child in children]


        def delete_child(self, child, session=None):
            session = self._get_session(session)
            assert type(child) == TREE_NODE or (type(child) == SQLAlchemyNodeType and SQLAlchemyNodeType), \
                    "Tree nodes to delete must be either the provided Node type if not none or a tree node to find it"

            if type(child) == SQLAlchemyNodeType:
                child = session.query(TREE_NODE).filter_by(metadata=self.metadataobj, attribute=child).one_or_none()
                assert child, f"Deleting node child implies the provided child as attribute exists for metadata {self.metadataobj}"

            existing = session.query(_TREE_EDGE).filter_by(ancestor=self, descendant=child).one_or_none()
            assert existing, f"Deleting node child implies a real node child is provided for {self.metadataobj}, not arbitrary node"

            del_edge_statement = delete(_TREE_EDGE).where(and_(_TREE_EDGE.ancestor == self, _TREE_EDGE.descendant == child))
            session.execute(del_edge_statement)
            del_node_statement = delete(TREE_NODE).where(and_(TREE_NODE.metadata_id == self.metadata.id, TREE_NODE.id == child.id))
            session.execute(del_node_statement)
            self._autocommit_if_enabled()

        def delete_children(self, children, session=None):
            for child in children:
                self.delete_child(child, session)


        def set_attribute(self, attribute_obj, session=None, allows_many=False):
            session = self._get_session(session)
            objs = self._get_nodes(session, self, allows_many)

            if not objs:
                new_node = TREE_NODE(metadataobj=self.metadataobj, attribute=attribute_obj)
                session.add(new_node)
            elif type(objs) == TREE_NODE:
                objs.attribute = attribute_obj
            else:
                for o in objs:
                    o.attribute = attribute_obj

            self._autocommit_if_enabled(session)


        def descendents(self, maxdepth=1, mindepth=1, session=None):
            return session.execute(
                select(TREE_NODE, _TREE_EDGE.path_size)
                    .join(_TREE_EDGE, onclause=
                        and_(_TREE_EDGE.ancestor == self,
                             _TREE_EDGE.descendent_id == TREE_NODE.id,
                             _TREE_EDGE.path_size >= mindepth,
                             or_(_TREE_EDGE.path_size <= maxdepth, maxdepth < 0)))
            ).all()
            # prendre en compte la depth max pour closure

        def ancestors(self, maxdepth=1, mindepth=1, session=None):
            return session.execute(
                select(TREE_NODE, _TREE_EDGE.path_size)
                    .join(_TREE_EDGE, onclause=
                        and_(_TREE_EDGE.descendent == self,
                             _TREE_EDGE.ancestor_id == TREE_NODE.id,
                             _TREE_EDGE.path_size >= mindepth,
                             or_(_TREE_EDGE.path_size <= maxdepth, maxdepth < 0)))
            ).all()



    class _COMMON_TREE(baseclass_for_metadata(MetadataClass)):

        __nodetype__ = _TREE_NODE
        __edgetype__ = _TREE_EDGE

        def __init__(self, session, metadataobj=None, autocommit=False, **argv):
            if metadataobj:
                assert type(metadataobj) == MetadataClass, f"Provided metadata object must be of {MetadataClass} type"  # comes from baseclass_for_metadata
                self.metadata = metadataobj
            else:
                self.metadata = MetadataClass.GET_CREATE(session, **argv)
            self.root_initialized = False
            self._session_saved = session
            self.autocommit = autocommit

        def _autocommit_if_enabled(self, session):
            if self.autocommit:
                session.commit()

        def _get_session(self, session):
            return session if session else self._saved_session


        def node_for_attributes(self, elem, session=None):
            session = self._get_session(session)
            return session.Query(TREE_NODE).filter_by(metadataobj=self.metadataobj, attribute=elem).one_or_none()

        def nodes_for_attributes(self, elem, session=None):
            session = self._get_session(session)
            return session.Query(TREE_NODE).filter_by(metadataobj=self.metadataobj, attribute=elem).all()


        def clear(self, session):
            self._session_saved = session
            statement = delete(_LIST_ENTRY).where(_LIST_ENTRY.metadata_id == self.metadata.id)
            session.execute(statement)
            session.commit()
            MetadataClass.DELETE(session, id=self.metadata.id)
            self.entries = []

        def __repr__(self):
            return f'{self.metadata} : {self.entries}'


        def get_roots(session) -> List[TreeNodeClass]:
            return session.execute(
                select(TreeNodeClass) \
                    .outerjoin(TreePathClass, onclause=TreePathClass.descendent == TreeNodeClass.id)
                    .group_by(TreeNodeClass.id)
                    .having(TreePathClass.ancestor == None)
            ).scalars().all()

        def subtree(session, node: TreeNodeClass = None) -> Dict[
            int, Dict]:  # un-optimized version of subtree as only direct children are known
            if node:
                cur_nodes = [(node, [node.id])]
            else:
                cur_nodes = [(root, [root.id]) for root in get_roots(session)]

            results = {n.id: (None, {}) for n, _ in cur_nodes}
            cur_nodes_kept = list(cur_nodes)
            node_id_set = set()

            while cur_nodes:
                cur_node, path = cur_nodes[0]
                node_id_set.add(cur_node.id)

                for child, depth in cur_node.descendents(session):  # default to a depth of 1
                    if depth != 1:
                        raise Exception(f"In classic subtree function depth is not one: {depth}")
                    if child.id in node_id_set:
                        raise Exception(f"Child ID {child.id} already encountered, a cycle may be present in the tree")

                    cur_nodes.append((child, path + [child.id]))
                    cur_nodes_kept.append((child, path + [child.id]))

                del cur_nodes[0]

            related_objects = session.query(TreeNodeClass.id, join_table_object).join(join_table_object).filter(
                TreeNodeClass.node.in_(node_id_set)).all()
            related_objects_dict = {i: ref for i, ref in related_objects}
            if len(set(related_objects_dict.keys()).intersection(node_id_set)) != len(node_id_set):
                raise Exception(f"Not all node objects being related to an existing foreign object ... (" + \
                                f"{len(related_objects_dict.keys().intersect(node_id_set))} != {len(node_id_set)}) ")

            for n, path in cur_nodes_kept:
                tmp_res = results
                for p in path[:-1]:
                    tmp_res = tmp_res[p][1]
                tmp_res[path[-1]] = (related_objects_dict[path[-1]], {})

            return results



    class TREE(_COMMON_TREE):
        pass

    class FOREST(_COMMON_TREE):
        pass

    return _COMMON_TREE




def test(session):
    from ..general.string_reference import test as populate_string_references, StringReference
    from .._Engine import create_structure

    T = TreeNode(StringReference, "TESTDB")

    create_structure()

    populate_string_references(session)

    if len(session.query(T).all()) < 8:
        refs = session.query(StringReference).all()
        fhalf = refs[:4]
        lhalf = refs[4:]
        for ref in fhalf:
            print(T.add_node(session, ref))
        print(T.add_nodes(session, lhalf))

        T.add_child(session, refs[0], refs[3], 1)
        T.add_child(session, refs[1], refs[2], 1)

        T.add_child(session, refs[1], refs[4], 2)
        T.add_child(session, refs[2], refs[4], 1)

        T.add_child(session, refs[1], refs[5], 2)
        T.add_child(session, refs[2], refs[5], 1)

        T.add_children(session, [(refs[1], refs[6], 3), \
                                 (refs[2], refs[6], 2), \
                                 (refs[5], refs[6], 1), \
                                 (refs[1], refs[7], 3), \
                                 (refs[2], refs[7], 2), \
                                 (refs[4], refs[7], 1)])

    elem = session.query(T).filter_by(id=2).one_or_none()
    print(elem, elem.obj.reference)
    print(elem.descendents(session))
    print(elem.descendents(session, maxdepth=-1))
    for e, depth in T.descendents(session, elem):
        print(e, depth)
        print(e.id, e.node)
        print(e.obj.reference)

    print(T.get_roots(session))

    print(T.subtree(session))


if __name__ == "__main__":
    from .._Engine import create_session

    session = create_session()
    test(session)
    session.close()
