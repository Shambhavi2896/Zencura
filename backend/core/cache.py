import logging
from flask_caching import Cache

logger = logging.getLogger(__name__)
cache = Cache()

def init_cache_with_fallback(app):
    try:
        cache.init_app(app, config={
            'CACHE_TYPE': app.config.get('CACHE_TYPE', 'redis'),
            'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL', 'redis://127.0.0.1:6379/0'),
            'CACHE_DEFAULT_TIMEOUT': 300
        })
        cache.get('_test_key')
        logger.info('Redis cache active')
    except Exception as e:
        logger.warning(f'Redis failed, using SimpleCache')
        cache.init_app(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})

