from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import and_, delete
from sqlalchemy.orm import relationship, reconstructor

from model._implem import BaseType, BaseChangeClassName
from model.metadata import metaclass_for_metadata
from model.type_system import register_type
from model.base_type import STRING_SIZE


class TEST(BaseType):

    __tablename__ = "test"

    alias = Column(String(STRING_SIZE), primary_key=True)
    target_type = Column(String(STRING_SIZE), nullable=False)

    def __init__(self, *args, **argv):
        print(self)
        print(args)
        print(argv)
        return super(TEST, self).__init__(*args, **argv)
    
    @reconstructor
    def init_on_load(self, *args, **argv):
        print(args)
        print(argv)
        print(self.alias)
        print(self.target_type)


if __name__ == "__main__":
    from model_to_disk import create_session
    from model.base_type import BasicEntity, STRING_SIZE

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
