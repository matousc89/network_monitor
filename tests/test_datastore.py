"""
Tests related to datastore
"""
import json
import unittest
import pathlib
import time

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
        time.sleep(1) # TODO make sure it runs in better way

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

    def test030_get_response_summary(self):
        """
        Test address report. Should return correct number of records.
        """
        url = build_url(*DATASTORE_APP_ADDRESS, slug="getResponseSummary")
        params = {
            "time_from": 100,
        }
        returned_data = requests.get(url, params=params).json()
        self.assertEqual(len(returned_data["data"]), 3)

    def test100_update_address(self):
        """
        Add address in database
        """
        params = self.data["addresses"][0]
        url = build_url(*DATASTORE_APP_ADDRESS, slug="updateAddress")
        returned_data = requests.post(url, json=params).json()
        self.assertEqual(returned_data["status"], "Created")

    def test110_update_address(self):
        """
        Update address in database
        """
        params = self.data["addresses"][0]
        params["note"] = "test"
        url = build_url(*DATASTORE_APP_ADDRESS, slug="updateAddress")
        returned_data = requests.post(url, json=params).json()
        self.assertEqual(returned_data["status"], "Updated")

    def test120_get_address_ok(self):
        params = self.data["addresses"][0]
        url = build_url(*DATASTORE_APP_ADDRESS, slug="getAddress")
        returned_data = requests.get(url, params=params).json()
        self.assertEqual(returned_data["data"]["ip_address"], params["ip_address"])

    def test121_get_address_fail(self):
        params = {"ip_address": "this.do.not.exist"}
        url = build_url(*DATASTORE_APP_ADDRESS, slug="getAddress")
        returned_data = requests.get(url, params=params).json()
        self.assertEqual(returned_data["status"], "Not found")

    def test122_get_all_addresses(self):
        url = build_url(*DATASTORE_APP_ADDRESS, slug="getAllAddresses")
        returned_data = requests.get(url).json()
        self.assertEqual(len(returned_data["data"]), 1)

    def test130_delete_address_fail(self):
        params = {"ip_address": "this.do.not.exist"}
        url = build_url(*DATASTORE_APP_ADDRESS, slug="deleteAddress")
        returned_data = requests.post(url, json=params).json()
        self.assertEqual(returned_data["status"], "Not found")

    def test131_delete_address_ok(self):
        params = self.data["addresses"][0]
        url = build_url(*DATASTORE_APP_ADDRESS, slug="deleteAddress")
        returned_data = requests.post(url, json=params).json()
        self.assertEqual(returned_data["status"], "Deleted")
