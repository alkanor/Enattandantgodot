from ._meta_meta import _META_SOMETHING

from sqlalchemy import Column, Integer, String

from model.base_type import STRING_SIZE


def META_NAMED(SQLAlchemyBaseType):

    tname_prefix = f'META_NAMED'

    columns = {
        "id": Column(Integer, primary_key=True),
        "name":  Column(String(STRING_SIZE))
    }

    return _META_SOMETHING(tname_prefix, columns, SQLAlchemyBaseType)


if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import _String

    session = create_session()

    NAMED_STRING = META_NAMED(_String)

    print(NAMED_STRING.GET(session, name="bonjour"))
    print(NAMED_STRING.GET_CREATE(session, name="bonjour2"))
    print(NAMED_STRING.NEW(session, name="bonjour"))
    print(NAMED_STRING.NEW(session, name="bonjour"))
    print(NAMED_STRING.GET(session, name="bonjour"))

    print(NAMED_STRING.GET_COND(session, NAMED_STRING.name == "bonjour2"))

    print(NAMED_STRING.GET_CREATE(session, name="bonjour"))
    print(NAMED_STRING.GET_CREATE(session, name="bonjour3"))

    NAMED_STRING.DELETE(session, name="bonjour", id=6)
    print(NAMED_STRING.NEW(session, name="bonjour4"))
    
    NAMED_STRING.DELETE(session, name="bonjour")

    print(NAMED_STRING.GET(session, name="bonjour"))
    print(NAMED_STRING.GET_CREATE(session, name="bonjour"))
