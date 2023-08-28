from fastapi import APIRouter, Depends, HTTPException,Security
from modules.datastore.sql_connector import SqlConnection, SqlTask
from modules.datastore.OAuth2 import OAuth2, User, Token


router = APIRouter(
    prefix="/taskDocker",
    tags=["taskDocker"],
    responses={404: {"description": "Not found"}},
)


oauth2 = OAuth2()

sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlTask = SqlTask(session)


@router.post("/create")#insert address
async def put_new(address, task, time, worker:int, latitude, longitude, color, name, runing: bool=True, hide: bool=False, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return "data"