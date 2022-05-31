"""
Tests related to Worker
"""
import json
import unittest
import pathlib
import time

# from run import run_worker_app_process
from modules.worker.sql_connector import WorkerSqlConnector

class TestingWorker(unittest.TestCase):

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
        self.sql_conn.update_all_tasks(self.data["tasks"])
        tasks = self.sql_conn.get_tasks()
        self.assertEqual(len(tasks), len(self.data["tasks"]))
        self.assertEqual(tasks[0]["ip_address"], self.data["tasks"][0]["ip_address"])

        # check if the obsolete task is removed
        time.sleep(0.001)
        self.sql_conn.update_all_tasks(self.data["tasks"][0:1])
        tasks = self.sql_conn.get_tasks() # TODO replace with sync?
        self.assertEqual(len(tasks), 1)

