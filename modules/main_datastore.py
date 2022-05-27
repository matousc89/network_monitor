"""
Fast api setup and routes for datastore.
"""
import json
from typing import Optional
from fastapi import FastAPI

from modules.sql_connector import DatastoreSqlConnector

from settings import TESTING


sql_conn = DatastoreSqlConnector()
sql_conn.update_ip_address()
if TESTING:
    sql_conn.clear_all_tables()

app = FastAPI()


@app.get("/")
def read_root():
    """ access via FastApi, root directory return true value """
    return {"status": True}

# @app.get("/getTasks")
# def read_ip_adresses():
#     """
#     Read config file and generate json of tasks (database fixture) TODO: should be optional
#     """
#     with open("apiServer/config.json", "r", encoding="utf-8") as readed_text:
#         config = json.loads(readed_text.read())
#     tasks = config["tasks"]
#     return tasks

@app.get("/getAverageResponse")
def get_avrg_response(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """
        generate JSON of average response time of each ip addresses, dateFrom and dateTo are optional
    """
    # TODO why the address is not selectable?
    return sql_conn.get_avrg_response_all(date_from, date_to)

@app.get("/getAddressInfo")
def get_address_info(time_from: Optional[str] = None, time_to: Optional[str] = None):
    """
    get info is detailed list of addresses (generate: number of addr records,
    first time testing, last time testing and average responsing time)"""
    return sql_conn.get_address_info(time_from, time_to)

@app.get("/addResponse")
def add_response(ip_addr, time, value, task, worker):
    """
    create new row (response) into db
    """
    sql_conn.add_response(ip_addr, time, value, task, worker)
    return {"status": True}
