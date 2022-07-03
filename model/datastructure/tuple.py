from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declared_attr

from model.base import sql_bases, BaseAndMetaFromAttrDict, BaseAndMetaChangeClassName
from model.type_system import register_type


__objectname__ = "TUPLE"


@register_type(__objectname__, lambda *basetypes: map(lambda x: x.__tablename__, basetypes))
def TUPLE(*SQLAlchemyBaseTypes):

    tuple_tablename = f'{__objectname__}<{",".join(map(lambda x: x.__tablename__, SQLAlchemyBaseTypes))}>'

    columns = {
        "id": Column(Integer, primary_key=True),
        **{f"elem{i}_id": None for i, t in enumerate(SQLAlchemyBaseTypes)},  # already in AddDeclAttrMetaclass for sqlalchemy reason
        **{f"elem{i}": None for i, t in enumerate(SQLAlchemyBaseTypes)},     # already in AddDeclAttrMetaclass for sqlalchemy reason
    }
    repr_cols = ["id", *(f"elem{i}" for i in range(len(SQLAlchemyBaseTypes)))]

    _, meta_base = BaseAndMetaFromAttrDict(columns, BaseAndMetaChangeClassName(*SQLAlchemyBaseTypes)[1])

    def relationship_col(i):
        def sub(cls):
            return relationship(getattr(cls, f"elem{i}_type"), foreign_keys=[getattr(cls, f"elem{i}_id")])
        return sub

    class AddDeclAttrMetaclass(meta_base):

        def __new__(cls, name, bases, dict):
            for i, base_type in enumerate(SQLAlchemyBaseTypes):
                dict.update({f"elem{i}_type": base_type})
                dict.update({f"elem{i}_id": Column(Integer, ForeignKey(base_type.id), nullable=False)})
                dict.update({f"elem{i}": declared_attr(relationship_col(i))})
            dict["__table_args__"] = (UniqueConstraint(*[f"elem{i}_id" for i in range(len(SQLAlchemyBaseTypes))], name='unique_tuple'),)
            return super(AddDeclAttrMetaclass, cls).__new__(cls, name, bases, dict)

    BaseFromDict = declarative_base(metaclass = AddDeclAttrMetaclass)
    sql_bases.append(BaseFromDict)

    class TupleBase:

        def get(self, index):
            return getattr(self, f"elem{index}")

        def set(self, index, val):
            setattr(self, f"elem{index}", val)

        def __repr__(self):
            textual = ','.join(map(lambda x: x + " " + repr(getattr(self, x)), repr_cols))
            return f'{tuple_tablename} : {textual}'

    _TUPLE = BasicEntity(tuple_tablename, columns, [BaseFromDict, TupleBase], __objectname__)

    return _TUPLE


if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import BasicEntity, _Integer, _String, STRING_SIZE

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String


    columns = {
        "id": Column(Integer, primary_key=True),
        "valuetup": Column(String(STRING_SIZE), unique=True),
        "GGG": Column(Integer, default=918),
    }

    Test = BasicEntity("baktplebasics", columns)

    session = create_session()

    v1 = Test.GET_CREATE(session, valuetup="tuple1")
    v2 = Test.GET_CREATE(session, valuetup="tuple2")
    v3 = Test.GET_CREATE(session, valuetup="tuple3")
    v4 = Test.GET_CREATE(session, valuetup="tuple4")

    i1 = _Integer.GET_CREATE(session, id=182)
    i2 = _Integer.GET_CREATE(session, id=190)
    i3 = _Integer.GET_CREATE(session, id=9999999)

    s1 = _String.GET_CREATE(session, id="Yo")
    s2 = _String.GET_CREATE(session, id="Man")


    TUPLE_TYPE = TUPLE(Test, _Integer, Test, _String)

    a1 = TUPLE_TYPE.GET_CREATE(session, elem0=v1, elem1=i1, elem2=v3, elem3=s2)
    a2 = TUPLE_TYPE.GET_CREATE(session, elem0=v4, elem1=i2, elem2=v1, elem3=s2)

    print(a1)
    print(a2)
    a1.set(1, i3)

    try:
        print(a1)
        session.commit()
    except IntegrityError:
        print("Integrity error normal if db already created before")
        session.rollback()

    print(a1.get(0))
    print(a1.get(1))

    TUPLE_TYPE2 = TUPLE(Test, _Integer, Test, _String)
    TUPLE_TYPE3 = TUPLE(Test, _Integer, Test)

    print(TUPLE_TYPE2 == TUPLE_TYPE)
