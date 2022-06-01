from sqlalchemy import Column, Integer, String

class BaseItem():
    """
    Attributes common for Response and Task.
    """
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(100))
    task = Column(String(100))


class BaseResponse(BaseItem):
    """
    Outcome of any task/test/measurement.
    """
    __tablename__ = 'responses'

    time = Column(Integer)
    value = Column(Integer)


class BaseTask(BaseItem):
    """
    Definition of task.
    """
    __tablename__ = 'tasks'

    frequency = Column(String(5))
    last_run = Column(Integer, default=0)


