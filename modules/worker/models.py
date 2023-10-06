from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Boolean

from modules.models import BaseTaskWorker, BaseResponse

Base = declarative_base()

class Response(BaseResponse, Base):
    """
    Outcome of any task/test/measurement.
    """
    synced = Column(Boolean)

    def sync_values(self):
        return {
            "id": self.id,
            "address": self.address,
            "task": self.task,
            "time": self.time,
            "value": self.value
        }


class Task(BaseTaskWorker, Base):
    """
    Definition of task.
    """
    active = Column(Integer)
    next_run = Column(Integer, default=0)

    def values(self):
        return {
            "address": self.address,
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
