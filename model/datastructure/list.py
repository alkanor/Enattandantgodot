from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import and_, delete
from sqlalchemy.orm import relationship

from model.metadata.named_date_metadata import NAMED_DATE_METADATA
from model.base.baseclass_metadata import baseclass_for_metadata
from model.base import BaseAndMetaChangeClassName
from model.type_system import register_type


__objectname__ = "LIST"


def _LIST_DEPENDANCIES(SQLAlchemyBaseType, MetadataType=None, *additional_args_to_construct_metadata):

    if not MetadataType:
        MetadataClass = NAMED_DATE_METADATA(__objectname__)
    else:
        MetadataClass = MetadataType(__objectname__, *additional_args_to_construct_metadata)
    
    metaclass_tablename = MetadataClass.__tablename__
    entrytype_tablename = f'{__objectname__}<{MetadataClass.__slug__},{SQLAlchemyBaseType.__tablename__}>'

    return metaclass_tablename, entrytype_tablename


@register_type(__objectname__, _LIST_DEPENDANCIES)
def LIST(SQLAlchemyBaseType, MetadataType=None, *additional_args_to_construct_metadata):

    metaclass_tablename, entrytype_tablename = _LIST_DEPENDANCIES(SQLAlchemyBaseType, MetadataType=None, *additional_args_to_construct_metadata)

    if not MetadataType:
        MetadataClass = NAMED_DATE_METADATA(__objectname__)
    else:
        MetadataClass = MetadataType(__objectname__, *additional_args_to_construct_metadata)

    assert(metaclass_tablename == MetadataClass.__tablename__)


    class _LIST_ENTRY(BaseAndMetaChangeClassName(SQLAlchemyBaseType, MetadataClass)[0]):

        __tablename__ = entrytype_tablename
        __basetype__ = SQLAlchemyBaseType

        id = Column(Integer, primary_key=True)
        metadata_id = Column(Integer, ForeignKey(MetadataClass.id), nullable=False)
        entry_id = Column(Integer, ForeignKey(SQLAlchemyBaseType.id), nullable=False)

        @declared_attr
        def metadataobj(cls):
            return relationship(MetadataClass, foreign_keys=[cls.metadata_id])
        
        @declared_attr
        def entry(cls):
            return relationship(SQLAlchemyBaseType, foreign_keys=[cls.entry_id])
        
        def __repr__(self):
            return f'{self.entry}'


    class _LIST(baseclass_for_metadata(MetadataClass)):

        __entrytype__ = _LIST_ENTRY
        __tablename__ = entrytype_tablename # not a real SQLAlchemy table but to ease table creation


        def __init__(self, session, *args, **argv):
            if args:
                assert(type(args[0]) == self.__metadataclass__)
                self.metadata = args[0]
            else:
                self.metadata = MetadataClass.GET_CREATE(session, **argv)
            self.entries_initialized = False
            self._entries = []
            self._session_saved = session


        # lazy load list entries when needed, otherwise only the metadata suffices
        @property
        def entries(self):
            if not self.entries_initialized:
                self.entries_initialized = True
                self._entries = self._session_saved.query(_LIST_ENTRY).filter_by(metadata_id=self.metadata.id).all()
            return self._entries

        @entries.setter
        def entries(self, new_entries):
            self._entries = new_entries

        @entries.deleter
        def entries(self):
            self.entries_initialized = False
            self.entries = []


        def add(self, session, element, commit=True):
            assert(element.__class__ == SQLAlchemyBaseType)
            self._session_saved = session
            if element.id:
                new_item = _LIST_ENTRY(metadataobj=self.metadata, entry_id=element.id)
            else:
                session.add(element)
                new_item = _LIST_ENTRY(metadataobj=self.metadata, entry=element)
            self.entries.append(new_item)
            session.add(new_item)
            if commit:
                session.commit()
        
        def add_many(self, session, elements, commit=True, commit_every_n=10000):
            assert(all([element.__class__ == SQLAlchemyBaseType for element in elements]))
            self._session_saved = session
            for i, element in enumerate(elements):
                if element.id:
                    new_item = _LIST_ENTRY(metadataobj=self.metadata, entry_id=element.id)
                else:
                    new_item = _LIST_ENTRY(metadataobj=self.metadata, entry=element)
                self.entries.append(new_item)
                session.add(new_item)
                if (i+1)%commit_every_n == 0:
                    session.commit()
            if commit:
                session.commit()
        
        def delete(self, session, element):
            assert(any(map(lambda x: x.entry_id == element.id, self.entries)))
            assert(element.__class__ == SQLAlchemyBaseType)
            self._session_saved = session
            statement = delete(_LIST_ENTRY).where(and_(_LIST_ENTRY.metadata_id == self.metadata.id, _LIST_ENTRY.entry_id == element.id))
            session.execute(statement)
            session.commit()
            self.entries = [x for x in self.entries if x.entry_id != element.id]

        def delete_many(self, session, elements, cut_by_chunks=10000):
            entries_id = set(map(lambda x: x.entry_id, self.entries))
            elements_id = set(map(lambda x: x.id, elements))
            assert(entries_id.intersection(elements_id) == elements_id)
            assert(all(map(lambda x: x.__class__ == SQLAlchemyBaseType, elements)))
            self._session_saved = session
            for i in range(0, len(elements), cut_by_chunks):
                statement = delete(_LIST_ENTRY).where(and_(_LIST_ENTRY.metadata_id == self.metadata.id, _LIST_ENTRY.entry_id.in_(list(map(lambda x: x.id, elements[i:i+cut_by_chunks])))))
                session.execute(statement)
                session.commit()
            self.entries = [x for x in self.entries if x.entry_id not in elements_id]

        def clear(self, session):
            self._session_saved = session
            statement = delete(_LIST_ENTRY).where(_LIST_ENTRY.metadata_id == self.metadata.id)
            session.execute(statement)
            session.commit()
            MetadataClass.DELETE(session, id=self.metadata.id)
            self.entries = []

        def __repr__(self):
            return f'{self.metadata} : {self.entries}'

    return _LIST



if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String


    columns = {
        "id": Column(Integer, primary_key=True),
        "value": Column(String(STRING_SIZE), unique=True),
        "ADD": Column(Integer, default=666),
    }

    Test = BasicEntity("bak2basics", columns)

    session = create_session()

    v1 = Test.GET_CREATE(session, value="bonjour1")
    v2 = Test.GET_CREATE(session, value="bonjour2")
    v3 = Test.GET_CREATE(session, value="bonjour3")
    v4 = Test.GET_CREATE(session, value="bonjour4")


    LIST_TYPE = LIST(Test)

    before = session.query(LIST_TYPE.__metadataclass__).all()
    print(before)
    for i in before:
        try:
            LIST_TYPE.DELETE(session, i)
        except Exception as e:
            session.rollback()
            print(f"No delete {e}")


    mylist1 = LIST_TYPE(session, name="superlist1")
    mylist2 = LIST_TYPE(session, name="superlist2")

    mylist1.add(session, v1)
    mylist1.add(session, v2)
    mylist1.add(session, v3)
    mylist1.add(session, v4)

    mylist2.add_many(session, [v1, v2, v4])

    print(mylist1)
    print(mylist2)

    mylist2.delete(session, v2)
    print(mylist2)

    try:
        mylist2.delete(session, v2)
        raise Exception("Should not happen")
    except AssertionError as e:
        print("deletion threw exception cause elem not existing")
    print(mylist2)

    mylist1.delete_many(session, [v1, v4])
    print(mylist1)

    print(mylist1.__metadataclass__.name)

    print(LIST_TYPE.GET_COND(session, LIST_TYPE.__metadataclass__.name.like("superlist%")))
    print(LIST_TYPE.GET_COND(session, LIST_TYPE.__metadataclass__.name.like("%2")))


    LIST_TYPE2 = LIST(Test) # just check unicity of type views
    mylist3 = LIST_TYPE(session, name="superlist3")
    mylist4 = LIST_TYPE(session, name="superlist1")

    print(mylist4)

    mylist3.add_many(session, [v2, v3, v4])
    mylist4.add_many(session, [v1, v2, v3, v3, v4])

    print(mylist3)
    print(mylist4)
    print(mylist1)

    try:
        statement = delete(LIST_TYPE.__metadataclass__)
        session.execute(statement)
        session.commit()
        raise Exception("Should not happen")
    except IntegrityError:
        print("Normal IntegrityError for deletion of foreign keys")
        session.rollback()