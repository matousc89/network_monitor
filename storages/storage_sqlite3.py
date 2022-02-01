import sqlite3


class Sqlite3Writer():

    def __init__(self, config, tables):
        # TODO catch exception
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

        #  TODO create all tables
        # TODO for table in tables:
        try:
            self.cursor.execute('''CREATE TABLE ping
                           (address, time, value)''') # TODO make it working with engines list
        except:
            pass

    def write(self, response):
        self.cursor.execute("INSERT INTO") # TODO replace text with response
        self.connection.commit()

