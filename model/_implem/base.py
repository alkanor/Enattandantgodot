from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from model_to_disk import get_engine
from model.general import sql_bases


Base = declarative_base()
sql_bases.append(Base)

class MetaCreateTableWhenEngine(DeclarativeMeta):

    def __init__(cls, name, bases, dict):
        super(MetaCreateTableWhenEngine, cls).__init__(name, (Base, ), dict)

        from model_to_disk import get_engine

        if get_engine():
            cls.metadata.create_all(get_engine())


BaseCreateTableWhenEngine = declarative_base(metaclass = MetaCreateTableWhenEngine)
sql_bases.append(BaseCreateTableWhenEngine)
