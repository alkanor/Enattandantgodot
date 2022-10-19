from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy import delete
from sqlalchemy.orm import relationship

from persistent.metadata.named_date_metadata import NAMED_DATE_METADATA
from persistent.base.baseclass_metadata import baseclass_for_metadata
from persistent.base import BaseAndMetaChangeClassName
from persistent.type_system import register_type


__objectname__ = "CONTEXT_TYPE"

from persistent.utils.utcnow_compile import utcnow


@register_type(__objectname__, lambda basetype, context=None: (basetype.__tablename__, ) if not context else (basetype.__tablename__, context.__tablename__,))
def ContextualizedType(SQLAlchemyBaseType, ContextType=None):
    if ContextType:
        object_tablename = f"{__objectname__}<{SQLAlchemyBaseType.__tablename__},{ContextType.__tablename__}>"
    else:
        object_tablename = f"{__objectname__}<{SQLAlchemyBaseType.__tablename__}>"

    if ContextType:
        ChangeClassNameBase, _ = BaseAndMetaChangeClassName(SQLAlchemyBaseType, ContextType)
    else:
        ChangeClassNameBase, _ = BaseAndMetaChangeClassName(SQLAlchemyBaseType)


    class _CONTEXTUALIZED_OBJECT(ChangeClassNameBase):

        __tablename__ = object_tablename
        __basetype__ = SQLAlchemyBaseType
        if ContextType:
            __contexttype__ = ContextType

        id = Column(Integer, primary_key=True)
        object_id = Column(Integer, ForeignKey(SQLAlchemyBaseType.id), nullable=False)
        created_at = Column(DateTime(timezone=True), server_default=utcnow())
        modified_at = Column(DateTime(timezone=True), onupdate=utcnow())

        if ContextType:
            context_id = Column(Integer, ForeignKey(ContextType.id), nullable=False)

        @declared_attr
        def obj(cls):
            return relationship(SQLAlchemyBaseType, foreign_keys=[cls.object_id])

        if ContextType:
            @declared_attr
            def context(cls):
                return relationship(ContextType, foreign_keys=[cls.context_id])


        def __init__(self, *args, **argv):
            filtered_args = {}
            session = None
            for arg in args:
                if ContextType and isinstance(arg, ContextType):
                    assert "context" not in filtered_args, "At least 2 context arguments passed to constructor, at most one expected"
                    filtered_args["context"] = arg
                elif isinstance(arg, SQLAlchemyBaseType):
                    assert "obj" not in filtered_args, "At least 2 base sqlaclh class arguments passed to constructor, at most one expected"
                    filtered_args["obj"] = arg
                else:
                    assert "session" not in filtered_args, "At least 2 other arguments passed to constructor, at most one expected (session)"
                    filtered_args["session"] = arg
                    session = arg
            if "context" in filtered_args and "context" in argv:
                assert filtered_args["context"] == args["context"], "Provided contexts (args and argv) must be the same"
            if "obj" in filtered_args and "obj" in argv:
                assert filtered_args["obj"] == args["obj"], "Provided base SQLAlch objects (args and argv) must be the same"
            argv.update(filtered_args)

            super().__init__(**{k: v for k,v in argv.items() if k != "session"})

            if session:
                session.add(self)
                session.commit()

        @classmethod
        def GET_ALL_FOR(cls, session, arg):
            if ContextType and isinstance(arg, ContextType):
                return session.query(cls).filter(cls.context == arg).all()
            elif isinstance(arg, SQLAlchemyBaseType):
                return session.query(cls).filter(cls.obj == arg).all()
            else:
                raise NotImplementedError

        @classmethod
        def GET_ALL_CREATED(cls, session, date, compareason_operator=None):
            raise NotImplementedError

        @classmethod
        def GET_ALL_MODIFIED(cls, session, date, compareason_operator=None):
            raise NotImplementedError

        def __repr__(self):
            return (f'[CTXT: {self.context}] ' if ContextType else '')+ f'{self.obj} (created at {self.created_at}, last modified at {self.modified_at})'

    return _CONTEXTUALIZED_OBJECT
