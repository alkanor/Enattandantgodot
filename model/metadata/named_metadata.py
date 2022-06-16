from sqlalchemy import Column, Integer, String

from model.base_type import STRING_SIZE

from ._metadata_meta import _META_SOMETHING


def NAMED_METADATA(SQLAlchemyBaseType):

    tname_prefix = f'META_NAMED'

    columns = {
        "id": Column(Integer, primary_key=True),
        "name":  Column(String(STRING_SIZE))
    }

    return _META_SOMETHING(tname_prefix, columns, SQLAlchemyBaseType)
