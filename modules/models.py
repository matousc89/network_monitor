from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Item():
    """
    Attributes common for Response and Task.
    """
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(100))
    worker = Column(String(100))
    task = Column(String(100))


class Response(Item, Base):
    """
    Outcome of any task/test/measurement.
    """
    __tablename__ = 'responses'

    time = Column(Integer)
    value = Column(Integer)


class Task(Item, Base):
    """
    Definition of task.
    """
    __tablename__ = 'tasks'

    frequency = Column(Integer)
    last_run = Column(Integer)
    next_run = Column(Integer) # TODO purge


def make_tables(engine):
    """
    Crate tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)