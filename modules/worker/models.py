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
    next_run = Column(Integer)

    def values(self):
        return {
            "ip_address": self.ip_address,
            "active": self.active,
            "frequency": self.frequency,
            "task": self.task,
            "next_run": self.next_run,
            "last_run": self.last_run,
        }


def make_tables(engine):
    """
    Crate tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)