"""
Test suite
"""
import unittest
import time
import os

import requests

from run import run_storage_app_process
from settings import DATASTORE_APP_ADDRESS
from settings import DATASTORE_DATABASE

class TestingStorage(unittest.TestCase):

    URL = "http://{}:{}/".format(*DATASTORE_APP_ADDRESS)

    @classmethod
    def setUpClass(cls):
        """Start server for testing"""
        cls.proc = run_storage_app_process(*DATASTORE_APP_ADDRESS)

    @classmethod
    def tearDownClass(cls):
        """Shutdown server after testing"""
        cls.proc.kill()

    def test000_root(self):
        r = requests.get(self.URL).json()
        self.assertEqual(r["status"], True)

    def test010_add_response(self):
        url = self.URL + "addResponse"
        params = {
            "ip_addr": "100.100.100.100",
            "time": int(time.time()),
            "value": 100,
            "task": "ping",
            "worker": "home1"
        }
        r = requests.get(url, params=params).json()
        params = {
            "ip_addr": "100.100.100.101",
            "time": int(time.time()),
            "value": 150,
            "task": "ping",
            "worker": "home1"
        }
        r = requests.get(url, params=params).json()
        params = {
            "ip_addr": "100.100.100.102",
            "time": int(time.time()),
            "value": 37,
            "task": "ping",
            "worker": "home1"
        }
        r = requests.get(url, params=params).json()
        self.assertEqual(r["status"], True)

    def test020_get_average_response(self):
        url = self.URL + "getAverageResponse"
        r = requests.get(url).json()
        value = -1
        for item in r:
            if item["address"] == "100.100.100.100":
                value = float(item.get("value", -1))
        self.assertEqual(value, 100)

    def test030_get_address_info(self):
        url = self.URL + "getAddressInfo"
        params = {
            "time_from": 1653657043,
        }
        r = requests.get(url, params=params).json()
        self.assertEqual(r["status"], True)

if __name__ == "__main__":
    unittest.main()


