"""
Test suite - run all tests.
"""
import unittest

from tests.test_datastore import TestingDatastore # noqa # pylint: disable=unused-import
from tests.test_worker import TestingWorker # noqa # pylint: disable=unused-import

if __name__ == "__main__":
    unittest.main()


