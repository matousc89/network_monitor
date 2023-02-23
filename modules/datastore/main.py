"""
Fast api setup and routes for datastore.
"""
from typing import Optional
from fastapi import Request, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import Union

from datetime import datetime, timedelta
from modules.datastore.sql_connector import DatastoreSqlConnector
from settings import TESTING
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from modules.datastore import old_report




sql_conn = DatastoreSqlConnector()
if TESTING:
    sql_conn.clear_all_tables()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
print("http://127.0.0.1:8000/docs")  # link to default FastAPI browser

@app.get("/")
def read_root():
    """ access via FastApi, root directory return true value """
    return {"status": True}


"""
=== START SECURITY ===
"""
SECRET_KEY = "885da96a8e6ff8ddfeb25f6196a93cd8f677c46097cc60df2c5812021281da49"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    role: Union[str, None] = None

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user = {'username': username, 'hashed_password': sql_conn.get_user_hash(username), 'role': sql_conn.get_user(username)}
    return UserInDB(**user)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not verify_password(password, sql_conn.get_user_hash(username)):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user



@app.get("/getUserHash")#get all responses for graph
async def get_user_hash(username):
    """
        generate JSON of all response times by time
    """
    return sql_conn.get_user_hash(username)

@app.get("/items/") #testing purpose / oauth2
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/getAllResponses")#get all responses for graph
def get_avrg_response():
    """
        generate JSON of all response times by time
    """
    return sql_conn.get_all_responses()


@app.post("/createTask")#insert address
async def put_new(address, task, time, worker):
    """
        generate JSON of all response times by time
    """
    data = [address,task,time,worker]
    print("přidá: ", data)
    return sql_conn.create_task(data)

@app.post("/deleteTask") #delete address from task table and responses of address
async def dell(address):
    """
        generate JSON of all response times by time
    """
    print("dell: ",address)
    return sql_conn.delete_task(address)

@app.post("/deleteAllResponses")#delete all responses
async def delete_responses():
    """
        generate JSON of all response times by time
    """
    return sql_conn.delete_all_responses()

@app.post("/updateTask")#update tasks dont remove data
async def update_task(address, task, time, worker,oldAddress):
    """
        generate JSON of all response times by time
    """
    data = [address, task, time, worker,oldAddress]
    print("přidá: ", data)
    return sql_conn.update_task(data)

@app.post("/pauseTask") #pause/start
async def pause(address, task, time, worker, runing):
    """
        generate JSON of all response times by time
    """
    data = [address, task, time, worker, runing]
    print("Start: ", data)
    return sql_conn.pause_task(data)

@app.get("/getWorkerTasks")
def get_worker_tasks(worker):
    """
    Return tasks for given worker
    """
    return sql_conn.get_worker_tasks(worker)

@app.get("/getWorkerTasks") # TODO why twice?
def get_worker_tasks(worker):
    """
    Return tasks for given worker
    """
    return sql_conn.get_worker_tasks(worker)








@app.get("/getAverageResponse")
def get_avrg_response(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """
        generate JSON of average response time of each ip addresses,
        dateFrom and dateTo are optional
    """
    return sql_conn.get_avrg_response_all(date_from, date_to)

@app.get("/getResponseSummary")
def get_response_summary(worker=False, time_from: Optional[str] = None, time_to: Optional[str] = None):
    """
    get info is detailed list of addresses (generate: number of addr records,
    first time testing, last time testing and average responsing time)"""
    return sql_conn.get_response_summary(worker, time_from, time_to)

@app.get("/addResponse")
def add_response(address, time, value, task, worker):
    """
    create new row (response) into db
    """
    sql_conn.add_response(address, time, value, task, worker)
    return {"status": True}


@app.get("/getAllAddresses")
def get_worker_tasks():
    """
    Get all addresses
    """
    return sql_conn.get_all_addresses()




@app.get("/getAddress") # TODO ?
def get_worker_tasks(address):
    """
    Delete address specified in request provided data
    """
    return sql_conn.get_address(address)

@app.post("/updateAddress")
async def update_address(request: Request):
    """
    Update address from provided data
    """
    data = await request.json()
    return sql_conn.update_address(data)

@app.post("/deleteAddress")
async def delete_address(request: Request):
    """
    Delete address specified in request provided data
    """
    data = await request.json()
    return sql_conn.delete_address(data)

@app.post("/syncWorker")
async def sync_worker(request: Request):
    """
    Worker synchronization:
    accept responses for storage
    return list of tasks for given worker
    """
    data = await request.json()
    return sql_conn.sync_worker(data)

@app.get("/report", response_class=HTMLResponse)
async def make_report():
    """
    Create and return html report.
    """
    worker = "default"
    responses = sql_conn.get_responses(worker=worker)

    df = old_report.responses2df(responses)

    html_content = []
    html_content += old_report.get_histogram(df)
    html_content += old_report.get_linear(df)
    html_content += old_report.get_bar(df)

    html_str = "\n".join(html_content)

    return HTMLResponse(content=html_str, status_code=200)


@app.get("/map", response_class=HTMLResponse)
async def make_map(latitude=50.0755, longitude=14.4378):
    """
    Create a folium map.
    use as: http://127.0.0.1:8000/map?longitude=200&latitude=10

    TODO: it should be worker latitude and longitude
    TODO: maybe join sql request instead of manual joining
    """
    worker = "default"
    annotated_addresses = sql_conn.get_all_addresses()
    address_summaries = sql_conn.get_response_summary(worker=worker)

    addresses = []
    for address in annotated_addresses["data"]:
        for summary in address_summaries["data"]:
            if address["address"] == summary["address"]:
                address.update(summary)
                addresses.append(address)

    html_str = old_report.get_map(addresses, latitude, longitude)

    return HTMLResponse(content=html_str, status_code=200)



app.mount("/media", StaticFiles(directory="media"), name="media")
