"""
Worker main contain the worker main class.
"""
import threading
import time
import requests
import logging
import copy

from settings import DATASTORE_APP_ADDRESS
from modules.worker.sql_connector import WorkerSqlConnector
from modules.worker.measurements import get_response_ping
from modules.common import get_granularity, build_url
from modules.common import ms_time, ms_sleep

from settings import worker_log_config

class Worker():
    """
    Worker class
    """
    def __init__(self, run=True):
        logging.config.dictConfig(worker_log_config)
        self.name = "default"# TODO where it should be stored? Should default value be UUID?
        self.datastore_url = build_url(*DATASTORE_APP_ADDRESS, "syncWorker")
        self.sql_conn = WorkerSqlConnector(self.name)
        self.sql_conn.reset_tasks()
        if run:
            self.__run()

    def __io_loop(self):
        """Filling up the storing queue with the data."""
        while True:
            responses = self.sql_conn.presync()
            payload = {
                "worker": self.name,
                "responses": responses,
            }
            try:
                tasks = requests.post(self.datastore_url, json=payload).json()
            except requests.exceptions.RequestException as e:
                logging.critical("Cannot contact datastore - {}".format(str(e)))
                tasks = []
            self.sql_conn.postsync(tasks, responses)
            time.sleep(3)

    def __execute_task(self, task):
        """Start execution thread
        """
        threading.Thread(target=self.__task_thread, args=(task,), daemon=True).start()

    def __task_thread(self, task):
        """Execute task in thread.

        If task was already executed in past, wait time is calculated
        to trigger task at correct time.
        """
        now = ms_time()
        if task["next_run"]:
            wait_time = task["next_run"] - now
        else:
            wait_time = 0
        task["last_run"] = now + wait_time
        task["next_run"] = task["last_run"] + get_granularity(task["frequency"])
        self.sql_conn.update_task(task)
        ms_sleep(wait_time)
        if task["task"] == "ping":
            task["value"] = get_response_ping(task["ip_address"])
        else:
            logging.warning("Unknown task type: {}".format(task["task"]))
            return
        task["time"] = task["last_run"]
        self.sql_conn.add_response(task)

    def __run(self):
        """
        Main loop of the worker class.

        Task thread is started earlier to allow waiting on exact time in the thread.
        """
        threading.Thread(target=self.__io_loop, daemon=True).start()
        logging.info("Worker started.")
        while True:
            tasks = self.sql_conn.get_tasks()
            now = ms_time()
            for task in tasks:
                if task["last_run"] == 0:
                    self.__execute_task(copy.deepcopy(task))
                elif task["next_run"] - ms_time(2) < now:
                    self.__execute_task(copy.deepcopy(task))
            ms_sleep(500)