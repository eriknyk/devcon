from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, Text, Date
from devcon.model import DeclarativeBase, metadata, DBSession

class Problems(DeclarativeBase):
    __tablename__ = 'problems'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    code = Column(Unicode(2))
    title = Column(Unicode(255))
    text = Column(Text())
    input = Column(Text())
    sample_input = Column(Text())
    output = Column(Text())
    sample_output = Column(Text())
    topic = Column(Unicode(255))
    serie = Column(Integer)
    points = Column(Integer())
    lang = Column(Unicode(2))
    date = Column(Date())
    input_filename = Column(Unicode(255))
