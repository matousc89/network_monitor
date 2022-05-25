"""MAIN"""
import json
from typing import Optional
from fastapi import FastAPI

from module.sql_connector import SqlConnector

app = FastAPI()
sql_conn = SqlConnector()
sql_conn.update_ip_addr()



@app.get("/")
def read_root():
    """ access via FastApi, root directory return true value """
    return 'true'

@app.get("/getTasks")
def read_ip_adresses():
    """
    Read config file and generate json of tasks
    """
    with open("../config.json", "r", encoding="utf-8") as readed_text:
        config = json.loads(readed_text.read())
    tasks = config["tasks"]
    return tasks

@app.get("/getAverageResponse")
def get_avrg_response(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """
        generate JSON of average response time of each ip addresses, dateFrom and dateTo are optinal
    """
    return sql_conn.get_avrg_response_all(date_from, date_to)

@app.get("/getAddrInfo")
def get_addr_info(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """
    get info is detailed list of addresses (generate: number of addr records,
    first time testing, last time testing and average responsing time)"""
    return sql_conn.get_addr_info(date_from, date_to)

@app.get("/addResponse")
def add_response(ip_addr, time, response, server):
    """
    create new row (response) into db
    """
    sql_conn.add_response(ip_addr, time, response, 0,server)
    return 'true'
