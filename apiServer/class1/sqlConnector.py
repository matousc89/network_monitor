from typing import Optional
import sqlalchemy as db
from fastapi import FastAPI
import pandas as pd
import os
import logging
import time
import collections
import json
import datetime


class sql():   
    def __init__(self):
        logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG)
        global engine
        engine = db.create_engine('sqlite:///network.db', echo = False)
        self.__checkTable()


    def __checkTable(self):
        if db.inspect(engine).has_table("ping1"):
            print("Ping1 has been already created")
        else:
            print("Creating ping1 table")
            meta = db.MetaData()
            ping = db.Table(
            'ping1', meta, 
            db.Column('id', db.Integer, primary_key = True), 
            db.Column('ip_addr', db.String), 
            db.Column('time', db.String),
            db.Column('response', db.String),
            db.Column('server', db.String),
            )
            meta.create_all(engine)
        if db.inspect(engine).has_table("ip_addr"):
            print("ip_addr table has been already created")
        else:
            print("Creating ip_addr table")
            meta = db.MetaData()
            ip_table = db.Table(
            'ip_addr', meta, 
            db.Column('id', db.Integer, primary_key = True), 
            db.Column('ip_addr', db.String), 
            db.Column('freq', db.String),
            db.Column('last_run', db.String),
            db.Column('next_run', db.String),
            db.Column('server', db.String),
            )
            meta.create_all(engine)

    """def writeResponse(ip_addr, createTime, response, server):
        try:
            engine.execute('INSERT INTO ping1(ip_addr, time, response, server) VALUES (:Ip_addr, :Time, :Response, :Server)', Ip_addr = ip_addr, Time = createTime, Response = response, Server = server)
            logging.debug('Ip adresa '+ ip_addr + ' uspesne zapsana do DB')
            return True
        except:
            logging.error('Ip adresu '+ ip_addr + ' se nepodarilo zapsat do DB')
            return False"""

    """def getResponse(ip): #
        result = engine.execute('SELECT * FROM ping1 WHERE ip_addr=:Ip_addr', Ip_addr=ip)
        row = result.fetchone()
        for k in row.keys():
            print(k.ip_addr)  """

    
    # After init: each ipAddr is deleted from database, then is loaded new from config file
    def updateIpAddr():
        engine.execute('DELETE FROM ip_addr')

        with open("config.json", "r") as f:
            config = json.loads(f.read())
        tasks = config["tasks"]

        for i in tasks:
            if "address" in i and "freq" in i:
                engine.execute('INSERT INTO ip_addr(ip_addr, freq, last_run, next_run) VALUES (:Ip_addr, :Freq, 0, 0)', Ip_addr = i['address'], Freq = i['freq'])

    def getAllAddr(self):
        result = engine.execute('SELECT * FROM ip_addr')
        rows = result.fetchall()
        return rows
    
    #write response of tested addr to db
    def addResponse(self, ip, time, response, nextTime, server):
        engine.execute('INSERT INTO ping1(ip_addr, time, response, server) VALUES (:Ip_addr, :Time, :Response, :Server)', Ip_addr = ip, Time = time, Response = response, Server = server)
        result = engine.execute('UPDATE ip_addr SET last_run =:Last_run, next_run =:Next_run WHERE ip_addr=:Ip_addr ', Last_run = time, Ip_addr = ip, Next_run = nextTime)
  
  
    """ EXPORT to API """  
    #generate JSON of average response time of each ip addresses, dateFrom and dateTo are optinal   
    def getAvrgResponseAll(self, dateFrom = None, dateTo = None):
        secFrom = None
        secTo = None
        if dateFrom != None:
            x = dateFrom.split("-")
            datetime_object = datetime.datetime(int(x[0]), int(x[1]), int(x[2]))
            secFrom = datetime_object.timestamp()

        if dateTo != None:
            x = dateTo.split("-")
            datetime_object = datetime.datetime(int(x[0]), int(x[1]), int(x[2]))
            secTo = datetime_object.timestamp()
        
        addresses = self.getAllAddr()
        json1 = {}
        counter = 0
        d = {}
        for i in addresses:
            if dateFrom != None and dateTo != None:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeFrom = secFrom, timeTo = secTo)
            elif dateFrom != None:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = secFrom)
            elif dateTo != None:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = secTo)
            else:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])    
            result = result.fetchone()[0]
            d[counter] = {} #adding to dictionary, in the end is created json
            d[counter]["address"] = i["ip_addr"]
            d[counter]["average"] = result
            counter = counter + 1
        return json.loads(json.dumps(d))

    #get info is detailed list of addresses (generate: number of addr records, first time testing, last time testing and average responsing time)
    def getAddrInfo(self, dateFrom = None, dateTo = None):
        secFrom = None
        secTo = None
        if dateFrom != None:
            x = dateFrom.split("-")
            datetime_object = datetime.datetime(int(x[0]), int(x[1]), int(x[2]))
            secFrom = int(datetime_object.timestamp())

        if dateTo != None:
            x = dateTo.split("-")
            datetime_object = datetime.datetime(int(x[0]), int(x[1]), int(x[2]))
            secTo = int(datetime_object.timestamp())

        
        addresses = self.getAllAddr()
        json1 = {}
        print(json1)
        counter = 0


        d = {}
        for i in addresses:
            if dateFrom != None and dateTo != None:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeFrom = secFrom, timeTo = secTo)
                count = engine.execute('SELECT COUNT(id) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeFrom = secFrom, timeTo = secTo)
                firstTime = engine.execute('SELECT MIN(time) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeFrom = secFrom, timeTo = secTo)
                lastTime = engine.execute('SELECT MAX(time) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeFrom = secFrom, timeTo = secTo)
            elif dateFrom != None:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = secFrom)
                count = engine.execute('SELECT COUNT(id) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = secFrom)
                firstTime = engine.execute('SELECT MIN(time) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = secFrom)
                lastTime = engine.execute('SELECT MAX(time) FROM ping1 WHERE ip_addr=:Ip_addr AND time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = secFrom)
            elif dateTo != None:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = secTo)
                count = engine.execute('SELECT COUNT(id) FROM ping1 WHERE ip_addr=:Ip_addr AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = secTo)
                firstTime = engine.execute('SELECT MIN(time) FROM ping1 WHERE ip_addr=:Ip_addr AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = secTo)
                lastTime = engine.execute('SELECT MAX(time) FROM ping1 WHERE ip_addr=:Ip_addr AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = secTo)
            else:
                result = engine.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])            
                count = engine.execute('SELECT COUNT(id) FROM ping1 WHERE ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])
                firstTime = engine.execute('SELECT MIN(time) FROM ping1 WHERE ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])
                lastTime = engine.execute('SELECT MAX(time) FROM ping1 WHERE ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])

            result = result.fetchone()[0]
            d[counter] = {}
            d[counter]["address"] = i["ip_addr"]
            d[counter]["average"] = result
            d[counter]["numberPing"] = count.fetchone()[0]
            d[counter]["firstTime"] = firstTime.fetchone()[0]
            d[counter]["lastTime"] = lastTime.fetchone()[0]
            counter = counter + 1
        return json.loads(json.dumps(d))

            

