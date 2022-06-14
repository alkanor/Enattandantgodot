from sqlalchemy import Column, Text as _Text

from model._implem import BaseType


class Text(BaseType):

    __tablename__ = f'text'

    id = Column(_Text, primary_key=True)
