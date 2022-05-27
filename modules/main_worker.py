"""Main

This script has the main loop where the tasks are executed by a new thread and
the results are queued in a specific thread.

This tool accepts any kind of task, address and time(freq or daytime) provided
in the config.
"""
import threading
import queue
import time
import json
import copy
from datetime import datetime
from modules.sql_connector import WorkerSqlConnector
import ping3

sql_conn = WorkerSqlConnector()
# sql_conn.set_null_next_run()

def ping(address):
    """Convert None values to -1."""
    result = ping3.ping(address)

    if type(result) == float:
        return_text = result
    else:
        return_text = -1

    return return_text


def get_granularity(granularity):
    """Convert frequencies to seconds."""
    freqs = {
        "H": 60 * 60,
        "M": 60,
        "S": 1,
        "D": 24 * 60 * 60,
    }
    number, letter = int(granularity[:-1]), granularity[-1].upper()
    return number * freqs[letter]

def execute_task_new(address, freq):
    """Assign a new thread to the new task."""
    sql_conn.set_next_time_buffer(address) #security buffer, in thread will be rewritten
    threading.Thread(target=execute_thread, args=('ping',address,freq), daemon=True).start()



def execute_thread(task_type, address, freq):
    """Execute task by thread.
    Keyword arguments:
    task_type -- the type of task (currently only ping)
    address -- the url or IP address
    """
    if task_type == "ping":
        response = {
            "type": task_type,
            "address": address,
            "time": int(time.time()),
            "nextTime": int(time.time()) + get_granularity(freq),
            "value": ping(address)
        }
    else:
        pass
    response_queue.put(response)


def writer_loop(settings):
    """Filling up the storing queue with the data."""
    ##storage_engine = get_writer_engine(settings["engine"])
    while True:
        while not response_queue.empty():
            response = response_queue.get()
            # writing the response based on the storage_engine
            sql_conn.add_response(response["address"], response["time"],
                response["value"], response["nextTime"])
            response_queue.task_done()
            time.sleep(0.1)
        time.sleep(1)


response_queue = queue.Queue()

with open("config.json", "r", encoding='utf-8') as f:
    config = json.loads(f.read())
tasks = config["tasks"]

# Result queue thread
threading.Thread(target=writer_loop, daemon=True).start()

for i in sql_conn.get_all_addr():
    execute_task_new(i["ip_addr"], i["freq"])

while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    ipNextTurn = sql_conn.get_next_ip_addr()

    ipNextTime = int(ipNextTurn.next_run)
    ipAddrNextTurn = ipNextTurn.ip_addr
    ipFreqNextTurn = ipNextTurn.freq

    if(ipNextTime < time.time()):
        execute_task_new(ipAddrNextTurn, ipFreqNextTurn)

    time.sleep(0.3)
