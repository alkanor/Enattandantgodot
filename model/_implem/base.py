from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from model_to_disk import get_engine
from model.general import sql_bases


Base = declarative_base()
sql_bases.append(Base)


class MetaCreateTableWhenEngine(DeclarativeMeta):

    def __init__(self, name, bases, dict):
        super(MetaCreateTableWhenEngine, self).__init__(name, (Base, ), dict)

        from model_to_disk import get_engine

        if get_engine():
            self.metadata.create_all(get_engine())


BaseCreateTableWhenEngine = declarative_base(metaclass = MetaCreateTableWhenEngine)
sql_bases.append(BaseCreateTableWhenEngine)


_cached_classes = {}

def BaseChangeClassName(*SQLAlchemyObjects):

    classname = "_".join(sorted(map(lambda x: x.__tablename__, SQLAlchemyObjects)))
    if _cached_classes.get(classname):
        return _cached_classes[classname]

    class MetaclassChangeName(MetaCreateTableWhenEngine):

        def __init__(self, name, bases, dict):
            super(MetaclassChangeName, self).__init__(name+"_"+classname, (Base, ), dict)

    _BaseChangeClassName = declarative_base(metaclass = MetaclassChangeName)
    _cached_classes[classname] = _BaseChangeClassName
    sql_bases.append(_BaseChangeClassName)
    return _BaseChangeClassName
