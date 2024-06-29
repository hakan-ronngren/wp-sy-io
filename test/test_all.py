import unittest

# Import the local modules from the test directory
from test_api_mock import *  # NOSONAR | I really want to import all the tests
from test_php import *     # NOSONAR | without having to list them all here

if __name__ == '__main__':
    unittest.main()
