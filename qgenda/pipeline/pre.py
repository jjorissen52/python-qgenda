import time

from qgenda import settings
from qgenda import helpers


def gzip_headers(method_self, method=None, params=None):
    if method.__name__ not in method_self.gzip_safe:
        use_gzip = params.pop('gzip', False)
        params['headers'] = method_self.headers if use_gzip else {
            key: value for key, value in method_self.headers.items() if value != 'gzip'
        }
    return method_self, params


def keep_authenticated(method_self, method=None, params=None):
    """

    """
    request_start = time.time()
    auth_details = method_self.auth_details
    expiration_time = auth_details.get("expiration_time", 0) if auth_details else 0
    if method_self.leader and not auth_details:
        method_self.authenticate()
        auth_details = method_self.auth_details
    else:
        retries = 10
        while retries:
            if expiration_time - request_start <= 0:
                time.sleep(1)
                auth_details = method_self.auth_details
            if auth_details:
                break
            retries -= 1
    if "access_token" in auth_details:
        method_self.headers.update({"Authorization": f'bearer {auth_details["access_token"]}'})
        params['headers'].update({"Authorization": f'bearer {auth_details["access_token"]}'})
    return method_self, params


def prepare_odata(logger):
    odata_filters = {'$filter', '$select', '$orderby'}

    def real_decorator(method_self, method, params):
        odata_kwargs = params.get('odata_kwargs', {})
        extra = []
        if odata_kwargs:
            extra = [key for key in odata_kwargs.keys() if key not in odata_filters]
        if extra:
            for e in extra:
                odata_kwargs.pop(e)
            logger.warning(f'Extra OData filter(s) removed from kwargs. Invalid filter {extra}')
        params['odata_kwargs'] = odata_kwargs
        return method_self, params
    return real_decorator


def prepare_extra_params(logger):

    def real_decorator(method_self, method, params):
        # intentional index error if not defined
        all_available_params = {
            # params defined explicitly in the function definition,
            # retrieved from the value set during the pipeline, if available
            *getattr(
                method,
                '_original_arg_names',
                {*helpers.get_arg_names(method)}
            ),
            # params defined in settings
            *settings.PARAMS[f'{method.__name__}_params']
        }
        for param in [*params]:
            if param not in all_available_params:
                params.pop(param)
                logger.warning(f'Extra param removed from kwargs: {param}')
        return method_self, params
    return real_decorator


def prepare_params(logger):
    _prep_odata = prepare_odata(logger)
    _prep_extras = prepare_extra_params(logger)

    def real_decorator(method_self, method, params):
        method_self, params = _prep_odata(method_self, method, params)
        method_self, params = _prep_extras(method_self, method, params)
        return method_self, params
    return real_decorator
