from fastapi import APIRouter, Depends, HTTPException,Security
from modules.datastore.sql_connector import SqlConnection, SqlResponse
from typing import Optional


router = APIRouter(
    prefix="/response",
    tags=["response"],
    responses={404: {"description": "Not found"}},
)

from modules.datastore.OAuth2 import OAuth2, User, Token

oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlResponse = SqlResponse(session)

@router.get("/getAll")#get all responses for graph
def get_avrg_response(time_from: Optional[str] = None, time_to: Optional[str] = None, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return sqlResponse.get_all(time_from, time_to)

@router.post("/deleteAll")#delete all responses
async def delete_responses(current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return sqlResponse.delete_all()

@router.get("/getAverage")
def get_avrg_response(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """
        generate JSON of average response time of each ip addresses,
        dateFrom and dateTo are optional
    """
    return sqlResponse.get_avrg_all(date_from, date_to)

@router.get("/getSummary")
def get_response_summary(worker: Optional[str] = None, time_from: Optional[str] = None, time_to: Optional[str] = None, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
    get info is detailed list of addresses (generate: number of addr records,
    first time testing, last time testing and average responsing time)"""
    return sqlResponse.get_summary(worker, time_from, time_to)

@router.get("/add")
def add_response(address, time, value, task, worker):
    """
    create new row (response) into db
    """
    sqlResponse.add(address, time, value, task, worker)
    return {"status": True}



