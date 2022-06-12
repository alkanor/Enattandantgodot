from ._meta_meta import _META_SOMETHING


from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import MultipleResultsFound

from model.base_type import STRING_SIZE




def META_CONTEXT(SQLAlchemyBaseType):

    tname_prefix = f'META_CTX'

    columns = {
        "id": Column(Integer, primary_key=True),
        "contextid":  Column(String(STRING_SIZE))
    }

    return _META_SOMETHING(tname_prefix, columns, SQLAlchemyBaseType)



if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import _String

    session = create_session()

    CTX_STRING = META_CONTEXT(_String)

    print(CTX_STRING.GET(session, contextid="bonjour"))
    print(CTX_STRING.GET_CREATE(session, contextid="bonjour2"))
    print(CTX_STRING.NEW(session, contextid="bonjour"))
    print(CTX_STRING.NEW(session, contextid="bonjour"))
    print(CTX_STRING.GET(session, contextid="bonjour"))

    print(CTX_STRING.GET_COND(session, CTX_STRING.contextid == "bonjour2"))

    print(CTX_STRING.GET_CREATE(session, contextid="bonjour"))
    print(CTX_STRING.GET_CREATE(session, contextid="bonjour3"))

    CTX_STRING.DELETE(session, contextid="bonjour", id=6)
    print(CTX_STRING.NEW(session, contextid="bonjour4"))
    
    CTX_STRING.DELETE(session, contextid="bonjour")

    print(CTX_STRING.GET(session, contextid="bonjour"))
    print(CTX_STRING.GET_CREATE(session, contextid="bonjour"))
