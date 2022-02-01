"""CSV Writer and Reader

This script allows the user to store the logs in a csv file. It is assumed
that the first row of the file is the same as the config table.

This tool accepts any kind of delimiter provided in the config.

This script requires that `pandas` be installed within the Python
environment you are running this script in.

"""

import os

import pandas as pd

class CSVWriter():

    def __init__(self, config, tables):
        """Creates file according to definition that is passed in tables."""
        self.tables = tables
        self.config = config
        for name, table in tables.items():
            if not os.path.isfile(self.get_path(name)):
                with open(self.get_path(name),"w") as f:
                    header = self.config["delimiter"].join(table["columns"]) + "\n"
                    f.write(header)

            table["columns"]
        # TODO catch exception

    def write(self, response):
        """Function adds row to the file."""
        name = response["type"]
        columns = self.tables[name]["columns"]
        line = self.config["delimiter"].join([str(response[col]) for col in columns]) + "\n"
        with open(self.get_path(name),"a") as f:
            f.write(line)

    def get_path(self, name):
        """Gets path that user provided in config."""
        return os.path.join(self.config["path"], "{}{}".format(name, self.config["extension"]))


class CSVReader():

    def __init__(self, config, tables):
        self.tables = tables
        self.config = config

    def get_path(self, name):
        """Gets path that user provided in config."""
        return os.path.join(self.config["path"], "{}{}".format(name, self.config["extension"]))

    def read_table(self, filename):
        """Reads table."""
        df = pd.read_csv(filename)
        return df

    def get_tables(self):
        """Changes index and separates the values based on the delimiter and index provided."""
        dfs = {}
        for name, table in self.tables.items():
            df = pd.read_csv(self.get_path(name), delimiter=self.config["delimiter"])
            index_col = table["index"]
            df.index = df[index_col]
            df = df.drop(columns=[index_col])
            dfs[name] = df
        return dfs






