import datetime
import json
import time
import unittest
import logging

from qgenda.api.client import QGendaClient

logger = logging.getLogger(__name__)


class TestAuthentication(unittest.TestCase):

    """
    This is assuming good config.
    """
    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_auth(self):
        self.client.authenticate()
        required = ["access_token", "token_type", "expires_in", "expiration_time"]
        self.assertTrue(all(key in self.client.auth_details for key in required))


class TestSchedule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_get_schedule_start_only(self):
        now = datetime.datetime.now()
        now_str = now.strftime("%m/%d/%Y")
        now_sane_str = now.strftime("%Y-%m-%dT00:00:00")
        response = self.client.get_schedule(start_date=now_str)
        self.assertEqual(response.status_code, 200)
        schedule = json.loads(response.text)
        bad_entries = list(filter(lambda x: x['Date'] != now_sane_str, schedule))
        self.assertFalse(any(bad_entries))

    def test_get_schedule_start_end(self):
        now = datetime.datetime.now()
        later = now + datetime.timedelta(days=10)
        now_str = now.strftime("%m/%d/%Y")
        later_str = later.strftime("%m/%d/%Y")
        now_sane_str = now.strftime("%Y-%m-%dT00:00:00")
        later_sane_str = later.strftime("%Y-%m-%dT00:00:00")
        response = self.client.get_schedule(start_date=now_str, end_date=later_str)
        self.assertEqual(response.status_code, 200)
        schedule = json.loads(response.text)
        bad_entries = list(filter(lambda x: not (now_sane_str <= x['Date'] <= later_sane_str), schedule))
        # print(json.dumps(bad_entries, indent=4))
        self.assertFalse(any(bad_entries))

    def test_odata(self):
        now = datetime.datetime.now()
        later = now + datetime.timedelta(days=10)
        now_str = now.strftime("%m/%d/%Y")
        later_str = later.strftime("%m/%d/%Y")
        now_sane_str = now.strftime("%Y-%m-%dT00:00:00")
        later_sane_str = later.strftime("%Y-%m-%dT00:00:00")
        selected = ['Date', 'StaffEmail']
        odata_kwargs = {
            '$_select': 'Date',
            '$select': ','.join(selected),
            '$orderby': 'Date',
            '$filter': "startswith(StaffEmail, 'c')",
        }
        response = self.client.get_schedule(start_date=now_str, end_date=later_str, odata_kwargs=odata_kwargs)
        self.assertEqual(response.status_code, 200)
        schedule = json.loads(response.text)
        bad_entries = list(filter(lambda x: not (now_sane_str <= x['Date'] <= later_sane_str), schedule))
        prior, unordered, unselected = '1999-01-01', [], []
        for entry in schedule:
            unordered.append(prior > entry["Date"])
            unselected.append(all(key not in selected for key in entry.keys()))
            prior = entry["Date"]
        self.assertFalse(any(bad_entries), "Some dates are out of the selected date range")
        self.assertFalse(any(unselected), "Some entries had selections not included in the $select statement.")
        self.assertFalse(any(unordered), "Some dates are out of order.")

    def test_cache(self):
        if self.client.use_caching:
            start = time.time()
            for i in range(100):
                self.test_odata()
                latest = time.time()
                self.assertTrue(latest - start < 3, 'Caching test is taking too long. '
                                                    'Caching is slow or improperly configured.')
        else:
            logger.info('Cache disabled.')


class TestStaff(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_get_staff(self):
        response = self.client.get_staff()
        self.assertEqual(response.status_code, 200)
        response_dict = json.loads(response.text) # just making sure it's possible


if __name__ == '__main__':
    unittest.main()
