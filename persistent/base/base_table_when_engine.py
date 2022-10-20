from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from .sql_bases import sql_bases


class MetaCreateTableWhenEngine(DeclarativeMeta):
    # __init__ is ok in this case since it's only an external action to perform
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)

        from persistent_to_disk import get_engine
        if get_engine():
            cls.metadata.create_all(get_engine())


BaseCreateTableWhenEngine = declarative_base(metaclass = MetaCreateTableWhenEngine)
sql_bases.append(BaseCreateTableWhenEngine)
