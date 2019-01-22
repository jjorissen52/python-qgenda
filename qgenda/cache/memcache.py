import pickle
import logging

from memcache import Client

logger = logging.getLogger(__name__)


class MemCache(Client):

    def __init__(self, **kwargs):
        """

        :param args: (host, port)
        """
        args = (kwargs.get('host', 'localhost'), int(kwargs.get('port', 11211)))
        super().__init__([
            args
        ])

    def get(self, key=None, default=None):
        cached_pickle = super().get(key)
        cached_obj = pickle.loads(cached_pickle) if cached_pickle else default
        return cached_obj

    def set(self, key=None, obj=None, expiration_seconds=3600):
        pickled_obj = pickle.dumps(obj) if obj is not None else None
        if pickled_obj is not None:
            super().set(key, pickled_obj, expiration_seconds)
            return True
        return False

    def clear(self):
        self.flushdb()
