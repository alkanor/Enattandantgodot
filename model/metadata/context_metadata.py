from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ._metadata_meta import _META_SOMETHING


def CONTEXT_METADATA(metadated_classname, SQLAlchemyContextType):

    tname_prefix = f'META_CTX<{metadated_classname}>'

    class ToInherit:
        
        @declared_attr
        def contextid(cls):
            return Column(Integer, ForeignKey(SQLAlchemyContextType.id), nullable=False)

        @declared_attr
        def context(cls):
            return relationship(SQLAlchemyContextType, foreign_keys=[cls.contextid])

    columns = {
        "id": Column(Integer, primary_key=True),
        "contextid": None, # already in ToInherit for sqlalchemy reason
        "context": None    # already in ToInherit for sqlalchemy reason
    }

    return _META_SOMETHING(tname_prefix, columns, ToInherit)



if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import _String, BasicEntity, STRING_SIZE

    from sqlalchemy import String


    columns = {
        "id": Column(Integer, primary_key=True),
        "value": Column(String(STRING_SIZE), unique=True),
        "SUPERCOL": Column(Integer, default=666),
    }

    Test = BasicEntity("thebaseobject", columns)

    v1 = Test(value="bonjour")

    session = create_session()
    
    v2 = Test.GET_CREATE(session, value="bonjour2")
    v3 = Test.GET_CREATE(session, value="bonjour3")
    v4 = Test.GET_CREATE(session, value="bonjour4")

    session.add(v1)
    try:
        session.commit()
    except:
        print("Rollbacking")
        session.rollback()
        v1 = Test.GET_CREATE(session, value="bonjour")
    

    CTX_STRING = CONTEXT_METADATA(Test.__tablename__, Test)

    print(CTX_STRING.GET(session, context=v1))
    print(CTX_STRING.GET_CREATE(session, context=v2))
    print(CTX_STRING.NEW(session, context=v1))
    print(CTX_STRING.NEW(session, context=v1))
    print(CTX_STRING.GET(session, context=v1))

    print(CTX_STRING.GET_COND(session, CTX_STRING.context == v2))

    print(CTX_STRING.GET_CREATE(session, context=v1))
    print(CTX_STRING.GET_CREATE(session, context=v3))

    CTX_STRING.DELETE(session, context=v1, id=6)
    print(CTX_STRING.NEW(session, context=v4))
    
    CTX_STRING.DELETE(session, context=v1)

    print(CTX_STRING.GET(session, context=v1))
    print(CTX_STRING.GET_CREATE(session, context=v1))
