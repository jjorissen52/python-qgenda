import logging
import requests

from qgenda.pipeline import handlers, pre, pipelines, post
from qgenda.api.exceptions import APICallError
from qgenda import settings
from qgenda.cache import cache

logger = logging.getLogger(__name__)


class QGendaClient:
    """
    NOTE TO API DEVELOPERS: ALL ARGUMENTS FOR NEWLY IMPLEMENTED METHODS
    MUST BE GIVEN A DEFAULT OR THINGS WILL BE BROKEN.
    """
    # have to set a default here or the auth_details getter will raise an error.
    use_caching = settings.USE_CACHING

    @handlers.log_bad_config(logger)
    def __init__(self, username=settings.USERNAME, password=settings.PASSWORD, company_key=settings.COMPANY_KEY,
                 api_url=settings.API_URL, api_version=settings.API_VERSION, headers=None,
                 raise_errors=True, use_caching=settings.USE_CACHING, leader=True):
        self.username = username
        self.password = password
        self.company_key = company_key
        self.api_url = f'{api_url.strip("/")}/{api_version.strip("/")}/'
        self.api_version = api_version
        self.raise_errors = raise_errors
        self.auth_details = dict()
        self.headers = headers if headers else {
            'user-agent': f'python-qgenda {self.username}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Transfer-Encoding': 'gzip',
        }
        # list of methods that it is safe to include gzip headers for
        self.gzip_safe = []
        self.use_caching = use_caching
        self.leader = leader

    def show_config(self):
        print(self.username, self.password, self.company_key, self.api_url,
              self.raise_errors, self.auth_details, self.headers, self.use_caching)

    @property
    def auth_details(self):
        """
        getter for auth_details. used for maintaining local and shared state
        :return:
        """
        if not self.use_caching:
            return self.__auth_details
        auth_details = self.__auth_details if self.__auth_details else cache.get('auth_details', default={})
        return auth_details

    @auth_details.setter
    def auth_details(self, arg):
        self.__auth_details = arg
        if self.use_caching and not cache.get('auth_details'):
            cache.set('auth_details', arg, settings.CACHE_LIFETIME)

    @pipelines.pre_execution_pipeline(pre.gzip_headers)
    @pipelines.post_execution_pipeline(post.handle_login_response, post.handle_error_response(logger))
    def authenticate(self, headers=None):
        """
        Authenticate against their provider for an OAuth token.

        :raise_errors: (kwarg: True) Raise an error on authentication failure
        :return: (dict) {"access_token:" <jwt_access_token>, "token_type": <token_type>, "expires_in": <seconds> }
        """
        login_url = f'{self.api_url.strip("/")}/login'
        params = {
            'email': self.username,
            'password': self.password,
        }
        headers = headers if headers else self.headers
        response = requests.post(login_url, data=params, headers=headers)
        return response

    @pipelines.pre_execution_pipeline(pre.gzip_headers, pre.keep_authenticated, pre.prepare_odata(logger))
    @pipelines.post_execution_pipeline(post.handle_error_response(logger))
    def get_schedule(self, start_date=None, end_date=None, odata_kwargs=None, headers=None):
        schedule_url = f'{self.api_url.strip("/")}/schedule'
        if not start_date:
            raise APICallError('start_date is a required argument.')
        params = {'startDate': start_date, 'companyKey': self.company_key}
        if end_date:
            params.update({"endDate": end_date})
        if odata_kwargs:
            params.update(odata_kwargs)
        headers = headers if headers else self.headers
        response = requests.get(schedule_url, params=params, headers=headers)
        return response

    @pipelines.pre_execution_pipeline(pre.gzip_headers, pre.keep_authenticated, pre.prepare_odata(logger))
    @pipelines.post_execution_pipeline(post.handle_error_response(logger))
    def get_staff(self, odata_kwargs=None, headers=None):
        schedule_url = f'{self.api_url.strip("/")}/staffmember'
        params = {**odata_kwargs} if odata_kwargs else {}
        headers = headers if headers else self.headers
        response = requests.get(schedule_url, params=params, headers=headers)
        return response

    @pipelines.pre_execution_pipeline(pre.gzip_headers, pre.keep_authenticated, pre.prepare_odata(logger))
    @pipelines.post_execution_pipeline(post.handle_error_response(logger))
    def get_facility(self, odata_kwargs=None, headers=None):
        facility_url = f'{self.api_url.strip("/")}/facility'
        params = {'companyKey': self.company_key}
        if odata_kwargs:
            params.update(odata_kwargs)
        headers = headers if headers else self.headers
        response = requests.get(facility_url, params=params, headers=headers)
        return response

    @pipelines.pre_execution_pipeline(pre.gzip_headers, pre.keep_authenticated, pre.prepare_odata(logger))
    @pipelines.post_execution_pipeline(post.handle_error_response(logger))
    def get_organization(self, odata_kwargs=None, headers=None, organization_key=None):
        if not organization_key:
            raise APICallError('organization_key is a required argument.')
        organization_url = f'{self.api_url.strip("/")}/organization'
        params = {'OrganizationKey': organization_key}
        if odata_kwargs:
            params.update(odata_kwargs)
        headers = headers if headers else self.headers
        response = requests.get(organization_url, params=params, headers=headers)
        return response

    @pipelines.pre_execution_pipeline(pre.gzip_headers, pre.keep_authenticated, pre.prepare_odata(logger))
    @pipelines.post_execution_pipeline(post.handle_error_response(logger))
    def get_task(self, odata_kwargs=None, headers=None):
        task_url = f'{self.api_url.strip("/")}/task'
        params = {**odata_kwargs} if odata_kwargs else {}
        headers = headers if headers else self.headers
        response = requests.get(task_url, params=params, headers=headers)
        return response

    @pipelines.pre_execution_pipeline(pre.gzip_headers, pre.keep_authenticated, pre.prepare_odata(logger))
    @pipelines.post_execution_pipeline(post.handle_error_response(logger))
    def get_timeevent(self, start_date=None, end_date=None, odata_kwargs=None, headers=None):
        timeevent_url = f'{self.api_url.strip("/")}/timeevent'
        if not start_date:
            raise APICallError('start_date is a required argument.')
        params = {'startDate': start_date, 'companyKey': self.company_key}
        if end_date:
            params.update({"endDate": end_date})
        if odata_kwargs:
            params.update(odata_kwargs)
        headers = headers if headers else self.headers
        response = requests.get(timeevent_url, params=params, headers=headers)
        return response

    @pipelines.pre_execution_pipeline(pre.gzip_headers, pre.keep_authenticated, pre.prepare_odata(logger))
    @pipelines.post_execution_pipeline(post.handle_error_response(logger))
    def get_dailycase(self, start_date=None, end_date=None, odata_kwargs=None, headers=None):
        dailycase_url = f'{self.api_url.strip("/")}/dailycase'
        if not start_date:
            raise APICallError('start_date is a required argument.')
        params = {'startDate': start_date, 'companyKey': self.company_key}
        if end_date:
            params.update({"endDate": end_date})
        if odata_kwargs:
            params.update(odata_kwargs)
        headers = headers if headers else self.headers
        response = requests.get(dailycase_url, params=params, headers=headers)
        return response

    def post_staff(self, *args, **kwargs):
        raise NotImplementedError('POST methods non-functional.')
