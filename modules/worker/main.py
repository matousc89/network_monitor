"""
Worker main contain the worker main class.
"""
import threading
# import queue
import time
# import json
import ping3
import requests

from settings import DATASTORE_APP_URL
from modules.worker.sql_connector import WorkerSqlConnector
from modules.common import ms_time, get_granularity

class Worker():
    """
    Worker class
    """

    def __init__(self):
        self.name = "default" # TODO store somewhere else
        self.datastore_url = DATASTORE_APP_URL + "getWorkerTasks"
        # self.response_queue = queue.Queue()
        self.sql_conn = WorkerSqlConnector(self.name)
        self.run()

    def __io_loop(self):
        """Filling up the storing queue with the data."""
        while True:
            # TODO sync responses (in one request with task update)
            tasks = requests.get(self.datastore_url, params={"worker": self.name}).json()
            self.sql_conn.update_all_tasks(tasks)
            time.sleep(3)

    def execute_task(self, task):
        """Start execution thread
        """
        threading.Thread(target=self.start_task_thread, args=(task,), daemon=True).start()

    def start_task_thread(self, task):
        """Execute task in thread.
        """
        # TODO calculate exact time, put it in database and wait
        now = ms_time()
        task["last_run"] = now
        task["next_run"] = now + get_granularity(task["frequency"])
        self.sql_conn.update_task(task)
        # TODO wait to exact time
        if task["task"] == "ping":
            # TODO make it happen
            task["value"] = get_response_ping(task["ip_address"])
        else:
            pass # TODO report unwknown task
        self.sql_conn.add_response(task)

    def run(self):
        """
        Main loop of the worker class.
        """
        threading.Thread(target=self.__io_loop, daemon=True).start()
        while True:
            tasks = self.sql_conn.get_tasks()
            now = ms_time()
            for task in tasks:
                if task["last_run"] == None:
                    self.execute_task(task)
                elif task["next_run"] < now: # TODO add time buffer?
                    self.execute_task(task)

            time.sleep(0.3)

def get_response_ping(address):
    """Convert None values to -1."""
    result = ping3.ping(address)

    if type(result) == float:
        return ms_time(result)
    else:
        return -1




