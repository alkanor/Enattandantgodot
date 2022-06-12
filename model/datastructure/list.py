from sqlalchemy import Column, Integer, String, ForeignKey

from model._implem import BaseType



def LIST(SQLAlchemyBaseType):

    class _LIST_NAME(BaseType):

        __tablename__ = f'LIST_NAME<{SQLAlchemyBaseType.__tablename__}>'

        id = Column(Integer, primary_key = True)
        name = Column(String(STRING_SIZE), primary_key = True)


    class _LIST(BaseDatastructure):

        __tablename__ = f'LIST<{SQLAlchemyBaseType.__tablename__}>'

        list_ref = Column(Integer, ForeignKey(f'LIST_NAME<{SQLAlchemyBaseType.__tablename__}>.id'))


        def add(self, element):
            pass
        
        def add_many(self, elements):
            pass
        
        def get(self, index_list):
            pass
        
        def delete(self, )