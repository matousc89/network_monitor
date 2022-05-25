""" API class """
import json
from typing import Optional
from fastapi import FastAPI

from module.sql_connector import SqlConnector

app = FastAPI()
sql_conn = SqlConnector()


@app.get("/")
def read_root():
    """ access via FastApi, root directory return true value """
    data_set = {"key1": [{"FirstName": "Alice", "age": 6},
        {"FirstName": "Alice2", "age": 8}], "key2": [4, 5, 6]}
    json_dump = json.dumps(data_set)
    return {json_dump}

@app.get("/getTasks")
def read_ip_adresses():
    """ FAST API return tasks """
    with open("../config.json", "r", encoding='utf-8') as readed_text:
        config = json.loads(readed_text.read())
    tasks = config["tasks"]
    return tasks

@app.get("/getAverageResponse")
def get_avrg_response(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """ FastApi return average response time """
    return sql_conn.get_avrg_response_all(date_from, date_to)

@app.get("/getAddrInfo")
def get_addr_info(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """ FastApi return detailed address information """
    return sql_conn.get_addr_info(date_from, date_to)

