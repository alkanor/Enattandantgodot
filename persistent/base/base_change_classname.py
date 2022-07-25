from sqlalchemy.ext.declarative import declarative_base

from .base_table_when_engine import MetaCreateTableWhenEngine
from .sql_bases import sql_bases


_cached_classes = {}

def BaseAndMetaChangeClassName(*SQLAlchemyObjects):

    classname = "_".join(sorted(map(lambda x: x.__tablename__, SQLAlchemyObjects)))
    if _cached_classes.get(classname):
        return _cached_classes[classname]

    class MetaChangeClassName(MetaCreateTableWhenEngine):
        # __init__ is ok in this case since it's only a cosmetic change on the class name
        def __init__(cls, name, bases, dict):
            super().__init__(name+"_"+classname, bases, dict)

    _BaseChangeClassName = declarative_base(metaclass = MetaChangeClassName)
    _cached_classes[classname] = _BaseChangeClassName
    sql_bases.append(_BaseChangeClassName)
    return _BaseChangeClassName, MetaChangeClassName
