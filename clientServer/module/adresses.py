"""
Load ip addr from primary server (apiServer)
"""

import json
import logging
from urllib.request import urlopen
from module.sql_connector import SqlConnector


class Adresses():
    """ class load addresses"""
    def __init__(self):
        """init"""
        logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG)
        self.load_ip_addr()

    @classmethod
    def load_ip_addr(cls):
        """ load ip addr from apiServer"""
        with open("config.json", "r", encoding='utf-8') as readed_text:
            config = json.loads(readed_text.read())
            url = config["primaryServer"][0]["ip_addr"]

        url_server = "http://" + url + "/getTasks"
        response = urlopen(url_server)
        data_json = json.loads(response.read())
        sql_conn = SqlConnector()
        sql_conn.update_ip_addr(data_json)
