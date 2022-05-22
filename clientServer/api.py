from typing import Optional
from fastapi import FastAPI
import json

from class1.sqlConnector import sql

app = FastAPI()
sqlConn = sql()


@app.get("/")
def read_root():
    data_set = {"key1": [{"FirstName": "Alice", "age": 6},{"FirstName": "Alice2", "age": 8}], "key2": [4, 5, 6]}
    json_dump = json.dumps(data_set)
    return {json_dump}

@app.get("/getTasks")
def read_ipAdresses():
    with open("../config.json", "r") as f:
        config = json.loads(f.read())
    tasks = config["tasks"]
    return tasks

@app.get("/getAverageResponse")
def getAvrgResponse(dateFrom: Optional[str] = None, dateTo: Optional[str] = None):
    #return dateTo
    return sqlConn.getAvrgResponseAll(dateFrom, dateTo)

@app.get("/getAddrInfo")
def getAddrInfo(dateFrom: Optional[str] = None, dateTo: Optional[str] = None):
    #return dateTo
    return sqlConn.getAddrInfo(dateFrom, dateTo)