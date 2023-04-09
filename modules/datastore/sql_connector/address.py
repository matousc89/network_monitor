from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.data_validation import DataValidation


class SqlAddress(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection

    def update(self, address_data):
        """
        Update address. If address does not exist, create it.
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.address == address_data["address"]).first()
            if address is None:
                address = Address(
                    address=address_data["address"],
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

    def delete(self, address_data):
        """
        Delete address if exists - according ip address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.address == address_data["address"]).first()
            if address is None:
                return {"status": "500"}
            else:
                session.delete(address)
                return {"status": "200"}
    
    def get(self, address):
        """
        Get information about IP address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.address == address).first()
            if address is None:
                return {"status": "500"}
            else:
                return {"status": "200", "data": address.values()}

    def get_all(self):
        """
        Return all addresses
        """
        with self.sessions.begin() as session:
            query = session.query(Address)
            return {"status": "200", "data": [item.values() for item in query.all()]}
