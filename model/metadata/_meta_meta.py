from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm.exc import UnmappedInstanceError

from ._base import BaseDictToAttrs

from model_to_disk import get_engine
from model.general import sql_bases



def _META_SOMETHING(metaname, columns_dict, SQLAlchemyBaseType):

    class SQLAlchClass(BaseDictToAttrs(columns_dict)):
        
        __tablename__ =  f'{metaname}[{SQLAlchemyBaseType.__tablename__}]'

        @classmethod
        def GET(cls, session, **argv):
            filtered_result = session.query(cls)
            for colname in columns_dict:
                filtered_result = filtered_result.filter(getattr(cls, colname) == argv[colname] if argv.get(colname) else True)
                
            result = list(filtered_result.all())
            if len(result) == 1:
                return result[0]
            else:
                return None if not result else result
        
        @classmethod
        def GET_CREATE(cls, session, **argv):
            existing = cls.GET(session, **argv)
            if existing:
                return existing
            newobj = cls(**argv)
            session.add(newobj)
            session.commit()
            return newobj

        @classmethod
        def NEW(cls, session, **argv):
            newobj = cls(**argv)
            session.add(newobj)
            session.commit()
            return newobj

        @classmethod
        def DELETE(cls, session, **argv):
            existing = cls.GET(session, **argv)
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
            textual = ' - '.join(map(lambda x: x + " " + repr(getattr(self, x)), columns_dict))
            return f'{self.__tablename__} : {textual}'

    return SQLAlchClass
