from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint, select
from sqlalchemy import and_, or_, delete, func
from sqlalchemy.orm import relationship, validates

from persistent.metadata.named_date_metadata import NAMED_DATE_METADATA
from persistent.base.baseclass_metadata import baseclass_for_metadata
from persistent.base import BaseAndMetaChangeClassName
from persistent.utils.utcnow_compile import utcnow
from persistent.type_system import register_type


__objectname__ = "TREETEST"


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
        version = Column(Integer, nullable=False) # version column to indicate when tree node has been modified
        metadata_id = Column(Integer, ForeignKey(MetadataClass.id), nullable=False)

        if store_time:
            last_child_updated = Column(DateTime, default=utcnow(), onupdate=utcnow(), nullable=False)
            last_updated = Column(DateTime, default=utcnow(), nullable=False)

        __mapper_args__ = {
            "version_id_col": version
        }

        @declared_attr
        def metadataobj(cls):
            return relationship(MetadataClass, foreign_keys=[cls.metadata_id])

        if SQLAlchemyNodeType:
            attribute_id = Column(Integer, ForeignKey(SQLAlchemyNodeType.id), nullable=False)

            @declared_attr
            def attribute(cls):
                return relationship(SQLAlchemyNodeType, foreign_keys=[cls.attribute_id])

            @validates('attribute_id')
            def update_time(self, key, new_attr):
                self.last_updated = utcnow()
                return new_attr

#            __table_args__ = (UniqueConstraint('metadata_id', 'attribute_id', name='unique_node'),)

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

        def __init__(self, tree=None, *args, **argv):
            self.tree = tree
            super().__init__(*args, **argv)

        def ancestors(self, *args, **argv):
            return self.tree.ancestors(self, *args, **argv)

    # factorized
    for method_name in ["add_child",
                        "add_children",
                        "delete_child",
                        "delete_children",
                        "subtree",
                        "ancestors",
                        "descendants"]:
        setattr(TREE_NODE, method_name, lambda self, *args, **argv: getattr(self.tree, method_name)(self, *args, **argv))



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



    return _COMMON_TREE



if __name__ == '__main__':
    print()