from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from model.base_type import STRING_SIZE

from ._metadata_meta import _META_SOMETHING


def NAMED_DATE_METADATA(metadated_classname):

    tname_prefix = f'META_NAMED_DATE<{metadated_classname}>'

    columns = {
        "id": Column(Integer, primary_key=True),
        "name":  Column(String(STRING_SIZE)),
        "date": Column(DateTime(timezone=True), server_default=func.now()),
    }

    return _META_SOMETHING(tname_prefix, columns)



if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import _String

    session = create_session()

    NAMED_STRING = NAMED_DATE_METADATA(_String.__tablename__)

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

    base_date = NAMED_STRING.GET(session, name="bonjour").date
    print(f"At same date {base_date} {func.date(base_date)}")
    print(NAMED_STRING.GET(session, date=str(base_date)))
    print(NAMED_STRING.GET_COND(session, func.date(base_date) == func.date(NAMED_STRING.date)))
