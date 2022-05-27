"""
For devel:
python -m uvicorn main:app --reload

For production:
uvicorn main:app --host 0.0.0.0 --port 80
"""
from multiprocessing import Process
import time

import uvicorn

from modules import main_datastore

from settings import DATASTORE_APP_ADDRESS

def run_storage_app(address, port):
    """
    start the storage application with uvicorn
    """
    uvicorn.run(main_datastore.app, host=address,
                port=port, log_level="critical")

def run_storage_app_process(address, port):
    """
    run storage app as a process
    """
    storage_app_proc = Process(target=run_storage_app, args=(address, port))
    storage_app_proc.start()
    return storage_app_proc


if __name__ == "__main__":
    run_storage_app_process(*DATASTORE_APP_ADDRESS)

    while True:
        time.sleep(10)
