from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import delete
from sqlalchemy.orm import relationship

from model.metadata.named_date_metadata import NAMED_DATE_METADATA
from model.base.baseclass_metadata import baseclass_for_metadata
from model.base import BaseAndMetaChangeClassName
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
    class _METADATED_ENTRY(ChangeClassNameBase):

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


    class _METADATED_OBJECT(baseclass_for_metadata(MetadataClass)):

        __metadataclass__ = MetadataClass

        def __init__(self, *args, **argv):
            if not args: # no session, so basic sqlalchemy construction
                self.entry = _METADATED_ENTRY(*args, **argv)
                self.update_from_entry()
                return
            else: # at least session in arg, we can automatically setup what is needed for object search according to args types
                session = args[0]
                assert len(args) > 1, "Not enough arguments to construct the metadated type, need at least metadata or base object"
                assert type(session) != MetadataClass and type(session) != SQLAlchemyBaseType, "First argument must be an SQLAlchemy session"

                if len(args) > 2:
                    if type(args[1]) == MetadataClass:  # in this case we must have the third argument type = metadata
                        self.entry = _METADATED_ENTRY(metadataobj=args[1], obj=args[2])
                    else:
                        self.entry = _METADATED_ENTRY(metadataobj=args[2], obj=args[1])
                    self.update_from_entry()
                    already_existing = session.query(_METADATED_ENTRY).filter_by(metadataobj=self._metadata, obj=self._obj).one_or_none()
                    if not already_existing: # persisting the metadated object if not existing as all required data is known
                        session.add(self.entry)
                        session.commit()
                else:
                    if type(args[1]) == MetadataClass:
                        self.entry = _METADATED_ENTRY(metadataobj=args[1])
                    else:
                        self.entry = _METADATED_ENTRY(obj=args[1])
                    self.update_from_entry()
                self._session_saved = session

        def update_from_entry(self):
            self._metadata = self.entry.metadataobj
            self._obj = self.entry.obj

        # lazy load the real object when needed, otherwise only the metadata suffices
        @property
        def object(self):
            if not self.entry.obj: # get the object from its metadata
                existing_entry = self._session_saved.query(_METADATED_ENTRY).join(_METADATED_ENTRY.obj).filter(_METADATED_ENTRY.metadataobj == self.entry.metadataobj).one_or_none()
                if existing_entry:
                    self.entry = existing_entry
                    self.update_from_entry()
            return self._obj

        @object.setter
        def object(self, new_obj):
            self.entry.obj = new_obj
            self._session_saved.add(self.entry)
            try:
                self._session_saved.commit()
            except Exception as e:
                self.entry.obj = None
                self._session_saved.rollback()
                raise e
            self.update_from_entry()

        @object.deleter
        def object(self):
            self.entry.obj = None


        @property
        def metadata(self):
            if not self._metadata: # get the object from its metadata
                existing_entry = self._session_saved.query(_METADATED_ENTRY).join(_METADATED_ENTRY.metadataobj).filter(_METADATED_ENTRY.obj == self.entry.obj).one_or_none()
                if existing_entry:
                    self.entry = existing_entry
                    self.update_from_entry()
            return self._metadata

        @metadata.setter
        def metadata(self, new_metadata):
            if self.entry.metadataobj:
                assert type(new_metadata) == MetadataClass, "Set metadata with badly typed class"
                if not getattr(new_metadata, "id"): # the metadata is not yet persisted, we need it to update the metadated object
                    self._session_saved.add(new_metadata)
                    self._session_saved.commit()
                    assert getattr(new_metadata, "id"), "Committed metadata should have an id"
                print(f"BEFORE {self.entry.metadataobj}")
                session.query(_METADATED_ENTRY). \
                                filter(_METADATED_ENTRY.metadataobj == self.entry.metadataobj). \
                                update({_METADATED_ENTRY.metadata_id: new_metadata.id})
                self.update_from_entry()
            else:
                self.entry.metadataobj = new_metadata
                self._session_saved.add(self.entry)
            try:
                self._session_saved.commit()
                print(f"AFTER {self.entry.metadataobj}")
            except Exception as e:
                self.entry.metadataobj = None
                self._session_saved.rollback()
                raise e

        @metadata.deleter
        def metadata(self):
            self.entry.metadataobj = None


        def clear(self, session):
            self._session_saved = session
            statement = delete(_METADATED_ENTRY).where(_METADATED_ENTRY.metadataobj == self.entry.metadataobj)
            session.execute(statement)
            session.commit()
            MetadataClass.DELETE(session, id=self.entry.metadataobj.id)
            self.entry = _METADATED_ENTRY(obj=None, metadataobj=None)

        def __repr__(self):
            return f'{self.entry.metadataobj} : {self.entry.obj}'

    return _METADATED_OBJECT


if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import BasicEntity, _Integer, _String, STRING_SIZE

    from sqlalchemy.exc import IntegrityError, MultipleResultsFound, InvalidRequestError
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

    theint = _Integer.GET_CREATE(session, id=1928)

    META1 = MetadatedType(Test)
    META2 = MetadatedType(_String, NAMED_DATE_METADATA)
    META3 = MetadatedType(_Integer)

    basic = META3(obj=theint, metadataobj=META3.__metadataclass__.GET_CREATE(session, name="M99"))
    print(basic)
    session.add(basic.entry)
    try:
        session.commit()
    except IntegrityError:
        print("Already added previously")
        session.rollback()

    _NAMED_DATE_METADATA = META1.__metadataclass__
    try:
        print(_NAMED_DATE_METADATA.GET_CREATE(session, name="M1"))
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
    metaed8 = META1.GET_CREATE(session, v4, name="CREATEALLEZMETADATA")

    print("Objects 1 5 6 7 8")
    print(metaed1.object)
    print(metaed5.object)
    print(metaed6.object)
    print(metaed7.object)
    print(metaed8.object)

    print("Meta 1 5 6 8")
    print(metaed1.metadata)
    print(metaed5.metadata)
    print(metaed6.metadata)
    print(metaed8.metadata)

    try:
        print(metaed7.metadata)
    except MultipleResultsFound:
        print("Normal base object multiple so exception raised")
        session.rollback()

    try:
        metaed5.metadata = metadata4
    except IntegrityError:
        print("Normal metadata multiple so exception raised")
        session.rollback()

    metadata5 = _NAMED_DATE_METADATA.NEW(session, name="M5")
    metaed5.metadata = metadata5

    metaed5.metadata = _NAMED_DATE_METADATA(name="M6")

    metaed1.clear(session)
    print(metaed1)

    try:
        metaed1.metadata = _NAMED_DATE_METADATA(name="M7")
        raise Exception("Should not happen")
    except InvalidRequestError:
        print("Setting metadata object only after clear yields transient error")
        session.rollback()
    except IntegrityError as e:
        print("Null constraint failed after object deletion")
        session.rollback()

    metaed1 = META1(session, _NAMED_DATE_METADATA(name="M7"))
    metaed1.object = v3
    print(metaed1)

    try:
        metaed1.metadata = _NAMED_DATE_METADATA.GET_ONE(session, name="M6")
        print("If it went here, we are at iteration 2 since the M6 object was linked one time to the id 7 and v2 bonjour2, but another was added so it got freed and reassociated to v3 bonjour3")
    except IntegrityError as e:
        print("Setting existing metadata object should be prevented")
        session.rollback()
