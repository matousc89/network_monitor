from fastapi import APIRouter, Depends, HTTPException,Security,Request
from modules.datastore.sql_connector import SqlConnection, SqlAddress
from typing import Optional


router = APIRouter(
    prefix="/address",
    tags=["address"],
    responses={404: {"description": "Not found"}},
)

from modules.datastore.OAuth2 import OAuth2, User, Token

oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlAddress = SqlAddress(session)

@router.get("/getAll")
def get_all():
    """
    Get all addresses
    """
    return sqlAddress.get_all()

@router.get("/get") # TODO ?
def get(address):
    """
    Delete address specified in request provided data
    """
    return sqlAddress.get(address)

@router.post("/update")
async def update(request: Request):
    """
    Update address from provided data
    """
    data = await request.json()
    return sqlAddress.update(data)

@router.post("/delete")
async def delete(request: Request):
    """
    Delete address specified in request provided data
    """
    data = await request.json()
    return sqlAddress.delete(data)