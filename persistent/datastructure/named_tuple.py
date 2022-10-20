from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from persistent.base import BaseAndMetaFromAttrDict, BaseAndMetaChangeClassName
from persistent.type_system import register_type
from persistent.base import sql_bases


__objectname__ = "NAMED_TUPLE"


@register_type(__objectname__, lambda **basetypes: map(lambda x: x[0]+","+x[1].__tablename__, sorted(basetypes.items())))
def NAMED_TUPLE(**NamedSQLAlchemyBaseTypes):

    tuple_tablename = f'{__objectname__}<{",".join(sorted(NamedSQLAlchemyBaseTypes.keys()))}>'

    columns = {
        "id": Column(Integer, primary_key=True),
        **{f"{t}_id": None for t in NamedSQLAlchemyBaseTypes.keys()},  # already in AddDeclAttrMetaclass for sqlalchemy reason
        **{t: None for t in NamedSQLAlchemyBaseTypes.keys()},          # already in AddDeclAttrMetaclass for sqlalchemy reason
    }
    repr_cols = ["id", *NamedSQLAlchemyBaseTypes.keys()]

    _, meta_base = BaseAndMetaFromAttrDict(columns, BaseAndMetaChangeClassName(*list(map(lambda x: x[1], sorted(NamedSQLAlchemyBaseTypes.items()))))[1])

    def relationship_col(i):
        def sub(cls):
            return relationship(getattr(cls, f"{i}_type"), foreign_keys=[getattr(cls, f"{i}_id")])
        return sub

    class AddDeclAttrMetaclass(meta_base):

        def __new__(cls, name, bases, dict):
            for t, base_type in list(NamedSQLAlchemyBaseTypes.items()):
                dict.update({f"{t}_type": base_type})
                dict.update({f"{t}_id": Column(Integer, ForeignKey(base_type.id), nullable=False)})
                dict.update({t: declared_attr(relationship_col(t))})
            dict["__table_args__"] = (UniqueConstraint(*[f"{i}_id" for i in NamedSQLAlchemyBaseTypes.keys()], name='unique_named_tuple'),)
            return super().__new__(cls, name, bases, dict)

    BaseFromDict = declarative_base(metaclass = AddDeclAttrMetaclass)
    sql_bases.append(BaseFromDict)

    class NamedTupleBase:

        def get(self, name):
            return getattr(self, name)

        def set(self, name, val):
            setattr(self, name, val)

        def __repr__(self):
            textual = ','.join(map(lambda x: x + " " + repr(getattr(self, x)), repr_cols))
            return f'{tuple_tablename} : {textual}'

    _NAMED_TUPLE = BasicEntity(tuple_tablename, columns, [BaseFromDict, NamedTupleBase], __objectname__)

    return _NAMED_TUPLE



if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, _Integer, _String, STRING_SIZE

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String


    columns = {
        "id": Column(Integer, primary_key=True),
        "valtup": Column(String(STRING_SIZE), unique=True),
        "XXX": Column(Integer, default=123),
    }

    Test = BasicEntity("baknamtplebasics", columns)

    session = create_session()

    v1 = Test.GET_CREATE(session, valtup="tuple1")

    i1 = _Integer.GET_CREATE(session, id=182)
    i2 = _Integer.GET_CREATE(session, id=190)
    i3 = _Integer.GET_CREATE(session, id=199)

    s1 = _String.GET_CREATE(session, id="Yo")

    TUPLE_TYPE = NAMED_TUPLE(first_v=Test, second_i=_Integer, third_i=_Integer)

    a1 = TUPLE_TYPE.GET_CREATE(session, first_v=v1, second_i=i1, third_i=i1)
    a2 = TUPLE_TYPE.GET_CREATE(session, first_v=v1, second_i=i2, third_i=i1)

    print(a1)
    print(a2)
    a1.set("third_i", i3)

    try:
        print(a1)
        session.commit()
    except IntegrityError:
        print("Integrity error normal if db already created before")
        session.rollback()

    print(a1.get("first_v"))
    print(a1.get("third_i"))

    a3 = TUPLE_TYPE.GET_CREATE(session, first_v=v1, second_i=i1, third_i=i2)
    print(a3)
