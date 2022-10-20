from sqlalchemy.ext.declarative import declarative_base

from .sql_bases import sql_bases


Base = declarative_base()
sql_bases.append(Base)
