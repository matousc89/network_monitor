"""
Tests related to datastore
"""
import json
import unittest
import pathlib

import requests

from run import run_storage_app_process
from settings import DATASTORE_APP_ADDRESS
from modules.common import build_url

class TestingDatastore(unittest.TestCase):
    """
    Tests related to datastore.
    """

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
        """
        Test root address to return ok status.
        """
        url = build_url(*DATASTORE_APP_ADDRESS)
        returned_data = requests.get(url).json()
        self.assertEqual(returned_data["status"], True)

    def test010_add_response(self):
        """
        Upload responses to datastore.
        """
        url = build_url(*DATASTORE_APP_ADDRESS, slug="addResponse")
        for params in self.data["responses"]:
            returned_data = requests.get(url, params=params).json()
            self.assertEqual(returned_data["status"], True)

    def test020_get_average_response(self):
        """
        Test average response time calculation at datastore.
        """
        url = build_url(*DATASTORE_APP_ADDRESS, slug="getAverageResponse")
        returned_data = requests.get(url).json()
        value = -1
        for item in returned_data:
            if item["address"] == "100.100.100.102":
                value = float(item.get("value", -1))
        self.assertEqual(value, 40)

    def test030_get_address_info(self):
        """
        Test address report. Should return correct number of records.
        """
        url = build_url(*DATASTORE_APP_ADDRESS, slug="getAddressInfo")
        params = {
            "time_from": 100,
        }
        returned_data = requests.get(url, params=params).json()
        self.assertEqual(len(returned_data), 3)
