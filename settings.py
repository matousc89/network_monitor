"""
Hardcoded settings for the project
"""
import sys

def url_from_address(address, port):
    return "http://{}:{}/".format(address, port)

TESTING = False

DATASTORE_DATABASE = "datastore.db"
DATASTORE_APP_ADDRESS = ("127.0.0.1", 8000)

WORKER_DATABASE = "worker.db"

LOG = 'datastore.log'


## Testing override
if 'unittest' in sys.modules.keys():
    TESTING = True

    DATASTORE_DATABASE = "datastore_test.db"
    DATASTORE_APP_ADDRESS = ("127.0.0.1", 5000)

    WORKER_DATABASE = "worker_test.db"

    LOG = 'datastore_test.log'


## Calculated part

DATASTORE_APP_URL = url_from_address(*DATASTORE_APP_ADDRESS)