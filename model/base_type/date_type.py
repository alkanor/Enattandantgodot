from sqlalchemy import Column, DateTime

from model.base import Base

from .common import CommonMethodBase


class Date(Base, CommonMethodBase):

    __tablename__ = 'datetime'

    id = Column(DateTime, primary_key=True)
