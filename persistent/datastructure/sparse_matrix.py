from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import and_, delete
from sqlalchemy.orm import relationship, reconstructor

from persistent.base import Base
from persistent.type_system import register_type
from persistent.base_type import STRING_SIZE


class TEST(Base):
    __tablename__ = "test"

    alias = Column(String(STRING_SIZE), primary_key=True)
    target_type = Column(String(STRING_SIZE), nullable=False)

    def __init__(self, *args, **argv):
        print("basic init")
        print(self)
        print(args)
        print(argv)
        return super().__init__(*args, **argv)

    @reconstructor
    def init_on_load(self, *args, **argv):
        print("init on load")
        print(args)
        print(argv)
        print(self.alias)
        print(self.target_type)


class TEST2(Base):
    __tablename__ = "test2"

    i = Column(Integer, primary_key=True)
    t = Column(Integer, ForeignKey(TEST.alias), nullable=False)
    rel = relationship(TEST, foreign_keys=[t])


if __name__ == "__main__":
    from persistent_to_disk import create_session
    from persistent.base_type import BasicEntity, STRING_SIZE

    from sqlalchemy.orm.exc import FlushError
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import String

    session = create_session()

    try:
        d = TEST(alias="okok", target_type="ppp")
        session.add(d)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()

    print("now")
    e = session.query(TEST).filter_by(alias="okok").one_or_none()
    print(e.target_type)

    print(session.query(TEST).filter_by(alias="okok").one_or_none())
    print(session.query(TEST).filter_by(alias="okok").one_or_none())
    print(session.query(TEST).filter_by(alias="okok").one_or_none() == session.query(TEST).filter_by(alias="okok").one_or_none())

    d2 = TEST(alias='pp', target_type='oo')
    t2 = TEST2(rel=d2)
 #   session.add(d2)
 #   session.commit()
    session.add(t2)
    session.commit()
    print(t2.rel.alias)
