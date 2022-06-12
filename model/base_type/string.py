from sqlalchemy import Column, String as _String

from model._implem import BaseType


STRING_SIZE = 256

class String(BaseType):

    __tablename__ = f'string'

    id = Column(_String(STRING_SIZE), primary_key = True)
