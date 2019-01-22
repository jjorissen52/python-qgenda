import functools
import sys

from qgenda import helpers
from qgenda.cache import cache
from qgenda.settings import CACHE_LIFETIME


class pre_execution_pipeline:

    def __init__(self, *pipline_functions):
        self.pipeline_functions = pipline_functions
        for pipeline in self.pipeline_functions:
            module = str(sys.modules[pipeline.__module__])
            assert 'pipeline.pre' in module, f'{pipeline.__name__} must be in qgenda_api.pipeline.pre'

    def __call__(self, method):
        @functools.wraps(method)
        def decorated(client_obj, *args, **kwargs):
            params = helpers.named_method_params(method, args, kwargs)
            request_key = f'{method.__name__}:{args}:{kwargs}'.replace(' ', '_')  # memcached does not allow spaces
            setattr(client_obj, 'latest_request_key', request_key)
            cached_response = cache.get(request_key) if client_obj.use_caching else None
            if cached_response:
                return cached_response
            caller_name = method.__name__
            # need to save caller so the pos_execution pipeline can get access.
            if not getattr(self, 'caller', None):
                setattr(self, 'caller', method)
            for pipline_func in self.pipeline_functions:
                client_obj, caller_name, params = pipline_func(client_obj, caller_name, params)
            # storing execution params and cache key on client for use by post_execution_pipeline
            setattr(client_obj, 'latest_execution_params', {**params})
            return method(client_obj, **params)
        return decorated


class post_execution_pipeline:
    """
    object pass in __call__ will either be a method or a pre-execution pipeline.
    """

    def __init__(self, *pipline_functions):
        self.pipeline_functions = pipline_functions
        for pipeline in self.pipeline_functions:
            module = str(sys.modules[pipeline.__module__])
            assert 'pipeline.post' in module, f'{pipeline.__name__} must be in qgenda_api.pipeline.post'

    def __call__(self, method):
        @functools.wraps(method)
        def decorated(client_self, *args, **kwargs):
            request_key = client_self.latest_request_key
            execution_params = getattr(client_self, 'latest_execution_params', None)
            response = method(client_self, *args, **kwargs)
            if not execution_params:
                return response
            for pipline_func in self.pipeline_functions:
                client_self, response = pipline_func(client_self, response)
            if client_self.use_caching:
                cache.set(request_key, response, CACHE_LIFETIME)
            return response
        return decorated
