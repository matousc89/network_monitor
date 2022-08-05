"""
Fast api setup and routes for datastore.
"""
from typing import Optional
from fastapi import Request, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from modules.datastore.sql_connector import DatastoreSqlConnector
from settings import TESTING

from modules.datastore import old_report


sql_conn = DatastoreSqlConnector()
if TESTING:
    sql_conn.clear_all_tables()

app = FastAPI()


@app.get("/")
def read_root():
    """ access via FastApi, root directory return true value """
    return {"status": True}

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
