from fastapi import APIRouter, Depends, HTTPException,Security
from modules.datastore.sql_connector import SqlConnection, SqlTask
from modules.datastore.OAuth2 import OAuth2, User, Token


router = APIRouter(
    prefix="/task",
    tags=["task"],
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
    data = [address, task, time, worker, latitude, longitude, color, name, runing, hide]
    print("přidá: ", data)
    return sqlTask.create(data)

@router.post("/associate") #associtate task to worker
async def put_new(taskId, workerId, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    data = [taskId, workerId]
    print(data)
    return sqlTask.associate(data)


@router.post("/delete") #delete address from task table and responses of address
async def dell(address,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    print("dell: ",address)
    return sqlTask.delete(address)

@router.post("/associateDelete") #delete address from task table and responses of address
async def dell(taskId, workerId,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return sqlTask.associate_delete(workerId, taskId)

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
