"""
Worker main contain the worker main class.
"""
import threading
import queue
import time
import json
import ping3
import requests

from settings import DATASTORE_APP_URL
from modules.worker.sql_connector import WorkerSqlConnector

class Worker():
    """
    Worker class
    """

    def __init__(self):
        self.name = "default" # TODO store somewhere else
        self.datastore_url = DATASTORE_APP_URL + "getWorkerTasks"
        self.response_queue = queue.Queue()
        self.sql_conn = WorkerSqlConnector(self.name)
        self.run()

    def io_loop(self):
        """Filling up the storing queue with the data."""
        while True:
            while not self.response_queue.empty():
                response = self.response_queue.get()
                # writing the response based on the storage_engine # TODO store response
                # sql_conn.add_response(response["address"], response["time"],
                #                       response["value"], response["nextTime"])
                # response_queue.task_done()
                time.sleep(0.1)

            tasks = requests.get(self.datastore_url, params={"worker": self.name}).json()
            self.sql_conn.update_tasks(tasks)

            time.sleep(3)

    def run(self):
        threading.Thread(target=self.io_loop, daemon=True).start()
        while True:
            pass

            # with self.task_lock:
            # for task in get_actual_tasks():
            #     print(task)

        #     now = datetime.now()
        #     current_time = now.strftime("%H:%M")
        #     ipNextTurn = sql_conn.get_next_ip_addr()
        #
        #     ipNextTime = int(ipNextTurn.next_run)
        #     ipAddrNextTurn = ipNextTurn.ip_addr
        #     ipFreqNextTurn = ipNextTurn.freq
        #
        #     if(ipNextTime < time.time()):
        #         execute_task_new(ipAddrNextTurn, ipFreqNextTurn)
            time.sleep(3)


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
