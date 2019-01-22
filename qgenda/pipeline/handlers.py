import functools
from qgenda import helpers, settings
from qgenda.api.exceptions import ImproperlyConfigured


def log_bad_config(logger):
    """
    Logs with level ERROR to the passed logger about missing keys
    :param logger:
    :return:
    """
    necessary_keys = ['username', 'password', 'company_key', 'api_url', 'api_version']

    def real_decorator(method):
        @functools.wraps(method)
        def _log_bad_config(*args, **kwargs):
            self = args[0]
            args_names = method.__code__.co_varnames[:method.__code__.co_argcount]
            params = helpers.get_default_args(method)
            args_dict = {**dict(zip(args_names, args)), **kwargs}
            params.update(args_dict)
            missing = list(key for key in necessary_keys if not params.get(key, None))
            if missing:
                logger.error(f'Your configuration {settings.CONF_FILE}:{settings.CONF_REGION} '
                             f'is missing necessary config: {", ".join(missing)}')
                if kwargs.get('raise_errors', False):
                    raise ImproperlyConfigured(f'Your configuration {settings.CONF_FILE}:[{settings.CONF_REGION}]'
                                               f'is missing necessary config: {", ".join(missing)}')
            if not params.get('leader', None) and not params.get('use_caching', None):
                raise ImproperlyConfigured('Shared auth not available without caching.')
            return method(*args, **kwargs)
        return _log_bad_config
    return real_decorator
