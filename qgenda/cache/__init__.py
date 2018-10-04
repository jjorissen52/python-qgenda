from qgenda import settings
import logging

logger = logging.getLogger(__name__)

if settings.USE_CACHING:

    try:
        if settings.CACHE_BACKEND.strip() == 'redis':
            from .redis import RedisCache as CacheClass
        elif settings.CACHE_BACKEND.strip() == 'memcache':
            from .memcache import MemCache as CacheClass
    except ImportError as e:
        logger.warn(f'Cache import raised: {e}')
        logger.warn('Could not import your caching backend. Is it installed?')
        from . mock import MockCache as CacheClass
else:
    from .mock import MockCache as CacheClass

cache = CacheClass(host=settings.CACHE_HOST, port=settings.CACHE_PORT)
