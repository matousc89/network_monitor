"""
Models adjusted for datastore.

TODO: add Worker model - to store its GPS
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float

from modules.models import BaseTask, BaseResponse, BaseItem

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


def make_tables(engine):
    """
    Crate tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)
