from typing import Optional
from fastapi import FastAPI
import json

from class1.sqlConnector import sql

app = FastAPI()
sqlConn = sql()
sql.updateIpAddr()


@app.get("/")
def read_root():
    return 'true'

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

@app.get("/addResponse")
def addResponse(ipAddr, time, response, server):
    #return dateTo
    sqlConn.addResponse(ipAddr, time, response, 0,server)
    return 'true'

@app.get("/getTasks")
def read_ipAdresses():
    with open("../config.json", "r") as f:
        config = json.loads(f.read())
    tasks = config["tasks"]
    return tasks
