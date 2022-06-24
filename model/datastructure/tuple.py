from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import and_, delete
from sqlalchemy.orm import relationship, reconstructor

from model.metadata.named_date_metadata import NAMED_DATE_METADATA
from model.base_type.base_entity import BaseDictToAttrs
from model._implem import BaseType, BaseChangeClassName
from model.metadata import metaclass_for_metadata
from model.type_system import register_type


__objectname__ = "TUPLE"


def _LIST_DEPENDANCIES(*SQLAlchemyBaseTypes):

    return map(lambda x: x.__tablename__, SQLAlchemyBaseTypes)


from model.base_type import BasicEntity


def _META_SOMETHING(metaname, columns_dict, MetaAdditional=None):

    return BasicEntity(metaname, columns_dict, MetaAdditional, metaname.split('<')[0])

from model.general import sql_bases
from sqlalchemy.ext.declarative import declarative_base


@register_type(__objectname__, _LIST_DEPENDANCIES)
def TUPLE(*SQLAlchemyBaseTypes):

    tuple_tablename = f'{__objectname__}<{",".join(map(lambda x: x.__tablename__, SQLAlchemyBaseTypes))}>'

    columns = {
        "id": Column(Integer, primary_key=True),
        **{f"elem{i}_id": None for i, t in enumerate(SQLAlchemyBaseTypes)},  # already in AddDeclAttrMetaclass for sqlalchemy reason
        **{f"elem{i}": None for i, t in enumerate(SQLAlchemyBaseTypes)},     # already in AddDeclAttrMetaclass for sqlalchemy reason
    }
    repr_cols = ["id", *(f"elem{i}" for i in range(len(SQLAlchemyBaseTypes)))]
    print(columns)

    new_base, meta_base = BaseDictToAttrs(columns)

    class AddDeclAttrMetaclass(meta_base):

        def __init__(self, name, bases, dict):
            print(dict)
            for i, base_type in enumerate(SQLAlchemyBaseTypes):
                dict.update({f"elem{i}_id": Column(Integer, ForeignKey(base_type.id), nullable=False)})
            for i, base_type in enumerate(SQLAlchemyBaseTypes):
                dict.update({f"elem{i}": relationship(base_type, foreign_keys=[dict[f"elem{i}_id"]])})
            super(AddDeclAttrMetaclass, self).__init__(name, bases, dict)

    BaseFromDict = declarative_base(metaclass = AddDeclAttrMetaclass)
    sql_bases.append(BaseFromDict)

    TUPLE = BasicEntity(tuple_tablename, columns, BaseFromDict, __objectname__)

    class TupleBase:

        def get(self, index):
            return getattr(self, f"elem{index}")

        def put(self, index, val):
            setattr(self, f"elem{index}", val)

        def __repr__(self):
            textual = ','.join(map(lambda x: x + " " + repr(getattr(self, x)), repr_cols))
            return f'{self.__tablename__} : {textual}'
     
    
    print(TupleBase.__dict__)
    for attr in TupleBase.__dict__:
        if attr not in dir(TUPLE) or attr == '__repr__':
            print(attr)
            setattr(TUPLE, attr, TupleBase.__dict__[attr])

    return TUPLE


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

    i1 = _Integer(id=182)
    i2 = _Integer(id=190)
    i3 = _Integer(id=9999999)

    s1 = _String(id="Yo")
    s2 = _String(id="Man")

    try:
        session.add(i1)
        session.commit()
    except:
        print("already here")
        session.rollback()
        i1 = session.query(_Integer).filter_by(id=182).one()

    try:
        session.add(i2)
        session.commit()
    except:
        print("already here")
        session.rollback()
        i2 = session.query(_Integer).filter_by(id=190).one()
    
    try:
        session.add(i3)
        session.commit()
    except:
        print("already here")
        session.rollback()
        i3 = session.query(_Integer).filter_by(id=9999999).one()

    try:
        session.add(s1)
        session.commit()
    except:
        print("already here")
        session.rollback()
        s1 = session.query(_String).filter_by(id="Yo").one()

    try:
        session.add(s2)
        session.commit()
    except:
        print("already here")
        session.rollback()
        s2 = session.query(_String).filter_by(id="Man").one()


    TUPLE_TYPE = TUPLE(Test, _Integer, Test, _String)

    a1 = TUPLE_TYPE.GET_CREATE(session, elem0=v1, elem1=i1, elem2=v3, elem3=s2)
    a2 = TUPLE_TYPE.GET_CREATE(session, elem0=v4, elem1=i2, elem2=v1, elem3=s2)

    print(a1)
    print(a2)
    a1.put(1, i3)

    print(a1)
    session.commit()
