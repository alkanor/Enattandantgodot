from sqlalchemy import Column, Integer as _Integer

from model.base import Base

from .common import CommonMethodBase


class Integer(Base, CommonMethodBase):

    __tablename__ = 'integer'

    id = Column(_Integer, primary_key=True)
