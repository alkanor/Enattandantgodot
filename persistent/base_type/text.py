from sqlalchemy import Column, Text as _Text

from persistent.base import Base

from .common import CommonMethodBase


class Text(Base, CommonMethodBase):

    __tablename__ = 'text'

    id = Column(_Text, primary_key=True)
