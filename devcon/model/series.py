from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, Text, Date, DateTime
from devcon.model import DeclarativeBase, metadata, DBSession

class Series(DeclarativeBase):
    __tablename__ = 'series'

    uid = Column(Integer, primary_key=True)
    title = Column(Unicode(255))
    date = Column(Date())
    current = Column(Integer)
    status = Column(Unicode(32))
