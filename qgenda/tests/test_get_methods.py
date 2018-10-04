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

    def test_get_schedule_odata(self):
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
                self.test_get_schedule_odata()
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


class TestTask(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_get_task(self):
        response = self.client.get_task()
        self.assertEqual(response.status_code, 200)
        tasks = json.loads(response.text)


@unittest.skip('401 Unauthorized')
class TestTimeevent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_get_timeevent_start_only(self):
        now = datetime.datetime.now()
        now_str = now.strftime("%m/%d/%Y")
        now_sane_str = now.strftime("%Y-%m-%dT00:00:00")
        response = self.client.get_timeevent(start_date=now_str)
        self.assertEqual(response.status_code, 200)
        timeevents = json.loads(response.text)
        bad_entries = list(filter(lambda x: x['Date'] != now_sane_str, timeevents))
        self.assertFalse(any(bad_entries))

    def test_get_timeevent_start_end(self):
        now = datetime.datetime.now()
        later = now + datetime.timedelta(days=10)
        now_str = now.strftime("%m/%d/%Y")
        later_str = later.strftime("%m/%d/%Y")
        now_sane_str = now.strftime("%Y-%m-%dT00:00:00")
        later_sane_str = later.strftime("%Y-%m-%dT00:00:00")
        response = self.client.get_timeevent(start_date=now_str, end_date=later_str)
        self.assertEqual(response.status_code, 200)
        timeevent = json.loads(response.text)
        bad_entries = list(filter(lambda x: not (now_sane_str <= x['Date'] <= later_sane_str), timeevent))
        # print(json.dumps(bad_entries, indent=4))
        self.assertFalse(any(bad_entries))

    def test_get_timeevent_odata(self):
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
        response = self.client.get_timeevent(start_date=now_str, end_date=later_str, odata_kwargs=odata_kwargs)
        self.assertEqual(response.status_code, 200)
        timeevent = json.loads(response.text)
        bad_entries = list(filter(lambda x: not (now_sane_str <= x['Date'] <= later_sane_str), timeevent))
        unfiltered = list(filter(lambda x: not x['StaffEmail'].startswith('c'), timeevent))
        prior, unordered, unselected = '1999-01-01', [], []
        for entry in timeevent:
            unordered.append(prior > entry["Date"])
            unselected.append(all(key not in selected for key in entry.keys()))
            prior = entry["Date"]
        self.assertFalse(any(bad_entries), "Some dates are out of the selected date range")
        self.assertFalse(any(unselected), "Some entries had selections not included in the $select statement.")
        self.assertFalse(any(unordered), "Some dates are out of order.")
        self.assertFalse(any(unfiltered), "Some emails do not start with the letter c.")


class TestFacility(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_get_facility(self):
        response = self.client.get_facility()
        self.assertEqual(response.status_code, 200)
        facilities = json.loads(response.text)

    @unittest.skip('401 Unauthorized when odata is included and the results set is empty')
    def test_get_facility_odata(self):
        selected = ['Name', 'ID']
        odata_kwargs = {
            '$select': ','.join(selected),
            '$_select': ','.join(selected),
            '$orderby': 'ID',
            '$filter': "startswith(Name, 'C')",
        }
        response = self.client.get_facility(odata_kwargs=odata_kwargs)
        self.assertEqual(response.status_code, 200)
        facilities = json.loads(response.text)
        unfiltered = list(filter(lambda x: not x['StaffEmail'].startswith('c'), facilities))
        prior, unordered, unselected = '0', [], []
        for entry in facilities:
            unordered.append(prior > entry["StaffEmail"])
            unselected.append(all(key not in selected for key in entry.keys()))
            prior = entry["StaffEmail"]
        self.assertFalse(any(unfiltered), "Some emails do not start with the letter c.")
        self.assertFalse(any(unselected), "Some entries had selections not included in the $select statement.")
        self.assertFalse(any(unordered), "Some emails are out of order.")


@unittest.skip('401 Unauthorized')
class TestDailycase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_get_dailycase_start_only(self):
        now = datetime.datetime.now()
        now_str = now.strftime("%m/%d/%Y")
        now_sane_str = now.strftime("%Y-%m-%dT00:00:00")
        response = self.client.get_dailycase(start_date=now_str)
        self.assertEqual(response.status_code, 200)
        dailycases = json.loads(response.text)
        bad_entries = list(filter(lambda x: x['Date'] != now_sane_str, dailycases))
        self.assertFalse(any(bad_entries))

    def test_get_dailycase_start_end(self):
        now = datetime.datetime.now()
        later = now + datetime.timedelta(days=10)
        now_str = now.strftime("%m/%d/%Y")
        later_str = later.strftime("%m/%d/%Y")
        now_sane_str = now.strftime("%Y-%m-%dT00:00:00")
        later_sane_str = later.strftime("%Y-%m-%dT00:00:00")
        response = self.client.get_dailycase(start_date=now_str, end_date=later_str)
        self.assertEqual(response.status_code, 200)
        dailycase = json.loads(response.text)
        bad_entries = list(filter(lambda x: not (now_sane_str <= x['Date'] <= later_sane_str), dailycase))
        # print(json.dumps(bad_entries, indent=4))
        self.assertFalse(any(bad_entries))

    def test_get_dailycase_odata(self):
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
        response = self.client.get_dailycase(start_date=now_str, end_date=later_str, odata_kwargs=odata_kwargs)
        self.assertEqual(response.status_code, 200)
        dailycase = json.loads(response.text)
        bad_entries = list(filter(lambda x: not (now_sane_str <= x['Date'] <= later_sane_str), dailycase))
        unfiltered = list(filter(lambda x: not x['StaffEmail'].startswith('c'), dailycase))
        prior, unordered, unselected = '1999-01-01', [], []
        for entry in dailycase:
            unordered.append(prior > entry["Date"])
            unselected.append(all(key not in selected for key in entry.keys()))
            prior = entry["Date"]
        self.assertFalse(any(bad_entries), "Some dates are out of the selected date range")
        self.assertFalse(any(unselected), "Some entries had selections not included in the $select statement.")
        self.assertFalse(any(unordered), "Some dates are out of order.")
        self.assertFalse(any(unfiltered), "Some emails do not start with the letter c.")


@unittest.skip("Don't have an Organization Key")
class TestOrganization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = QGendaClient(raise_errors=True)

    def test_get_organization(self):
        response = self.client.get_organization()
        self.assertEqual(response.status_code, 200)
        companies = json.loads(response.text)


if __name__ == '__main__':
    unittest.main()
