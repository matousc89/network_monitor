from fastapi import APIRouter, Depends, HTTPException,Security, Response
from modules.datastore.sql_connector import SqlConnection, SqlTask
from modules.datastore.OAuth2 import OAuth2, User, Token
from modules.datastore.models import Task
from modules.datastore.schema import TaskIn, TaskAssociate, TaskDelete
from typing import Any



router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)

oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlTask = SqlTask(session)


@router.post("/", status_code=200)#insert address
async def create_new(task: TaskIn, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
#    data = [address, task, time, worker, latitude, longitude, color, name, runing, hide]
#    print("přidá: ", data)
    return sqlTask.create(task)


@router.post("/associate", status_code=200) #associtate task to worker
async def put_new(data: TaskAssociate, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return sqlTask.associate(data)


@router.delete("/") #delete address from task table and responses of address
async def delete(data:TaskDelete,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    print("dell: ",data.address)
    return sqlTask.delete(data)

@router.post("/associate-delete") #delete address from task table and responses of address
async def deleteAssociate(data:TaskAssociate,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return sqlTask.associate_delete(data)

@router.post("/update")#update tasks dont remove data
async def update_task(address, task, time, worker, oldAddress, latitude, longitude, color, name, runing: bool, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    data = [address, task, time, worker, latitude, longitude, color, name, runing, oldAddress]
    print("upravi: ", data)
    return sqlTask.update(data)

@router.post("/pause") #pause/start
async def pause(address, runing: bool = True, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    data = [address, runing]
    print("Start: ", data)
    return sqlTask.pause(data)

@router.post("/hide") #pause/start
async def pause(address, hide: bool = False, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    data = [address, hide]
    print("Start: ", data)
    return sqlTask.hide(data)

@router.get("/WorkersTask")
def get_worker_tasks(worker,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
    Return tasks for given worker
    """
    return sqlTask.WorkersTask(worker)

@router.get("/getActiveTasks")
def get_active_task(workerId,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
    Return tasks for given worker
    """
    return sqlTask.getActiveTasks(workerId)

@router.get("/getTasks")
def get_worker_tasks(current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
    Return tasks for given worker
    """
    return sqlTask.getTasks()
