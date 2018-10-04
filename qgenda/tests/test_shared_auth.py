import datetime
import json
import time
import unittest
import logging

from qgenda.api.client import QGendaClient
from qgenda.api import exceptions

logger = logging.getLogger(__name__)


class TestSharedAuth(unittest.TestCase):
    """
    Testing the leader/follower implementation.
    """

    def test_bad_config(self):
        with self.assertRaises(exceptions.ImproperlyConfigured):
            client = QGendaClient(raise_errors=True, use_caching=False, leader=False)

    def test_shared_auth_basic(self):
        client1 = QGendaClient(raise_errors=True, leader=True)
        if not client1.use_caching:
            logger.warning('Caching is disabled and shared auth will not be used.')
            return
        client2 = QGendaClient(raise_errors=True, leader=False)
        response1 = client1.get_staff()
        response2 = client2.get_staff()
        self.assertTrue(response1.status_code, 200)
        self.assertTrue(response2.status_code, 200)

    def test_shared_auth_excessive(self):
        leader = QGendaClient(raise_errors=True, leader=True)
        if not leader.use_caching:
            logger.warning('Caching is disabled and shared auth will not be used.')
            return
        response = leader.get_staff()
        self.assertTrue(response.status_code, 200)
        start = time.time()
        for i in range(100):
            client = QGendaClient(raise_errors=True, leader=False)
            response = client.get_staff()
            self.assertTrue(response.status_code, 200)
            latest = time.time()
            self.assertTrue(latest - start < 3, 'Caching test is taking too long. '
                                                'Caching is slow or improperly configured.')


if __name__ == '__main__':
    unittest.main()
