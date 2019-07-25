import configparser
import os
import logging

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_CONF_FILE = os.environ.get('QGENDA_CONF_FILE')
ENV_CONF_REGION = os.environ.get('QGENDA_CONF_REGION')
DEBUG = bool(os.environ.get('QGENDA_DEBUG'))
if ENV_CONF_FILE:
    CONF_FILE = ENV_CONF_FILE
else:
    CONF_FILE = ''
    logging.warn('Please make sure you set the QGENDA_CONF_FILE '
                 'environment variable. API will not function without it.')
CONF_REGION = ENV_CONF_REGION if ENV_CONF_REGION else 'qgenda'
DEFAULTS = {
    'company_key': None,
    'username': None,
    'password': None,
    'api_url': 'https://api.qgenda.com/',
    'api_version': 'v2',
    'cache_backend': None,
    'cache_host': None,
    'cache_port': None,
    'cache_lifetime': 0,
    'debug': DEBUG,
}


def read_config(keys):
    """
    We don't want a failed import for bad config, we just want to set everything that is not in the config file/region
    set to None
    :param keys: (iterable) default keys to set to None
    :return:
    """
    config = configparser.ConfigParser(defaults=DEFAULTS, allow_no_value=True)
    config.read(CONF_FILE)
    if not config.has_section(CONF_REGION):
        config.add_section(CONF_REGION)

    parameters = {key: config.get(CONF_REGION, key) for key in keys}
    parameters.update({'config': config})
    return parameters


config_dict = read_config(DEFAULTS.keys())

COMPANY_KEY = config_dict.get('company_key')
USERNAME = config_dict.get('username')
PASSWORD = config_dict.get('password')
API_URL = config_dict.get('api_url')
API_VERSION = config_dict.get('api_version')
CACHE_BACKEND = config_dict.get('cache_backend')
USE_CACHING = bool(CACHE_BACKEND)
CACHE_HOST = config_dict.get('cache_host')
CACHE_PORT = config_dict.get('cache_port')
CACHE_LIFETIME = int(config_dict.get('cache_lifetime') if config_dict.get('cache_lifetime') else 0)
DEBUG = config_dict.get('debug')

