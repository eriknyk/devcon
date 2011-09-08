from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, Text, Date, DateTime
from devcon.model import DeclarativeBase, metadata, DBSession

class Results(DeclarativeBase):
    __tablename__ = 'results'

    uid = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    submits = Column(Integer)
    submits_detail = (Unicode(255))
    points = Column(Integer)
    summary = Column(Unicode(255))
    
