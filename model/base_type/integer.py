from sqlalchemy import Column, Integer as _Integer

from model._implem import BaseType


class Integer(BaseType):

    __tablename__ = f'integer'

    id = Column(_Integer, primary_key = True)
