from sqlalchemy import Column, Integer, UniqueConstraint

from persistent.base import Base

from .common import CommonMethodBase


class Range(Base, CommonMethodBase):

    __tablename__ = 'range'

    id = Column(Integer, primary_key=True)
    min = Column(Integer)
    max = Column(Integer)

    __table_args__ = (UniqueConstraint('min', 'max', name='unique_range'), )

    def __init__(self, *args, **argv):
        if 'min' in argv and 'max' in argv:
            assert argv['min'] < argv['max'], "Range min must be inferior to range max"
        super().__init__(*args, **argv)

    def __repr__(self):
        return f'[{self.min},{self.max}]'
