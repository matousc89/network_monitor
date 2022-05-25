"""
takes care of the connection to the database
"""
import logging
import json
import datetime
import sqlalchemy as db



class SqlConnector():
    """
    Sql connector
    """
    def __init__(self):
        """
        init
        """
        logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG)
        global ENGINE
        ENGINE = db.create_engine('sqlite:///network.db', echo = False)
        self.__check_table()

    @classmethod
    def __check_table(cls):
        """
        Check if tables exist
        """
        if db.inspect(ENGINE).has_table("ping1"):
            print("Ping1 has been already created")
        else:
            print("Creating ping1 table")
            meta = db.MetaData()
            db.Table(
            'ping1', meta,
            db.Column('id', db.Integer, primary_key = True),
            db.Column('ip_addr', db.String),
            db.Column('time', db.String),
            db.Column('response', db.String),
            db.Column('server', db.String),
            )
            meta.create_all(ENGINE)
        if db.inspect(ENGINE).has_table("ip_addr"):
            print("ip_addr table has been already created")
        else:
            print("Creating ip_addr table")
            meta = db.MetaData()
            db.Table(
            'ip_addr', meta,
            db.Column('id', db.Integer, primary_key = True),
            db.Column('ip_addr', db.String),
            db.Column('freq', db.String),
            db.Column('last_run', db.String),
            db.Column('next_run', db.String),
            db.Column('server', db.String),
            )
            meta.create_all(ENGINE)

    @classmethod
    def update_ip_addr(cls):
        """
        After init: each ipAddr is deleted from database, then is loaded new from config file
        """
        ENGINE.execute('DELETE FROM ip_addr')

        with open("config.json","r", encoding="utf-8") as readed_text:
            config = json.loads(readed_text.read())
        tasks = config["tasks"]

        for i in tasks:
            if "address" in i and "freq" in i:
                ENGINE.execute('INSERT INTO ip_addr(ip_addr, freq, last_run, next_run)'+
                    'VALUES (:Ip_addr, :Freq, 0, 0)', Ip_addr = i['address'], Freq = i['freq'])
    @classmethod
    def get_all_addr(cls):
        """
        Get all addresses from DB, return rows
        """
        result = ENGINE.execute('SELECT * FROM ip_addr')
        rows = result.fetchall()
        return rows

    @classmethod
    def add_response(cls, ip_addr, time, response, next_time, server):
        """
        write response of tested addr to db
        """
        ENGINE.execute('INSERT INTO ping1(ip_addr, time, response, server)'+
            ' VALUES (:Ip_addr, :Time, :Response, :Server)',
            Ip_addr = ip_addr, Time = time, Response = response, Server = server)
        ENGINE.execute('UPDATE ip_addr SET last_run =:Last_run, '+
            'next_run =:Next_run WHERE ip_addr=:Ip_addr ',
            Last_run = time, Ip_addr = ip_addr, Next_run = next_time)

    def get_avrg_response_all(self, date_from = None, date_to = None):
        """
        generate JSON of average response time of each ip addresses, dateFrom and dateTo are optinal
        """

        sec_from = None
        sec_to = None
        if date_from is not None:
            date_split = date_from.split("-")
            datetime_object = datetime.datetime(int(date_split[0]),+
                int(date_split[1]), int(date_split[2]))
            sec_from = datetime_object.timestamp()

        if date_to is not None:
            date_split = date_to.split("-")
            datetime_object = datetime.datetime(int(date_split[0]),+
                int(date_split[1]), int(date_split[2]))
            sec_to = datetime_object.timestamp()

        addresses = self.get_all_addr()
        counter = 0
        dict_new = {}
        for i in addresses:
            if date_from is not None and date_to is not None:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1 WHERE '+
                    'ip_addr=:Ip_addr AND' +
                    'time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"],
                    time_from = sec_from, time_to = sec_to)
            elif date_from is not None:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1 '+
                    'WHERE ip_addr=:Ip_addr AND' +
                    'time > :timeFrom; ', Ip_addr = i["ip_addr"], time_from = sec_from)
            elif date_to is not None:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1'+
                ' WHERE ip_addr=:Ip_addr AND'+
                ' time < :timeTo; ', Ip_addr = i["ip_addr"], time_to = sec_to)
            else:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1 WHERE'+
                ' ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])
            result = result.fetchone()[0]
            dict_new[counter] = {} #adding to dictionary, in the end is created json
            dict_new[counter]["address"] = i["ip_addr"]
            dict_new[counter]["average"] = result
            counter = counter + 1
        return json.loads(json.dumps(dict_new))

    def get_addr_info(self, date_from = None, date_to = None):
        """
            get info is detailed list of addresses (generate: number of addr records,
            first time testing, last time testing and average responsing time)
        """
        sec_from = None
        sec_to = None
        if date_from is not None:
            date_split = date_from.split("-")
            datetime_object = datetime.datetime(int(date_split[0]),+
                int(date_split[1]), int(date_split[2]))
            sec_from = int(datetime_object.timestamp())

        if date_to is not None:
            date_split = date_to.split("-")
            datetime_object = datetime.datetime(int(date_split[0]),+
                int(date_split[1]), int(date_split[2]))
            sec_to = int(datetime_object.timestamp())

        addresses = self.get_all_addr()
        json1 = {}
        print(json1)
        counter = 0


        dict_new = {}
        for i in addresses:
            if date_from is not None and date_to is not None:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr'+
                    ' AND time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"],
                    timeFrom = sec_from, timeTo = sec_to)
                count = ENGINE.execute('SELECT COUNT(id) FROM ping1 WHERE ip_addr=:Ip_addr AND'+
                    ' time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"],
                    timeFrom = sec_from, timeTo = sec_to)
                first_time = ENGINE.execute('SELECT MIN(time) FROM ping1 WHERE ip_addr=:Ip_addr'+
                    ' AND time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"],
                    timeFrom = sec_from, timeTo = sec_to)
                last_time = ENGINE.execute('SELECT MAX(time) FROM ping1 WHERE ip_addr=:Ip_addr AND'+
                    ' time > :timeFrom AND time < :timeTo; ', Ip_addr = i["ip_addr"],
                    timeFrom = sec_from, timeTo = sec_to)
            elif date_from is not None:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr'+
                    ' AND time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = sec_from)
                count = ENGINE.execute('SELECT COUNT(id) FROM ping1 WHERE ip_addr=:Ip_addr AND '+
                    ' time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = sec_from)
                first_time = ENGINE.execute('SELECT MIN(time) FROM ping1 WHERE ip_addr=:Ip_addr'+
                    ' AND time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = sec_from)
                last_time = ENGINE.execute('SELECT MAX(time) FROM ping1 WHERE ip_addr=:Ip_addr AND'+
                    ' time > :timeFrom; ', Ip_addr = i["ip_addr"], timeFrom = sec_from)
            elif date_to is not None:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1 WHERE ip_addr=:Ip_addr '+
                    'AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = sec_to)
                count = ENGINE.execute('SELECT COUNT(id) FROM ping1 WHERE ip_addr=:Ip_addr AND '
                    +'time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = sec_to)
                first_time = ENGINE.execute('SELECT MIN(time) FROM ping1 WHERE ip_addr=:Ip_addr '+
                    'AND time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = sec_to)
                last_time = ENGINE.execute('SELECT MAX(time) FROM ping1 WHERE ip_addr=:Ip_addr AND '
                    +'time < :timeTo; ', Ip_addr = i["ip_addr"], timeTo = sec_to)
            else:
                result = ENGINE.execute('SELECT AVG(response) FROM ping1 WHERE '+
                    'ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])
                count = ENGINE.execute('SELECT COUNT(id) FROM ping1 WHERE '+
                    'ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])
                first_time = ENGINE.execute('SELECT MIN(time) FROM ping1 WHERE '+
                    'ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])
                last_time = ENGINE.execute('SELECT MAX(time) FROM ping1 WHERE '+
                    'ip_addr=:Ip_addr; ', Ip_addr = i["ip_addr"])

            result = result.fetchone()[0]
            dict_new[counter] = {}
            dict_new[counter]["address"] = i["ip_addr"]
            dict_new[counter]["average"] = result
            dict_new[counter]["numberPing"] = count.fetchone()[0]
            dict_new[counter]["firstTime"] = first_time.fetchone()[0]
            dict_new[counter]["lastTime"] = last_time.fetchone()[0]
            counter = counter + 1
        return json.loads(json.dumps(dict_new))
