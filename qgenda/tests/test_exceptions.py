import unittest
import os
import json
os.environ['QGENDA_CONF_REGION'] = 'qgenda_test'  # ensure bad imports
from qgenda.api.client import QGendaClient
from qgenda.api import exceptions

"""
NOTE: RUNNING THIS TEST WILL RUIN YOUR IMPORTS! YOU WILL NEED TO RUN THIS TEST SEPARATELY FROM THE OTHERS!
"""


class TestRaises(unittest.TestCase):

    def test_improper_config(self):
        with self.assertRaises(exceptions.ImproperlyConfigured):
            QGendaClient(None, 'password', company_key=None, raise_errors=True)

    def test_bad_login(self):
        with self.assertRaises(exceptions.HTTPError):
            client = QGendaClient('username', 'password', 'company_key', api_version='v2',
                                  api_url='https://api.qgenda.com/', raise_errors=True)
            client.authenticate()


class TestNoRaise(unittest.TestCase):

    def test_bad_login(self):
        client = QGendaClient('username', 'password', 'company_key', api_version='v2',
                              api_url='https://api.qgenda.com/', raise_errors=False)
        resp = client.authenticate()
        json_resp = json.loads(resp.text)
        self.assertTrue(all(key in json_resp for key in ["error", "error_description"]))


if __name__ == '__main__':
    unittest.main()
