from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey, delete
from sqlalchemy.orm import relationship, reconstructor

from persistent.base import Base, BaseAndMetaChangeClassName, baseclass_for_sqlalchemy_with_subclass
from persistent.type_system import register_type
from persistent.base_type import STRING_SIZE


class ALIAS_METADATA(Base):

    __tablename__ = "alias"

    alias = Column(String(STRING_SIZE), primary_key=True)
    target_type = Column(String(STRING_SIZE), nullable=False)


_alias_cache = {}
def _update_metadata(session, aliastype):
    filter = {
                "alias": aliastype.__tablename__,
                "target_type":  aliastype.__basetype__.__tablename__
            }

    if not _alias_cache:
        all_aliases = session.query(ALIAS_METADATA).all()
        _alias_cache.update({a.alias: a.target_type for a in all_aliases})

    if filter["alias"] not in _alias_cache:
        existing = session.query(ALIAS_METADATA).filter_by(**filter).one_or_none()
        if not existing:
            new_alias = ALIAS_METADATA(**filter)
            session.add(new_alias)
            session.commit()
        _alias_cache[filter["alias"]] = filter["target_type"]



@register_type("ALIAS", lambda basetype, alias_name: (basetype.__tablename__, alias_name))
def ALIAS(SQLAlchemyBaseType, alias_name):

    is_base_sqlalchemy_type = SQLAlchemyBaseType.__dict__.get("id", None) is not None # this condition may not be the best to differentiate SQLAlchemy classes and non-sqlalchemy ones
    base_type = SQLAlchemyBaseType if is_base_sqlalchemy_type else SQLAlchemyBaseType.__metadataclass__ # but this will throws an error if non SQLAlchemy class is not metadata one
    have_get_method = SQLAlchemyBaseType.__dict__.get("GET_CREATE", None) is not None

    class _ALIAS(BaseAndMetaChangeClassName(SQLAlchemyBaseType)[0], baseclass_for_sqlalchemy_with_subclass(base_type, "orm_obj")):

        __basetype__ = base_type
        __tablename__ = alias_name

        id = Column(Integer, primary_key=True)
        alias_id = Column(Integer, ForeignKey(base_type.id), nullable=False, unique=True)

        @declared_attr
        def orm_obj(cls):
            return relationship(base_type, foreign_keys=[cls.alias_id])

        # create an alias from an already existing element or a potential element:
        #  - if the element already exists, either it is provided as the target, or it is gotten by GET_CREATE method of subtype, or manually if basic SQLAlchemy class
        #  - if not, either it will fail if provided directly, or it will be created within the GET_CREATE, or manually if basic SQLAlchemy class (avoid it because not performant)
        def __init__(self, session, *args, **argv):
            _update_metadata(session, self.__class__)
            if args:
                assert(type(args[0]) == SQLAlchemyBaseType or (not is_base_sqlalchemy_type and type(args[0]) == base_type))
                if type(args[0]) == SQLAlchemyBaseType:
                    self.target = args[0]
                    self.orm_obj = self.target
                else: # the only possibility here is to have is_base_sqlalchemy_type = false, so base_type = metadata type and the provided argument is the metadata, so the orm obj
                    self.orm_obj = args[0]
                    self.target = SQLAlchemyBaseType(session, self.orm_obj)
            else:
                if have_get_method:
                    self.target = SQLAlchemyBaseType.GET_CREATE(session, **argv)
                    if is_base_sqlalchemy_type:
                        self.orm_obj = self.target
                    else:
                        self.orm_obj = self.target.metadata
                else:
                    self.orm_obj = session.query(base_type).filter_by(**argv).one_or_none()
                    if not self.orm_obj:
                        self.orm_obj = base_type(**argv)
                        session.add(self.orm_obj)
                        session.commit()
                    
                    if is_base_sqlalchemy_type:
                        self.target = self.orm_obj
                    else:
                        self.target = SQLAlchemyBaseType(session, self.orm_obj)

            self.copy_aliased_attributes()
            
            super().__init__(alias_id=self.target.id if is_base_sqlalchemy_type else self.target.metadata.id)

        @reconstructor
        def init_on_load(self):
            if is_base_sqlalchemy_type:
                assert(self.orm_obj.__class__ == SQLAlchemyBaseType)
                self.target = self.orm_obj
            else:
                self.target = SQLAlchemyBaseType(session, self.orm_obj)
            self.copy_aliased_attributes()
        
        def copy_aliased_attributes(self):
            for k, v in self.target.__dict__.items():
                if k not in self.__dict__ and k != 'id':
                    setattr(self, k, v)
                    #print(f"Attr {k} not in new obj, adding it => {v}")

        def __repr__(self):
            return f'ALIAS ({alias_name}, id={self.id}) [{self.target}]'

        def clear(self, session):
            statement = delete(_ALIAS).where(_ALIAS.alias_id == self.alias_id)
            session.execute(statement)
            session.commit()

    # copying the target attributes for calling them on the alias
    for attr in SQLAlchemyBaseType.__dict__:
        if attr not in dir(_ALIAS) and attr != 'id':
            #print(f"Attr {attr} not in new obj, adding it => {SQLAlchemyBaseType.__dict__[attr]}")
            setattr(_ALIAS, attr, SQLAlchemyBaseType.__dict__[attr])

    return _ALIAS





if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy.exc import IntegrityError, InvalidRequestError
    from sqlalchemy import String


    columns = {
        "id": Column(Integer, primary_key=True),
        "vv": Column(String(STRING_SIZE), unique=True),
        "xx": Column(Integer, default=666),
    }

    Test = BasicEntity("bak3basics", columns)

    session = create_session()

    HOST = ALIAS(Test, "HOST")

    v1 = HOST.GET_CREATE(session, vv="jour1")
    v2 = HOST.GET_CREATE(session, vv="jour2")
    v3 = HOST.GET_CREATE(session, vv="jour3")
    v4 = HOST.GET_CREATE(session, vv="jour4")
    v5 = Test.GET_CREATE(session, vv="jour5")

    host1 = HOST(session, vv="12")
    try:
        host2 = HOST(session, vv="12", xx=1020)
        raise Exception("Should not happen")
    except IntegrityError as e:
        session.rollback()
        print("adding element vv=12,xx=1020 is not ok since searching it returns none and adding it break unicity constraint for v=12")
    host3 = HOST(session, vv="12")

    try:
        session.add(host1)
        #session.add(host3) # returned the same as host1
        session.commit()
    except:
        print("If failed here, maybe because host was added previously")
        session.rollback()

    print(host1.vv)
    print(host1.xx)

    print(v1, v2, v3, v4, v5)

    from_bad = HOST(session, v5)
    print(from_bad)
    try:
        session.add(from_bad)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        print("May have been previously added")

    from .list import LIST

    HOSTLIST = LIST(HOST)
    HOST_GROUP = ALIAS(HOSTLIST, "HOST_GROUP")

    mylist1 = HOSTLIST(session, name="superlist1")
    mylist2 = HOSTLIST(session, name="superlist2")

    hostgroup1 = HOST_GROUP.GET_CREATE(session, name="mylist")
    hostgroup2 = HOST_GROUP.GET_CREATE(session, name="mylist")
    hostgroup3 = HOST_GROUP.GET_CREATE(session, name="mylist2")

    mylist1.add(session, HOST.GET_CREATE(session, vv="jourXX"))
    hostgroup1.add(session, v1)
    try:
        hostgroup1.add(session, v5)
        raise Exception("Should not happen")
    except AssertionError as e:
        #session.rollback()
        print("adding Test element instead of HOST is nok ok because of type coherence")

    hostgroup2.add_many(session, [v1, v2, v4])
    print(hostgroup1)
    print(hostgroup2)

    hostgroup3.add(session, v1)
    print(hostgroup3)

    # delete alias then clear the associated object (fk needs to be cleared)
    HOST_GROUP.DELETE(session, id=hostgroup1.id)
    hostgroup1.target.clear(session)

    print(hostgroup1)
    print(hostgroup2)

    print(HOST_GROUP.GET(session, name="mylist"))

    try:
        hostgroup1.add_many(session, [v1, v2])
        raise Exception("Should not happen")
    except InvalidRequestError:
        print("Cannot add many to hostgroup1 as it has been deleted")
        session.rollback()

    hostgroup1 = HOST_GROUP.GET_CREATE(session, name="mylistX")
    HOST_GROUP.DELETE(session, hostgroup1)
    print(hostgroup1)

    hostgroup1 = HOST_GROUP.GET_CREATE(session, name="mylistY")
    HOST_GROUP.DELETE(session, hostgroup1.metadata)
    print(hostgroup1)

    hostgroup1 = HOST_GROUP.GET_CREATE(session, name="mylistZ")
    metadata_from_other = session.query(hostgroup1.target.__metadataclass__).filter_by(id=hostgroup1.target.metadata.id).one_or_none()
    print(metadata_from_other)
    HOST_GROUP.DELETE(session, metadata_from_other)
    print(hostgroup1)
    
    hostgroup3.add_many(session, [v3, v4])

    print(hostgroup2)
    print(hostgroup3)
