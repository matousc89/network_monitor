"""
Models adjusted for datastore.

TODO: add Worker model - to store its GPS
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, Integer

from modules.models import BaseTask, BaseResponse, BaseItem

Base = declarative_base()

class Response(BaseResponse, Base):
    """
    Outcome of any task/test/measurement.
    """
    worker = Column(String(100))

    def values(self):
        """
        Return values for api client.
        """
        return {
            "address": self.address,
            "task": self.task,
            "time": self.time,
            "value": self.value,
            "worker": self.worker
        }


class Task(BaseTask, Base):
    """
    Definition of task.
    """

    
    worker = Column(String(100))


class Address(BaseItem, Base):
    """
    IP address meta data
    """
    __tablename__ = 'addresses'

    name = Column(String(100))
    location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    note = Column(String(500))

    def values(self):
        """
        Return values for api client.
        """
        return {
            "address": self.address,
            "name": self.name,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "note": self.note,
        }

class Users(Base):
    """
    
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    hashed_password = Column(String(100))
    role = Column(Integer)

    def values(self):
        """
        Return values for api client.
        """
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "role": self.role,
        }

class Worker(Base):
    """
    
    """
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    token = Column(String(100))

    def values(self):
        """
        Return values for api client.
        """
        return {
            "id": self.id,

        }

class WorkerHasTask(Base):
    """
    
    """
    __tablename__ = 'worker_has_task'

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer)
    task_id = Column(Integer)

    def values(self):
        """
        Return values for api client.
        """
        return {
            "id": self.id,

        }

class UserHasWorker(Base):
    """
    
    """
    __tablename__ = 'user_has_worker'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    worker_id = Column(Integer)

    def values(self):
        """
        Return values for api client.
        """
        return {
            "id": self.id,

        }


def make_tables(engine):
    """
    Create tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)
