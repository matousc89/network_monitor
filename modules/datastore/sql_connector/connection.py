from sqlalchemy.sql import func, exists
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import sqlite3 #  i have added this if you find better way to handle databases, you can remove it

from settings import DATASTORE_DATABASE
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.models import make_tables, init_data
from modules.sql_connector import CommonSqlConnector
from modules.datastore.data_validation import DataValidation

class SqlConnection(CommonSqlConnector):
    def __init__(self):
            """
            Init the sql connector (connect, prepare tables).
            """
            engine = db.create_engine('sqlite:///{}'.format(DATASTORE_DATABASE), echo=False)
            make_tables(engine)
            init_data(engine)
            self.sessions = sessionmaker(engine)

    def getSession(self):
        return self.sessions