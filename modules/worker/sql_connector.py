"""
takes care of the connection to the database
"""
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from settings import WORKER_DATABASE
from modules.worker.models import Response, Task
from modules.worker.models import make_tables
from modules.sql_connector import CommonSqlConnector
from modules.common import ms_time

class WorkerSqlConnector(CommonSqlConnector):
    """
    Extra sql operations required for Worker.
    """

    def __init__(self, worker):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.worker = worker
        engine = db.create_engine(f'sqlite:///{WORKER_DATABASE}', echo=False)
        make_tables(engine)
        self.sessions = sessionmaker(engine)

    def clear_all_tables(self):
        """
        Clear content from tables (for testing purposes mainly).
        """
        with self.sessions.begin() as session:
            session.query(Task).delete()
            session.query(Response).delete()

    def update_task(self, task_data):
        """Update information about execution of the given task.
        """
        with self.sessions.begin() as session:
            task = session.query(Task).filter(
                Task.address == task_data["address"],
                Task.task == task_data["task"]
            ).first()
            task.next_run = task_data["next_run"]
            task.last_run = task_data["last_run"]

    def get_tasks(self):
        """
        Get all tasks.
        """
        with self.sessions.begin() as session:
            query = session.query(Task)
            return [item.values() for item in query.all()]

    def add_response(self, response):
        """
        write response of tested address to database
        """
        result = Response(
            address=response["address"],
            time=response["time"],
            value=response["value"],
            task=response["task"],
            synced=False,
        )
        with self.sessions.begin() as session:
            session.add(result)

    def reset_tasks(self):
        """Reset tasks times on startup of application.
        """
        with self.sessions.begin() as session:
            session.query(Task).update({Task.last_run: 0, Task.next_run: 0})

    def presync(self):
        """Function called before synchronization with datastore

        Should select responses that should be sent to datastore.
        """
        with self.sessions.begin() as session:
            query = session.query(Response).filter(Response.synced == False)
            return [item.sync_values() for item in query.all()]

    def postsync(self, tasks, responses):
        """Function called after synchronization with datastore

        Tasks:
        - New tasks are created.
        - Already existing tasks are annotated with current timestamp and updated.
        - Stored tasks without current timestamp are deleted.

        Responses are marked as synced.
        """
        active_stamp = ms_time()
        with self.sessions.begin() as session:
            if responses:
                id_list = [item["id"] for item in responses]
                session.query(Response).filter(
                    Response.id.in_(id_list)).update({Response.synced: True})

            for incoming_task in tasks:
                existing_task = session.query(Task).filter(
                    Task.address == incoming_task["address"],
                    Task.task == incoming_task["task"]
                ).first()
                if existing_task is not None:
                    existing_task.frequency = incoming_task["frequency"]
                    existing_task.active = active_stamp
                else:
                    new_task = Task(
                        address=incoming_task["address"],
                        task=incoming_task["task"],
                        frequency=incoming_task["frequency"],
                        active=active_stamp,
                    )
                    session.add(new_task)
            session.query(Task).filter(Task.active < active_stamp).delete()
