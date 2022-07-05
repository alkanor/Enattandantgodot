from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declared_attr

from model.base import sql_bases, BaseAndMetaFromAttrDict, BaseAndMetaChangeClassName
from model.type_system import register_type


__objectname__ = "UNION"


@register_type(__objectname__, lambda *basetypes: sorted(map(lambda x: x.__tablename__, set(basetypes))))
def UNION(*SQLAlchemyBaseTypes):
    per_tablename = {x.__tablename__: x for x in SQLAlchemyBaseTypes}
    sorted_keys = sorted(per_tablename.keys())
    sorted_basetypes = sorted(per_tablename.items())
    sorted_values = list(map(lambda x: x[1], sorted_basetypes))

    union_tablename = f'{__objectname__}<{",".join(sorted_keys)}>'

    columns = {
        "id": Column(Integer, primary_key=True),
        **{f"{i}_id": None for i in sorted_keys},
        **{i: None for i in sorted_keys},
    }
    repr_cols = ["id", *sorted_keys]

    _, meta_base = BaseAndMetaFromAttrDict(columns, BaseAndMetaChangeClassName(*sorted_values)[1])

    def relationship_col(i):
        def sub(cls):
            return relationship(getattr(cls, f"{i}_type"), foreign_keys=[getattr(cls, f"{i}_id")])
        return sub

    class AddDeclAttrMetaclass(meta_base):

        def __new__(cls, name, bases, dict):
            for i, base_type in sorted_basetypes:
                dict.update({f"{i}_type": base_type})
                dict.update({f"{i}_id": Column(Integer, ForeignKey(base_type.id), nullable=True, unique=True)})
                dict.update({i: declared_attr(relationship_col(i))})
            return super().__new__(cls, name, bases, dict)

    BaseFromDict = declarative_base(metaclass=AddDeclAttrMetaclass)
    sql_bases.append(BaseFromDict)

    class UnionBase:

        def __init__(self, *args, **argv):
            assert(len(argv) + len(args) == 1)
            if argv:
                arg = list(argv.items())[0]
                setattr(self, arg[0], arg[1])
            else:
                setattr(self, args[0].__tablename__, args[0])

        def get(self):
            not_none = [getattr(self, i) for i in sorted_keys]
            not_none = [i for i in not_none if i]
            assert(len(not_none) <= 1)
            return not_none[0] if not_none else None

        def set(self, value):
            assert(value.__tablename__ in sorted_keys)
            for k in sorted_keys:
                setattr(self, k, None)
            setattr(self, value.__tablename__, value)

        def __repr__(self):
            textual = ','.join(map(lambda x: x + " " + repr(getattr(self, x)), repr_cols))
            return f'{union_tablename} : {textual}'

    _UNION = BasicEntity(union_tablename, columns, [BaseFromDict, UnionBase], __objectname__)

    return _UNION


if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import BasicEntity, _Integer, _String, STRING_SIZE

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String

    columns = {
        "id": Column(Integer, primary_key=True),
        "lol": Column(String(STRING_SIZE), unique=True),
        "xD": Column(Integer, default=1337),
    }

    Test = BasicEntity("XXD", columns)

    session = create_session()

    v1 = Test.GET_CREATE(session, lol="lol", xD=87)
    v2 = Test.GET_CREATE(session, lol="union", xD=100)
    v3 = Test.GET_CREATE(session, lol="make", xD=12)
    v4 = Test.GET_CREATE(session, lol="stupid", xD=23)

    i1 = _Integer.GET_CREATE(session, id=88)
    i2 = _Integer.GET_CREATE(session, id=145)
    i3 = _Integer.GET_CREATE(session, id=999)

    s1 = _String.GET_CREATE(session, id="Yo")
    s2 = _String.GET_CREATE(session, id="Man")

    UNION_TYPE = UNION(Test, _Integer, _String)

    a1 = UNION_TYPE.GET_CREATE(session, string=s2)
    a2 = UNION_TYPE(i3)

    try:
        session.add(a2)
        session.commit()
    except IntegrityError:
        print("If exception normal if db already existing")
        session.rollback()

    print(a1)
    print(a2)
    a1.set(i2)

    try:
        print(a1)
        session.commit()
    except IntegrityError:
        print("Integrity error normal if db already created before")
        session.rollback()

    print(a1.get())

    a1.set(v2)
    try:
        print(a1.get())
        session.commit()
    except IntegrityError:
        print("Integrity error normal if db already created before")
        session.rollback()

    UNION_TYPE2 = UNION(Test, _Integer, _String)
    UNION_TYPE3 = UNION(_Integer, _String)

    print(UNION_TYPE2 == UNION_TYPE)
