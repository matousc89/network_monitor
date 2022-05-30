from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

from modules.models import BaseTask, BaseResponse

Base = declarative_base()

class Response(BaseResponse, Base):
    """
    Outcome of any task/test/measurement.
    """
    synced = Column(Boolean)


class Task(BaseTask, Base):
    """
    Definition of task.
    """
    active = Column(Integer)
    # frequency = Column(Integer)
    # last_run = Column(Integer)
    # next_run = Column(Integer) # TODO purge

    def values(self):
        return {
            "ip_address": self.ip_address,
            "active": self.active,
            "frequency": self.frequency,
            "task": self.task,
        }


def make_tables(engine):
    """
    Crate tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)