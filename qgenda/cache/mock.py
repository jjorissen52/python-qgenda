import logging

logger = logging.getLogger(__name__)


class MockCache:

    def __init__(self, debug=False, **kwargs):
        self.debug = True if debug else False

    def get(self, key=None, default=None):
        if self.debug:
            logger.warning('Caching config is on, but cache configurations are improperly configured or packages '
                           'are missing.')
        return None

    @staticmethod
    def set(key=None, obj=None, expiration_seconds=3600):
        return False

    @staticmethod
    def clear():
        return None