from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import and_, delete
from sqlalchemy.orm import relationship

from model.type_system import register_type
from model.base_type import STRING_SIZE
from model._implem import BaseType


class ALIAS_METADATA(BaseType):

    __tablename__ = "alias"

    alias = Column(String(STRING_SIZE), primary_key=True)
    target_type = Column(String(STRING_SIZE), nullable=False)


_alias_cache = {}
def _update_metadata(session, aliastype):
    filter = {
                "alias": aliastype.__tablename__,
                "target_type":  aliastype.__basetype__.__tablename__
            }

    if not _alias_cache:
        all_aliases = session.query(ALIAS_METADATA).all()
        _alias_cache.update({a.alias: a.target_type for a in all_aliases})

    if filter["alias"] not in _alias_cache:
        existing = session.query(ALIAS_METADATA).filter_by(**filter).one_or_none()
        if not existing:
            new_alias = ALIAS_METADATA(**filter)
            session.add(new_alias)
            session.commit()
        _alias_cache[filter["alias"]] = filter["target_type"]



@register_type("ALIAS", lambda basetype, alias_name: (basetype.__tablename__, alias_name))
def ALIAS(SQLAlchemyBaseType, alias_name):

    class _ALIAS(BaseType):

        __basetype__ = SQLAlchemyBaseType
        __tablename__ = alias_name

        id = Column(Integer, primary_key=True)
        alias_id = Column(Integer, ForeignKey(SQLAlchemyBaseType.id), nullable=False)

        @declared_attr
        def alias(cls):
            return relationship(SQLAlchemyBaseType, foreign_keys=[cls.alias_id])


        def __init__(self, session, *args, **argv):
            _update_metadata(session, self.__class__)
            if args:
                assert(type(args[0]) == self.__basetype__)
                self.alias = args[0]
            else:
                self.alias = session.query(SQLAlchemyBaseType).filter_by(**argv).one_or_none()

        def __repr__(self):
            return f'ALIAS [{self.alias}]'


        @classmethod
        def GET(cls, session, **argv):
            if not SQLAlchemyBaseType.GET(session, **argv):
                return None
            else:
                return cls(session, **argv)
        
        @classmethod
        def GET_CREATE(cls, session, **argv):
            return cls(session, **argv)

        @classmethod
        def NEW(cls, session, **argv):
            new_alias = SQLAlchemyBaseType.NEW(session, **argv)
            return cls(session, new_alias)

        @classmethod
        def DELETE(cls, session, **argv):
            existing = cls.GET(session, **argv)
            if existing is None:
                return
            SQLAlchemyBaseType.DELETE(session, **argv)
                
        @classmethod
        def GET_COND(cls, session, condition):
            from_basetype = SQLAlchemyBaseType.GET_COND(session, condition)
            return list([cls(session, b) for b in from_basetype])

    return _ALIAS





if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import _String, BasicEntity, STRING_SIZE

    from sqlalchemy import String


    columns = {
        "id": Column(Integer, primary_key=True),
        "vv": Column(String(STRING_SIZE), unique=True),
        "xx": Column(Integer, default=666),
    }

    Test = BasicEntity("bak3basics", columns)

    session = create_session()

    v1 = Test.GET_CREATE(session, xx="jour1")
    v2 = Test.GET_CREATE(session, xx="jour2")
    v3 = Test.GET_CREATE(session, xx="jour3")
    v4 = Test.GET_CREATE(session, xx="jour4")


    HOST = ALIAS(Test, "HOST")

    host1 = HOST(session, vv="12")
    host2 = HOST(session, vv="12", xx=1020)
    host3 = HOST(session, vv="12")


    from .list import LIST

    HOSTLIST = LIST(HOST)
    HOST_GROUP = ALIAS(HOSTLIST, "HOST_GROUP")

    mylist1 = HOSTLIST(session, name="superlist1")
    mylist2 = HOSTLIST(session, name="superlist2")

    print(_alias_cache)
    list1 = HOST_GROUP(session, name="mylist")
    print(_alias_cache)

