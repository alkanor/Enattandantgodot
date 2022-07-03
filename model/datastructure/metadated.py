from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import and_, delete
from sqlalchemy.orm import relationship

from model.metadata.named_date_metadata import NAMED_DATE_METADATA
from model.base import Base, BaseAndMetaChangeClassName
from model.metadata import baseclass_for_metadata
from model.type_system import register_type


__objectname__ = "METADATED_TYPE"


def _DEPENDANCIES(SQLAlchemyBaseType, MetadataType=None, *additional_args_to_construct_metadata):
    if not MetadataType:
        MetadataClass = NAMED_DATE_METADATA(SQLAlchemyBaseType.__tablename__)
    else:
        MetadataClass = MetadataType(SQLAlchemyBaseType.__tablename__, *additional_args_to_construct_metadata)

    metaclass_tablename = MetadataClass.__tablename__
    object_tablename = f'{MetadataClass.__slug__}-{SQLAlchemyBaseType.__tablename__}'

    return metaclass_tablename, object_tablename


@register_type(__objectname__, _DEPENDANCIES)
def MetadatedType(SQLAlchemyBaseType,  MetadataType=None, *additional_args_to_construct_metadata):
    metaclass_tablename, object_tablename = _DEPENDANCIES(SQLAlchemyBaseType, MetadataType=None,
                                                            *additional_args_to_construct_metadata)

    if not MetadataType:
        MetadataClass = NAMED_DATE_METADATA(SQLAlchemyBaseType.__tablename__)
    else:
        MetadataClass = MetadataType(SQLAlchemyBaseType.__tablename__, *additional_args_to_construct_metadata)

    assert (metaclass_tablename == MetadataClass.__tablename__)

    ChangeClassNameBase, _ = BaseAndMetaChangeClassName(SQLAlchemyBaseType, MetadataClass)
    class _METADATED_OBJECT(ChangeClassNameBase, baseclass_for_metadata(MetadataClass)):

        __tablename__ = object_tablename
        __metadataclass__ = MetadataClass
        __basetype__ = SQLAlchemyBaseType

        id = Column(Integer, primary_key=True)
        metadata_id = Column(Integer, ForeignKey(MetadataClass.id), nullable=False, unique=True)
        object_id = Column(Integer, ForeignKey(SQLAlchemyBaseType.id), nullable=False)

        @declared_attr
        def metadataobj(cls):
            return relationship(MetadataClass, foreign_keys=[cls.metadata_id])

        @declared_attr
        def obj(cls):
            return relationship(SQLAlchemyBaseType, foreign_keys=[cls.object_id])

        def __init__(self, *args, **argv):
            if not args: # no session, so basic sqlalchemy construction
                super(ChangeClassNameBase, self).__init__(*args, **argv)
                return
            else: # at least session in arg, we can automatically setup what is needed for object search according to args types
                session = args[0]
                assert len(args) > 1, "Not enough arguments to construct the metadated type, need at least metadata or base object"
                assert type(session) != MetadataClass and type(session) != SQLAlchemyBaseType, "First argument must be an SQLAlchemy session"

                if len(args) > 2:
                    if type(args[1]) == self.__metadataclass__:  # in this case we must have the third argument type = metadata
                        self.metadataobj = args[1]
                        self.obj = args[2]
                    else:
                        self.metadataobj = args[2]
                        self.obj = args[1]
                    already_existing = session.query(_METADATED_OBJECT).filter_by(metadataobj=self.metadataobj, obj=self.obj).one_or_none()
                    if not already_existing: # persisting the metadated object if not existing as all required data is known
                        session.add(self)
                        session.commit()
                else:
                    self.metadataobj = None
                    self.obj = None
                    if type(args[1]) == self.__metadataclass__:
                        self.metadataobj = args[1]
                    else:
                        self.obj = args[1]
                self._session_saved = session

        # lazy load the real object when needed, otherwise only the metadata suffices
        @property
        def object(self):
            if not self.obj: # get the object from its metadata
                self.obj = self._session_saved.query(_METADATED_OBJECT).join(_METADATED_OBJECT.obj).filter(_METADATED_OBJECT.metadataobj == self.metadataobj).one_or_none()
            return self.obj

        @object.setter
        def object(self, new_obj):
            self.obj = new_obj
            self._session_saved.add(self)
            self._session_saved.commit()

        @object.deleter
        def object(self):
            self.obj = None


        @property
        def metadata_object(self):
            if not self.metadataobj: # get the object from its metadata
                self.metadataobj = self._session_saved.query(_METADATED_OBJECT).join(_METADATED_OBJECT.metadataobj).filter(_METADATED_OBJECT.obj == self.obj).one_or_none()
            return self.metadataobj

        @metadata_object.setter
        def metadata_object(self, new_metadata):
            self.metadataobj = new_metadata
            self._session_saved.add(self)
            self._session_saved.commit()

        @metadata_object.deleter
        def metadata_object(self):
            self.metadataobj = None


        def clear(self, session):
            self._session_saved = session
            statement = delete(_METADATED_OBJECT).where(_METADATED_OBJECT.metadata_id == self.metadata.id)
            session.execute(statement)
            session.commit()
            MetadataClass.DELETE(session, id=self.metadata.id)
            self.obj = None
            self.metadataobj = None

        def __repr__(self):
            return f'{self.metadataobj} : {self.obj}'

    return _METADATED_OBJECT


if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import BasicEntity, _Integer, _String, STRING_SIZE

    from sqlalchemy.exc import IntegrityError, MultipleResultsFound
    from sqlalchemy import String

    columns = {
        "id": Column(Integer, primary_key=True),
        "STR": Column(String(STRING_SIZE), unique=True),
        "INT": Column(Integer, default=666),
    }

    Test = BasicEntity("bak55basics", columns)

    session = create_session()

    v1 = Test.GET_CREATE(session, STR="bonjour1", INT=23)
    v2 = Test.GET_CREATE(session, STR="bonjour2", INT=34)
    v3 = Test.GET_CREATE(session, STR="bonjour3", INT=45)
    v4 = Test.GET_CREATE(session, STR="bonjour4", INT=56)

    META1 = MetadatedType(Test)
    META2 = MetadatedType(_String, NAMED_DATE_METADATA)
    META3 = MetadatedType(_Integer)

    _NAMED_DATE_METADATA = META1.__metadataclass__
    try:
        metadata1 = _NAMED_DATE_METADATA.GET_CREATE(session, name="M1")[0]
    except:
        metadata1 = _NAMED_DATE_METADATA.GET_CREATE(session, name="M1")
    metadata2 = _NAMED_DATE_METADATA.GET_CREATE(session, name="M2")
    metadata3 = _NAMED_DATE_METADATA.NEW(session, name="M1")
    metadata4 = _NAMED_DATE_METADATA.GET_CREATE(session, name="M4")

    print(metadata1)
    print(metadata3)

    metaed1 = META1(session, v1, metadata1)
    print(metaed1)

    try:
        metaed2 = META1(session, v2, metadata1)
        raise Exception("Should not happen")
    except IntegrityError:
        print("Normal break of metadated object unicity (metadata)")
        session.rollback()

    metaed3 = META1(session, v1, metadata2)
    print(metaed3)

    metaed4 = META1(session, v1, metadata3)
    print(metaed4)

    metaed5 = META1(session, v2)
    metaed6 = META1(session, metadata2)
    metaed7 = META1(session, v1)

    print(metaed1.object)
    print(metaed5.object)
    print(metaed6.object)
    print(metaed7.object)

    print(metaed1.metadata_object)
    print(metaed5.metadata_object)
    print(metaed6.metadata_object)

    try:
        print(metaed7.metadata_object)
    except MultipleResultsFound:
        print("Normal metadata multiple so exception raised")
        session.rollback()

    metaed5.metadata_object = metadata4
