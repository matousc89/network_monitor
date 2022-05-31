"""
takes care of the connection to the database
"""
import logging
import time

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from settings import WORKER_DATABASE
from settings import LOG
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
        Init the sql connector (connect, prepare tables, setup logging).
        """
        self.worker = worker
        logging.basicConfig(filename=LOG, encoding='utf-8', level=logging.DEBUG)
        engine = db.create_engine('sqlite:///{}'.format(WORKER_DATABASE), echo=False)
        make_tables(engine)
        self.sessions = sessionmaker(engine)

    def clear_all_tables(self):
        """
        Clear content from tables (for testing purposes mainly).
        """
        with self.sessions.begin() as session:
            session.query(Task).delete()
            session.query(Response).delete()

    def add_response(self, ip_address, time, value, task):
        """
        write response of tested address to db
        """
        result = Response(
            ip_address=ip_address,
            time=int(time),
            value=int(value),
            task=task,
            worker=self.worker
        )
        with self.sessions.begin() as session:
            session.add(result)

    def update_all_tasks(self, tasks):
        """Manage incoming tasks from datastore.

        New tasks are created.
        Already existing tasks are annotated with current timestamp and updated.
        Stored tasks without current timestamp are deleted.
        """
        active_stamp = ms_time()
        with self.sessions.begin() as session:
            for incoming_task in tasks:
                existing_task = session.query(Task).filter(
                    Task.ip_address == incoming_task["ip_address"],
                    Task.task == incoming_task["task"]
                ).first()
                if existing_task is not None:
                    existing_task.frequency = incoming_task["frequency"]
                    existing_task.active = active_stamp
                else:
                    new_task = Task(
                        ip_address=incoming_task["ip_address"],
                        task=incoming_task["task"],
                        frequency=incoming_task["frequency"],
                        active=active_stamp,
                    )
                    session.add(new_task)
            session.query(Task).filter(Task.active < active_stamp).delete()

    def update_task(self, task_data):
        """Update information about execution of the given task.
        """
        with self.sessions.begin() as session:
            task = session.query(Task).filter(
                Task.ip_address == task_data["ip_address"],
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
            ip_address=response["ip_address"],
            time=response["last_run"],
            value=response["value"],
            task=response["task"],
            synced=False,
        )
        with self.sessions.begin() as session:
            session.add(result)

    def get_unsynced_responses(self):
        with self.sessions.begin() as session:
            query = session.query(Response).filter(Response.synced == False)
            return [item.sync_values() for item in query.all()]

    def mark_responses_as_synced(self, responses):
        id_list = [item["id"] for item in responses]
        with self.sessions.begin() as session:
            session.query(Response).filter(
                Response.id.in_(id_list)).update({Response.synced: True})
