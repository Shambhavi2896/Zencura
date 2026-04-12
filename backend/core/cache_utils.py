from functools import wraps
from flask import request
from backend.core.cache import cache
import hashlib
import json
from flask_jwt_extended import get_jwt

def get_cache_key(*args, **kwargs):
    jwt_identity = ""
    try:
        jwt_data = get_jwt()
        jwt_identity = str(jwt_data.get("sub", ""))
    except:
        pass
    key_parts = [
        jwt_identity,
        request.path,
        request.query_string.decode("utf-8") if request.query_string else "",
        request.endpoint or "",
    ]
    key_string = "|".join(key_parts)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    return f"api_cache:{key_hash}"

def cached_route(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method != "GET":
                return f(*args, **kwargs)
            cache_key = get_cache_key()
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                data, status_code = response[0], (
                    response[1] if len(response) > 1 else 200
                )
            else:
                data, status_code = response, 200
            if 200 <= status_code < 300:
                cache.set(cache_key, response, timeout=timeout)
            return response
        return decorated_function
    return decorator

def invalidate_cache(*patterns):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            if isinstance(result, tuple):
                status_code = result[1] if len(result) > 1 else 200
            else:
                status_code = 200
            if 200 <= status_code < 300:
                try:
                    for pattern in patterns:
                        try:
                            cache.delete_pattern(pattern)
                        except:
                            cache.clear()
                            break
                except:
                    pass
            return result
        return decorated_function
    return decorator

def cache_with_tag(tag, timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method != "GET":
                return f(*args, **kwargs)
            cache_key = f"{tag}:{get_cache_key()}"
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                status_code = response[1] if len(response) > 1 else 200
            else:
                status_code = 200
            if 200 <= status_code < 300:
                cache.set(cache_key, response, timeout=timeout)
            return response
        return decorated_function
    return decorator

class CacheInvalidator:
    def __init__(self):
        self.tags = {}
    def register(self, tag, *patterns):
        self.tags[tag] = patterns
    def invalidate(self, tag):
        if tag in self.tags:
            for pattern in self.tags[tag]:
                try:
                    cache.delete_pattern(pattern)
                except:
                    cache.clear()
                    break
invalidator = CacheInvalidator()
invalidator.register(
    "doctors", "api_cache:*doctors*", "api_cache:*doctor*", "api_cache:*search*"
)
invalidator.register(
    "patients", "api_cache:*patients*", "api_cache:*patient*", "api_cache:*search*"
)
invalidator.register(
    "appointments", "api_cache:*appointments*", "api_cache:*appointment*"
)
invalidator.register("payments", "api_cache:*payments*", "api_cache:*payment*")
invalidator.register("reports", "api_cache:*reports*", "api_cache:*analytics*")
