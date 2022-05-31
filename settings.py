"""
Hardcoded settings for the project
"""
import sys
import pathlib

from modules.common import build_url

## User specified part

TESTING = False

DATABASE_FOLDER = "databases"
LOG_FOLDER = "logs"

DATASTORE_DATABASE_FILE = "datastore.db"
DATASTORE_APP_ADDRESS = ("127.0.0.1", 8000)

WORKER_DATABASE_FILE = "worker.db"

LOG_FILE = 'main.log'


## Testing override

if 'unittest' in sys.modules.keys():
    TESTING = True

    DATASTORE_DATABASE_FILE = "datastore_test.db"
    DATASTORE_APP_ADDRESS = ("127.0.0.1", 5000)

    WORKER_DATABASE_FILE = "worker_test.db"

    LOG_FILE = 'main_test.log'


## Calculated part

DATASTORE_APP_URL = build_url(*DATASTORE_APP_ADDRESS)
DATASTORE_DATABASE = pathlib.PurePath(DATABASE_FOLDER, DATASTORE_DATABASE_FILE)

WORKER_DATABASE = pathlib.PurePath(DATABASE_FOLDER, WORKER_DATABASE_FILE)

LOG = pathlib.PurePath(LOG_FOLDER, LOG_FILE)