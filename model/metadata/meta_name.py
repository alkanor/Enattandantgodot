from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import MultipleResultsFound

from ._base import BaseMetadatastructure
from .meta_meta import MetaBase

from model.base_type import STRING_SIZE



def META_NAME(SQLAlchemyBaseType):

    class SQLAlchClass(MetaBase):
        
        __tablename__ =  f'META[{SQLAlchemyBaseType.__tablename__}]'

        id = Column(Integer, primary_key=True)
        name = Column(String(STRING_SIZE))

        @classmethod
        def GET(cls, session, name=None, id=None):
            try:
                result = session.query(cls).filter(cls.name==name if name else True).filter(cls.id==id if id else True).one_or_none()
                return result
            except MultipleResultsFound:
                return session.query(cls).filter(cls.name==name if name else True).filter(cls.id==id if id else True).all()
        
        @classmethod
        def GET_CREATE(cls, session, name=None, id=None):
            existing = cls.GET(session, name, id)
            if existing:
                return existing
            newobj = cls(name=name, id=id)
            session.add(newobj)
            session.commit()
            return newobj

        @classmethod
        def NEW(cls, session, name=None):
            newobj = cls(name=name)
            session.add(newobj)
            session.commit()
            return newobj

        @classmethod
        def DELETE(cls, session, name=None, id=None):
            existing = cls.GET(session, name, id)
            if existing is None:
                return
            try:
                session.delete(existing)
            except UnmappedInstanceError:
                for x in existing:
                    session.delete(x)
            session.commit()
                
        @classmethod
        def GET_COND(cls, session, condition):
            return session.query(cls).filter(condition).all()
        
        def __repr__(self):
            return f'{self.__tablename__} : id {self.id} - name {self.name}'

    return SQLAlchClass


if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import _String

    session = create_session()

    NAMED_STRING = META_NAME(_String)

    print(NAMED_STRING.GET(session, "bonjour"))
    print(NAMED_STRING.GET_CREATE(session, "bonjour2"))
    print(NAMED_STRING.NEW(session, "bonjour"))
    print(NAMED_STRING.NEW(session, "bonjour"))
    print(NAMED_STRING.GET(session, "bonjour"))

    print(NAMED_STRING.GET_COND(session, NAMED_STRING.name == "bonjour2"))

    print(NAMED_STRING.GET_CREATE(session, "bonjour"))
    print(NAMED_STRING.GET_CREATE(session, "bonjour3"))

    NAMED_STRING.DELETE(session, "bonjour", 6)
    print(NAMED_STRING.NEW(session, "bonjour4"))
    
    NAMED_STRING.DELETE(session, "bonjour")

    print(NAMED_STRING.GET(session, "bonjour"))
    print(NAMED_STRING.GET_CREATE(session, "bonjour"))
