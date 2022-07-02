from sqlalchemy import Column, String as _String

from model.base import Base

from .common import CommonMethodBase


STRING_SIZE = 256

class String(Base, CommonMethodBase):

    __tablename__ = 'string'

    id = Column(_String(STRING_SIZE), primary_key=True)
