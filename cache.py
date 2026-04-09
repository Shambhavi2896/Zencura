from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://127.0.0.1:6379/1',
    'CACHE_DEFAULT_TIMEOUT': 300
})
