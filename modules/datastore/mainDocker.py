from typing import Union

from fastapi import Request, FastAPI, HTTPException, status, Security
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

from settings import TESTING
from modules.datastore.OAuth2 import OAuth2, User, Token

from modules.datastore.sql_connector import SqlConnection, SqlAddress, SqlOther, SqlResponse
from modules.datastore.routers import taskDocker

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}