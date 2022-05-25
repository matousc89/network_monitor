import json
import logging
from urllib.request import urlopen
from class1.sqlConnector import sql


class Adresses():
    def __init__(self):
        logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG)
        db.sql
        self.loadIpAddr()

    def loadIpAddr():
        with open("config.json", "r") as f:
            config = json.loads(f.read())
            url = config["primaryServer"][0]["ip_addr"]
        
        urlServer = "http://" + url + "/getTasks"
        response = urlopen(urlServer)
        data_json = json.loads(response.read())
        sql.updateIpAddr(data_json)

    
