from class1.adresses import Adresses
from class1.sqlConnector import sql

"""Main

This script has the main loop where the tasks are executed by a new thread and
the results are queued in a specific thread.

This tool accepts any kind of task, address and time(freq or daytime) provided
in the config.

This script requires that `ping3` and `datetime` be installed within the Python
environment you are running this script in.

"""

import threading, queue
import time
import json
import copy

import ping3
from datetime import datetime

from class1.sqlConnector import sql

sqlConn = sql()
sqlConn.setNullNextRun()

print(sqlConn.getAvrgResponseAll())

#from storages.engines import get_writer_engine

def ping(address):
    """Convert None values to -1."""
    result = ping3.ping(address)

    if type(result) == float:
        return result
    else:
        return -1


def get_granularity(granularity):
    """Convert frequencies to seconds."""
    FREQS = {
        "H": 60 * 60,
        "M": 60,
        "S": 1,
        "D": 24 * 60 * 60,
    }
    number, letter = int(granularity[:-1]), granularity[-1].upper()
    return number * FREQS[letter]

def execute_task_NEW(address, freq):
    """Assign a new thread to the new task."""
    sqlConn.setNextTimeBuffer(address) #security buffer, in thread will be rewritten
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
        # TODO: add any other task_type ex.(trace route, http requests, etc)
        pass
    response_queue.put(response)


def writer_loop(settings):
    """Filling up the storing queue with the data."""
    ##storage_engine = get_writer_engine(settings["engine"])
    while True:
        while not response_queue.empty():
            response = response_queue.get()
            # writing the response based on the storage_engine
            sqlConn.addResponse(response["address"], response["time"], response["value"], response["nextTime"])
            response_queue.task_done()
            time.sleep(0.001)
        time.sleep(settings["sleep"])


response_queue = queue.Queue() # the response queue is the thread queue

with open("config.json", "r") as f:
    config = json.loads(f.read())
tasks = config["tasks"]



# Result queue thread
threading.Thread(target=writer_loop, args=[copy.copy(config["writer_settings"])], daemon=True).start()

for i in sqlConn.getAllAddr():
    execute_task_NEW(i["ip_addr"], i["freq"])

while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    ipNextTurn = sqlConn.getNextIpAddr()

    ipNextTime = int(ipNextTurn.next_run)
    ipAddrNextTurn = ipNextTurn.ip_addr
    ipFreqNextTurn = ipNextTurn.freq

    if(ipNextTime < time.time()):
        execute_task_NEW(ipAddrNextTurn, ipFreqNextTurn)

    """Separating the frequencies and the daytime tasks."""
    """for task in tasks:
        # logic for frequency based tasks
        if "freq" in task.keys():
            if not "last_run" in task.keys(): # starting from scratch
                execute_task(task)
            else:
                if time.time() > get_granularity(task["freq"]) + task["last_run"]:
                    execute_task(task)
        # logic for daytime based tasks
        elif "daytime" in task.keys():
            if not "next_run" in task.keys() and current_time == task["daytime"]:

                execute_task(task)
            elif "next_run" in task.keys():
                if time.time() >= task["next_run"] and current_time == task["daytime"]:
                    execute_task(task)
         # if no information known?
        else:
            error = {
                "type": task["type"],
                "address": task["address"],
                "value": "Error"
            }"""

    time.sleep(0.3)



