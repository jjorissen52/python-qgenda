import datetime
import json
import unittest
from unittest.mock import MagicMock, patch
from qgenda.api import client


def mock_auth(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({
        "access_token": None,
        "token_type": None,
        "expires_in": 10000000000000,
        "expiration_time": 10000000000000,
    })
    mock_requests.post.return_value = mock_response


def mock_get_200(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps([])
    mock_requests.get.return_value = mock_response


@patch('qgenda.api.client.logger.warning', lambda *args: None)
@patch('qgenda.api.client.logger.error', lambda *args: None)
class TestPreparedParams(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = client.QGendaClient(raise_errors=False)

    @patch('qgenda.api.client.requests')
    def test_get_schedule(self, mock_requests):
        mock_auth(mock_requests)
        self.client.authenticate()

        now = datetime.datetime.now()
        now_str = now.strftime("%m/%d/%Y")

        bad_extras = dict(sup=1, okay=2)
        good_extras = dict(sinceModifiedTimestamp=1, includeDeletes=1)
        mock_get_200(mock_requests)
        self.client.get_schedule(start_date=now_str, **bad_extras, **good_extras)

        for bad in bad_extras:
            self.assertNotIn(bad, mock_requests.get.call_args[1]['params'])
        for good in good_extras:
            self.assertIn(good, mock_requests.get.call_args[1]['params'])
