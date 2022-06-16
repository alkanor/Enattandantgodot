from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from model.base_type import STRING_SIZE

from ._metadata_meta import _META_SOMETHING


def NAMED_CONTEXT_METADATA(SQLAlchemyBaseType, SQLAlchemyContextType):

    tname_prefix = f'META_NAMED_CTX'

    class MetaDecl:
        
        @declared_attr
        def contextid(cls):
            return Column(Integer, ForeignKey(SQLAlchemyContextType.id), nullable=False)
        
        @declared_attr
        def context(cls):
            return relationship(SQLAlchemyContextType, foreign_keys=[cls.contextid])

    columns = {
        "id": Column(Integer, primary_key=True),
        "name":  Column(String(STRING_SIZE)),
        "contextid": None, # already in MetaDecl for sqlalchemy reason
        "context": None    # already in MetaDecl for sqlalchemy reason
    }

    return _META_SOMETHING(tname_prefix, columns, SQLAlchemyBaseType, MetaDecl)