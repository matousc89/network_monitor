from pydantic import BaseModel, Field,Json
from typing import Optional, List

class AddressIn(BaseModel):
    address: str
    name: str
    location: str
    latitude: float
    longitude: float
    note: Optional[str]
    color: str

class AddressOut(AddressIn):
    id: int

class AddressDelete(BaseModel):
    address:str

class TaskIn(BaseModel):
    address_id: int
    running: bool = Field(default=True)
    hide: bool = Field(default=False)
    task: str
    frequency: str
    retry: Optional[int] = Field(default=0)
    timeout: Optional[int] = Field(default=1)
    treshold: Optional[int] = Field(defalut=50)
    retry_data: Optional[dict]

class TaskOut(TaskIn):
    id: int

class TaskAssociate(BaseModel):
    taskId: int
    workerId: int

class TaskId(BaseModel):
    id: int

class Response(BaseModel):
    address: str
    time: int
    value: int
    task: str

class ResponseAdd(Response):
    workerId: int

class ResponseGet(BaseModel):
    time_from: Optional[int]
    time_to: Optional[int]
    limit: Optional[int]

class ResponseGetWorker(BaseModel):
    time_from: Optional[int]
    time_to: Optional[int]
    workerId: Optional[int]

class HostStatus(BaseModel):
    address: str
    time_from: int
    time_to: int
    available: bool

class syncWorker(BaseModel):
    responses: Optional[List[Response]]
    hosts_availability: Optional[List[HostStatus]] 
    api: str