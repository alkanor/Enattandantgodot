from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import UnmappedInstanceError

from model._implem import BaseMetaType
from model.general import sql_bases


cache = {}

def BaseDictToAttrs(attr_dict):
    cache_key = str(sorted(attr_dict.items()))

    if cache_key in cache:
        return cache[cache_key]

    class MetaClassDictToAttrs(BaseMetaType):

        def __init__(self, name, bases, dict):
            dict.update({k: v for k, v in attr_dict.items() if v is not None})
            super(MetaClassDictToAttrs, self).__init__(name, bases, dict)

    BaseFromDict = declarative_base(metaclass = MetaClassDictToAttrs)
    sql_bases.append(BaseFromDict)

    cache[cache_key] = BaseFromDict, MetaClassDictToAttrs

    return cache[cache_key]


def BasicEntity(tablename, columns_dict, ToInheritAdditional=None, slug=None, MetaAdditional=None):

    additional_metadict = {}
    if MetaAdditional:
        additional_metadict["metaclass"] = MetaAdditional

    class _BasicEntity(BaseDictToAttrs(columns_dict)[0], ToInheritAdditional if ToInheritAdditional else object, **additional_metadict):

        __tablename__ = tablename
        __slug__ = slug

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
            for k, v in argv.items():
                if not hasattr(newobj, k):
                    setattr(newobj, k, v)
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
            return f'{self.__tablename__} : [{textual}]'

    return _BasicEntity
