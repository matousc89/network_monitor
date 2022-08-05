"""
Tests related to Worker
"""
import json
import unittest
import pathlib
import time

# from run import run_worker_app_process
from modules.worker.sql_connector import WorkerSqlConnector
# from modules.worker.main import Worker

class TestingWorker(unittest.TestCase):
    """
    Tests related to Worker.
    """

    datapath = pathlib.PurePath("tests", "test_worker.json")
    with open(datapath, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    sql_conn = WorkerSqlConnector("default")
    sql_conn.clear_all_tables()

    # @classmethod
    # def setUpClass(cls):
    #     """
    #     """
    #     cls.worker = Worker(run=False)
    #     time.sleep(0.5) # TODO should check if running in better way (environment variable flag?)

    # @classmethod
    # def setUpClass(cls):
    #     """Start server for testing"""
    #     cls.proc = run_worker_app_process()
    #     time.sleep(0.5) # TODO should check if running in better way (environment variable flag?)
    #
    # @classmethod
    # def tearDownClass(cls):
    #     """Shutdown server after testing"""
    #     cls.proc.kill()

    def test010(self):
        """ Empty db

        Test that no tasks are in the db.
        """
        tasks = self.sql_conn.get_tasks()
        self.assertEqual(len(tasks), 0)

    def test020(self):
        """ Task addition
        """
        self.sql_conn.postsync(self.data["tasks"], [])
        tasks = self.sql_conn.get_tasks()
        self.assertEqual(len(tasks), len(self.data["tasks"]))
        self.assertEqual(tasks[0]["address"], self.data["tasks"][0]["address"])

    def test030(self):
        """Remove obsolete task after second postsync.

        Function has to wait to make task obsolete.
        """
        time.sleep(0.001)
        self.sql_conn.postsync(self.data["tasks"][0:1], [])
        tasks = self.sql_conn.get_tasks()
        self.assertEqual(len(tasks), 1)

    def test040(self):
        """Add response
        """
        response = self.data["responses"][0]
        self.sql_conn.add_response(response)
