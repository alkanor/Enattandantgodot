from sqlalchemy.ext.declarative import declarative_base

from .base_table_when_engine import MetaCreateTableWhenEngine
from .sql_bases import sql_bases


cache = {}

# provide metaclasses that do or do not inherit for DeclarativeMeta is of none importance since the MetaCreateTableWhenEngine metaclass is added in any case
def BaseAndMetaFromAttrDict(attr_dict, *metaclasses):
    cache_key = str(sorted(attr_dict.items()))

    if cache_key in cache:
        return cache[cache_key]

    class MetaFromAttrDict(*[*metaclasses, MetaCreateTableWhenEngine]):
        # __new__ is more appropriate in this case as we do not know when is handled the real object creation from attrs dict in sqlalchemy
        def __new__(cls, name, bases, dict):
            dict.update({k: v for k, v in attr_dict.items() if v is not None})
            return super().__new__(cls, name, bases, dict)

    BaseFromAttrDict = declarative_base(metaclass = MetaFromAttrDict)
    sql_bases.append(BaseFromAttrDict)

    cache[cache_key] = BaseFromAttrDict, MetaFromAttrDict

    return cache[cache_key]
