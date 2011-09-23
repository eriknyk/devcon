from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, Text, Date, DateTime
from devcon.model import DeclarativeBase, metadata, DBSession

class Submits(DeclarativeBase):
    __tablename__ = 'submits'

    user_id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, primary_key=True)
    user_name = Column(Unicode(16))
    problem_title = Column(Unicode(255))
    datetime = Column(DateTime())
    attempt = Column(Integer, primary_key=True)
    filename = Column(Unicode(255))
    output_filename = Column(Unicode(255))
    submit_filename = Column(Unicode(255))
    result = Column(Unicode(255))
    comments = Column(Unicode(255))
    serie = Column(Integer)
    accepted = Column(Integer)
    
