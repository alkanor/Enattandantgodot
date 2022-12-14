from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from persistent.base_type import STRING_SIZE

from ._metadata_meta import _META_SOMETHING


def NAMED_CONTEXT_METADATA(metadated_classname, SQLAlchemyContextType):

    tname_prefix = f'META_NAMED_CTX<{metadated_classname}>'

    class ToInherit:
        
        @declared_attr
        def contextid(cls):
            return Column(Integer, ForeignKey(SQLAlchemyContextType.id), nullable=False)
        
        @declared_attr
        def context(cls):
            return relationship(SQLAlchemyContextType, foreign_keys=[cls.contextid])

    columns = {
        "id": Column(Integer, primary_key=True),
        "name":  Column(String(STRING_SIZE)),
        "contextid": None, # already in ToInherit for sqlalchemy reason
        "context": None    # already in ToInherit for sqlalchemy reason
    }

    return _META_SOMETHING(tname_prefix, columns, ToInherit)
