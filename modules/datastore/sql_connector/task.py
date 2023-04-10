from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.data_validation import DataValidation
from sqlalchemy.sql import func, exists


class SqlTask(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection

    def create(self, data):
        """
        add new task
        """ # TODO add colors and name to database
        test = DataValidation()
        result = Task(
            address=data[0],
            frequency=data[2],
            task=data[1],
            name=data[7],
            latitude=data[4],
            longitude=data[5],
            color=data[6],
            runing=data[8],
            hide=data[9]
        )

        with self.sessions.begin() as session:
                    existAddress = session.query(exists().where(Task.address == data[0])).scalar()
                    if not existAddress:
                        session.add(result)

        return {"status": DataValidation().IP()}

    def associate(self, data):
        with self.sessions.begin() as session:
            statement = worker_has_task.insert().values(task_id=data[0], worker_id=data[1])
            session.execute(statement)
            session.commit()


    def delete(self, address):
        """
        delete address from tasks and responses of address
        """
        with self.sessions.begin() as session:
            addressTask = session.query(Task).filter(Task.address == address).delete()

        return {"status": "200"}

    def associate_delete(self, workerId, taskId):
        """
        delete address from tasks and responses of address

        delete_stmt = (
...     delete(user_table)
...     .where(user_table.c.name == "patrick")
...     .returning(user_table.c.id, user_table.c.name)
... )
>>> print(delete_stmt)

        """
        with self.sessions.begin() as session:
            statement = worker_has_task.delete().where(worker_has_task.c.task_id==taskId, worker_has_task.c.worker_id==workerId)
            session.execute(statement)
            session.commit()
        return {"status": "200"}

    def update(self, data):
        """
        update task (dell old and save new)
        """
        print(data)
        result = {
            "address":data[0],
            "frequency":data[2],
            "task":data[1],
            "name":data[7],
            "latitude":data[4],
            "longitude":data[5],
            "color":data[6],
            "runing":data[8]
        }

        with self.sessions.begin() as session:
                    #addressTask = session.query(Task).filter(Task.address == data[9]).delete()
                    #existAddress = session.query(exists().where(Task.address == data[9])).scalar()
                    existAddress = session.query(Task).filter(Task.address == data[9]).update(result)
                    print(existAddress)
                    if not existAddress:
                        session.add(Task(**result))

        return {"status": "200"}

    def pause(self, data):
        """
        pause task just remove task from list
        """
        with self.sessions.begin() as session:
            session.query(Task).filter(Task.address == data[0]).update({"runing":data[1]})


        return {"status": "200"}

    def hide(self, data):
        """
        pause task just remove task from list
        """
        with self.sessions.begin() as session:
            session.query(Task).filter(Task.address == data[0]).update({"hide":data[1]})

        return {"status": "200"}


    def WorkersTask(self, worker):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            query = session.query(Task).join(Task, Worker.task).filter(Worker.id == worker)
            #query = session.query(Task).filter(Task.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO make custom function in Task class (instead of __dict__)

    def getTasks(self):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            query = session.query(Task).join(Task, Worker.task)
            #query = session.query(Task).filter(Task.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO make custom function in Task class (instead of __dict__)

    def getActiveTasks(self, workerId):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            query = session.query(Task).join(Task, Worker.task).filter(Worker.id == workerId)
            #query = session.query(Task).filter(Task.worker == worker)
            return [item.id for item in query.all()] # TODO make custom function in Task class (instead of __dict__)
    

       