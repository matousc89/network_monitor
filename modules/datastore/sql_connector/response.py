from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.data_validation import DataValidation
from sqlalchemy.sql import func, exists

class SqlResponse(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection

    def get_all(self, time_from, time_to):
        """
        generate JSON of all responses
        """ # TODO time selection

        with self.sessions.begin() as session:
            if time_from!=None and time_to!=None:
                query = session.query(Response).filter(Response.time >= time_from, Response.time <= time_to)
            elif time_from == None and time_to != None:
                query = session.query(Response).filter(Response.time <= time_to)
            elif time_from != None and time_to == None:
                query = session.query(Response).filter(Response.time >= time_from)
            else:
                query = session.query(Response)
            return {"status": "200", "data": [item.values() for item in query.all()]}
    
    def delete_addr(self, address):
        with self.sessions.begin() as session:
            addressResponses = session.query(Response).filter(Response.address == address).delete()

        return "ok"

    def delete_all(self):
        """
        delete all responses
        """
        with self.sessions.begin() as session:
            session.query(Response).delete()
        return {"status": "200"}

    def add(self, address, time, value, task, worker):
        """
        write response of tested address to db
        """ # TODO update last time of task
        # TODO obsolete since worker sync
        result = Response(
            address=address,
            time=int(time),
            value=int(value),
            task=task,
            worker=worker
        )
        with self.sessions.begin() as session:
            session.add(result)
    
    def get_avrg_all(self, date_from=None, date_to=None):
        """
        generate JSON of average response time of each ip addresses, dateFrom and dateTo are optional
        """ # TODO time selection
        outcome = []
        with self.sessions.begin() as session:
            for item in session.query(Response.address).distinct():
                address = item[0]
                # TODO optimize query
                value = session.query(func.avg(Response.value)).filter(Response.address == address).one()[0]
                outcome.append({"address": address, "value": int(value)})
        return outcome

    ## TODO: validate worker (if does not exist, than internal error)
    def get_summary(self, worker=False, time_from=False, time_to=False):
        """
            get info is detailed list of addresses (generate: number of addr records,
            first time testing, last time testing and average responsing time)
            # TODO filter by worker and task
        """
        outcome = []
        with self.sessions.begin() as session:
            for item in session.query(Response.address).distinct():
                address = item[0]
                query = session.query(Response).filter(Response.address == address)
                if worker:
                    query = query.filter(Response.worker == worker)
                if time_from:
                    query = query.filter(Response.time > time_from)
                if time_to:
                    query = query.filter(Response.time < time_to)
                outcome.append({
                    "address": address,
                    "first_response": query.order_by(Response.time).first().time,
                    "last_response": query.order_by(Response.time.desc()).first().time,
                    "average": query.with_entities(func.avg(Response.value)).one()[0],
                    "count": query.count()
                })
        return {"status": "200", "data": outcome}

    def get(self, worker=False, task="ping"):
        """
        Return list of responses.
        """
        with self.sessions.begin() as session:
            query = session.query(Response).filter(Response.task == task)
            if worker:
                query.filter(Response.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO custom function


    
    
