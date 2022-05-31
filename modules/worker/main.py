"""
Worker main contain the worker main class.
"""
import threading
import time
import requests

from settings import DATASTORE_APP_URL, DATASTORE_APP_ADDRESS
from modules.worker.sql_connector import WorkerSqlConnector
from modules.worker.measurements import get_response_ping
from modules.common import ms_time, get_granularity, build_url

class Worker():
    """
    Worker class
    """
    def __init__(self):
        self.name = "default" # TODO store somewhere else
        self.datastore_url = DATASTORE_APP_URL + "getWorkerTasks" # TODO correct one
        self.sql_conn = WorkerSqlConnector(self.name)
        self.__run()

    def __io_loop(self):
        """Filling up the storing queue with the data."""
        while True:
            responses = self.sql_conn.get_unsynced_responses() # TODO presync functions
            url = build_url(*DATASTORE_APP_ADDRESS, "syncWorker")
            payload = {
                "worker": self.name,
                "responses": responses,
            }
            tasks = requests.post(url, json=payload).json() # TODO catch exception
            self.sql_conn.mark_responses_as_synced(responses) # TODO postsync functions - replace with one sql command
            self.sql_conn.update_all_tasks(tasks)
            time.sleep(3)

    def __execute_task(self, task):
        """Start execution thread
        """
        threading.Thread(target=self.__task_thread, args=(task,), daemon=True).start()

    def __task_thread(self, task):
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

    def __run(self):
        """
        Main loop of the worker class.
        """
        threading.Thread(target=self.__io_loop, daemon=True).start()
        while True:
            tasks = self.sql_conn.get_tasks()
            now = ms_time()
            for task in tasks:
                if task["last_run"] == None:
                    self.__execute_task(task)
                elif task["next_run"] < now: # TODO add time buffer?
                    self.__execute_task(task)

            time.sleep(0.3)





