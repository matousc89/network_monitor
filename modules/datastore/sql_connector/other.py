"""
takes care of the connection to the database
"""
from sqlalchemy.sql import func, exists
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import sqlite3 #  i have added this if you find better way to handle databases, you can remove it

from settings import DATASTORE_DATABASE
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.models import make_tables
from modules.sql_connector import CommonSqlConnector
from modules.datastore.data_validation import DataValidation

class SqlOther(CommonSqlConnector):
    """
    Extra sql operations required for Datastore.
    """

    def __init__(self, db_connection):
        self.sessions = db_connection

    def clear_all_tables(self):
        """
        Clear content from tables (for testing purposes mainly).
        """
        with self.sessions.begin() as session:
            session.query(Task).delete()
            session.query(Response).delete()
            session.query(Address).delete()
    def sync_worker(self, data):
        """
        Sync worker - store responses and return tasks
        """
        worker_id = self.get_worker(data["api"])

        if worker_id is not None:
            with self.sessions.begin() as session:
                for response in data["responses"]:
                    result = Response(
                        address=response["address"],
                        time=response["time"],
                        value=response["value"],
                        task=response["task"],
                        worker=worker_id
                    )
                    session.add(result)
                    # TODO alter task last update

                ##tasks = session.query.filter(Task.worker == worker_id)
                tasks = session.query(Task).join(Task, Worker.task).filter(Worker.id == worker_id)
                #tasks = session.query(Worker).filter(Worker.task.contains(task)).all()
                #tasks = session.query(Task).filter(Task.worker_id == worker_id)
                return [item.__dict__ for item in tasks.all()] # TODO make custom function in Task class (instead of __dict__)

    def get_worker(self, token):
        try:
            with self.sessions.begin() as session:
                result = session.query(Worker).filter(Worker.token == token).one()
                return result.id
        except:
            return None

    def get_workers(self):
        try:
            with self.sessions.begin() as session:
                result = session.query(Worker)
                return [item.__dict__ for item in result.all()]
        except:
            return None

    