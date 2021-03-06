"""
takes care of the connection to the database
"""
from sqlalchemy.sql import func
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from settings import DATASTORE_DATABASE
from modules.datastore.models import Response, Task, Address
from modules.datastore.models import make_tables
from modules.sql_connector import CommonSqlConnector

class DatastoreSqlConnector(CommonSqlConnector):
    """
    Extra sql operations required for Datastore.
    """

    def __init__(self):
        """
        Init the sql connector (connect, prepare tables).
        """
        engine = db.create_engine('sqlite:///{}'.format(DATASTORE_DATABASE), echo=False)
        make_tables(engine)
        self.sessions = sessionmaker(engine)

    # def get_all_addr(self):
    #     """
    #     Get all unique addresses
    #     """
    #     with self.sessions.begin() as session:
    #         result = list(session.query(Response.ip_address).distinct())
    #     return result

    def add_response(self, ip_address, time, value, task, worker):
        """
        write response of tested address to db
        """ # TODO update last time of task
        # TODO obsolete since worker sync
        result = Response(
            ip_address=ip_address,
            time=int(time),
            value=int(value),
            task=task,
            worker=worker
        )
        with self.sessions.begin() as session:
            session.add(result)

    def get_avrg_response_all(self, date_from=None, date_to=None):
        """
        generate JSON of average response time of each ip addresses, dateFrom and dateTo are optional
        """ # TODO time selection
        outcome = []
        with self.sessions.begin() as session:
            for item in session.query(Response.ip_address).distinct():
                address = item[0]
                # TODO optimize query
                value = session.query(func.avg(Response.value)).filter(Response.ip_address == address).one()[0]
                outcome.append({"address": address, "value": int(value)})
        return outcome

    def get_response_summary(self, worker=False, time_from=False, time_to=False):
        """
            get info is detailed list of addresses (generate: number of addr records,
            first time testing, last time testing and average responsing time)
            # TODO filter by worker and task
        """
        outcome = []
        with self.sessions.begin() as session:
            for item in session.query(Response.ip_address).distinct():
                address = item[0]
                query = session.query(Response).filter(Response.ip_address == address)
                if worker:
                    query = query.filter(Response.worker == worker)
                if time_from:
                    query = query.filter(Response.time > time_from)
                if time_to:
                    query = query.filter(Response.time < time_to)
                outcome.append({
                    "ip_address": address,
                    "first_response": query.order_by(Response.time).first().time,
                    "last_response": query.order_by(Response.time.desc()).first().time,
                    "average": query.with_entities(func.avg(Response.value)).one()[0],
                    "count": query.count()
                })
        return {"status": "Ok", "data": outcome}

    def get_worker_tasks(self, worker):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            query = session.query(Task).filter(Task.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO make custom function in Task class (instead of __dict__)

    def sync_worker(self, data):
        """
        Sync worker - store responses and return tasks
        """
        with self.sessions.begin() as session:
            for response in data["responses"]:
                result = Response(
                    ip_address=response["ip_address"],
                    time=response["time"],
                    value=response["value"],
                    task=response["task"],
                    worker=data["worker"]
                )
                session.add(result)
                # TODO alter task last update

            tasks = session.query(Task).filter(Task.worker == data["worker"])
            return [item.__dict__ for item in tasks.all()] # TODO make custom function in Task class (instead of __dict__)

    def clear_all_tables(self):
        """
        Clear content from tables (for testing purposes mainly).
        """
        with self.sessions.begin() as session:
            session.query(Task).delete()
            session.query(Response).delete()
            session.query(Address).delete()

    def get_responses(self, worker=False, task="ping"):
        """
        Return list of responses.
        """
        with self.sessions.begin() as session:
            query = session.query(Response).filter(Response.task == task)
            if worker:
                query.filter(Response.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO custom function

    def update_address(self, address_data):
        """
        Update address. If address does not exist, create it.
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.ip_address == address_data["ip_address"]).first()
            if address is None:
                address = Address(
                    ip_address=address_data["ip_address"],
                )
                session.add(address)
                status = {"status": "Created"}
            else:
                status = {"status": "Updated"}
            data_keys = ["location", "latitude", "longitude", "note"]
            for key in data_keys:
                if key in address_data:
                    setattr(address, key, address_data[key])
            return status

    def delete_address(self, address_data):
        """
        Delete address if exists - according ip address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.ip_address == address_data["ip_address"]).first()
            if address is None:
                return {"status": "Not found"}
            else:
                session.delete(address)
                return {"status": "Deleted"}

    def get_address(self, ip_address):
        """
        Get information about IP address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.ip_address == ip_address).first()
            if address is None:
                return {"status": "Not found"}
            else:
                return {"status": "Ok", "data": address.values()}

    def get_address(self, ip_address):
        """
        Get information about IP address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.ip_address == ip_address).first()
            if address is None:
                return {"status": "Not found"}
            else:
                return {"status": "Ok", "data": address.values()}

    def get_all_addresses(self):
        """
        Return all addresses
        """
        with self.sessions.begin() as session:
            query = session.query(Address)
            return {"status": "Ok", "data": [item.values() for item in query.all()]}
