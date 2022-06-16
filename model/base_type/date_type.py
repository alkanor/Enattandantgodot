from sqlalchemy import Column, DateTime

from model._implem import BaseType


class Date(BaseType):

    __tablename__ = f'datetime'

    id = Column(DateTime, primary_key=True)
