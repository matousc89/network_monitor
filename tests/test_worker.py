import json
import unittest
import pathlib
import time

import requests

from run import run_worker_app_process
from modules.worker.sql_connector import WorkerSqlConnector
# from settings import DATASTORE_APP_ADDRESS

class TestingWorker(unittest.TestCase):

    # URL = "http://{}:{}/".format(*DATASTORE_APP_ADDRESS)
    datapath = pathlib.PurePath("tests", "test_worker.json")
    with open(datapath, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    sql_conn = WorkerSqlConnector("default")
    sql_conn.clear_all_tables()

    # @classmethod
    # def setUpClass(cls):
    #     """Start server for testing"""
    #     cls.proc = run_worker_app_process()
    #
    # @classmethod
    # def tearDownClass(cls):
    #     """Shutdown server after testing"""
    #     cls.proc.kill()

    def test010_sql_put_tasks(self):
        # no tasks at start
        tasks = self.sql_conn.get_tasks()
        self.assertEqual(len(tasks), 0)

        # check the import of dummy tasks
        self.sql_conn.update_tasks(self.data["tasks"])
        tasks = self.sql_conn.get_tasks()
        self.assertEqual(len(tasks), len(self.data["tasks"]))
        self.assertEqual(tasks[0]["ip_address"], self.data["tasks"][0]["ip_address"])

        # check if the obsolete task is removed
        time.sleep(0.001)
        self.sql_conn.update_tasks(self.data["tasks"][0:1])
        tasks = self.sql_conn.get_tasks()
        self.assertEqual(len(tasks), 1)

