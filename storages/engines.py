"""Engines

This script allows the user to pick the engine type for the writing
and the reading of the logs.

This script will be utilized more when more engines are provided.

It also provides TABLES which are used to create the csv files.

"""

# from storages import storage_sqlite3
from storages import storage_csv

def get_writer_engine(engine_config):
    """Getting the engine for writing.(currently only csv is available)"""
    name = engine_config["type"]
    return ENGINES[name][0](engine_config, TABLES)

def get_reader_engine(engine_config):
    """Getting the engine for reading.(currently only csv is available)"""
    name = engine_config["type"]
    return ENGINES[name][1](engine_config, TABLES)


ENGINES = {
         # "sqlite3": storage_sqlite3.Sqlite3Writer, # TODO enable when ready
    "csv": (storage_csv.CSVWriter, storage_csv.CSVReader),
}

TABLES = {
    "ping": {"columns": ["address", "time", "value"], "index": "time"},
    "errors": {"columns": ["time", "message"], "index": "time"}
}

