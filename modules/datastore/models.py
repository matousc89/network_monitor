from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

from modules.models import BaseTask, BaseResponse

Base = declarative_base()

class Response(BaseResponse, Base):
    """
    Outcome of any task/test/measurement.
    """
    worker = Column(String(100))


class Task(BaseTask, Base):
    """
    Definition of task.
    """
    worker = Column(String(100))


def make_tables(engine):
    """
    Crate tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)
