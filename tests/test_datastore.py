import json
import unittest
import pathlib

import requests

from run import run_storage_app_process
from settings import DATASTORE_APP_ADDRESS


class TestingDatastore(unittest.TestCase):

    URL = "http://{}:{}/".format(*DATASTORE_APP_ADDRESS)
    datapath = pathlib.PurePath("tests", "test_datastore.json")
    with open(datapath, "r", encoding="utf-8") as f:
        data = json.loads(f.read())

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
        for params in self.data["responses"]:
            r = requests.get(url, params=params).json()
            self.assertEqual(r["status"], True)

    def test020_get_average_response(self):
        url = self.URL + "getAverageResponse"
        r = requests.get(url).json()
        value = -1
        for item in r:
            if item["address"] == "100.100.100.102":
                value = float(item.get("value", -1))
        self.assertEqual(value, 40)

    def test030_get_address_info(self):
        url = self.URL + "getAddressInfo"
        params = {
            "time_from": 100,
        }
        r = requests.get(url, params=params).json()
        self.assertEqual(len(r), 3)
