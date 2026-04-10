"""Caching utilities and decorators for API optimization."""

from functools import wraps
from flask import request
from backend.core.cache import cache
import hashlib
import json
from flask_jwt_extended import get_jwt


def get_cache_key(*args, **kwargs):
    """Generate a cache key from function arguments and request parameters."""
    # Include JWT identity in cache key to prevent cross-user cache hits
    jwt_identity = ""
    try:
        jwt_data = get_jwt()
        jwt_identity = str(jwt_data.get('sub', ''))
    except:
        pass
    
    # Build cache key from args, kwargs, and query parameters
    key_parts = [
        jwt_identity,
        request.path,
        request.query_string.decode('utf-8') if request.query_string else '',
        request.endpoint or '',
    ]
    
    # Create deterministic hash
    key_string = '|'.join(key_parts)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    return f"api_cache:{key_hash}"


def cached_route(timeout=300):
    """Decorator to cache API responses with configurable timeout.
    
    Args:
        timeout: Cache timeout in seconds (default 300s = 5 minutes)
    
    Usage:
        @app.route('/api/doctors')
        @jwt_required()
        @cached_route(timeout=600)
        def get_doctors():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip caching for non-GET requests
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            # Generate cache key
            cache_key = get_cache_key()
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Call the actual endpoint
            response = f(*args, **kwargs)
            
            # Cache the response if it's a success (2xx)
            if isinstance(response, tuple):
                data, status_code = response[0], response[1] if len(response) > 1 else 200
            else:
                data, status_code = response, 200
            
            if 200 <= status_code < 300:
                cache.set(cache_key, response, timeout=timeout)
            
            return response
        
        return decorated_function
    return decorator


def invalidate_cache(*patterns):
    """Decorator to invalidate cache patterns after a function completes.
    
    Usage:
        @app.route('/api/doctors', methods=['POST'])
        @jwt_required()
        @invalidate_cache('api_cache:*doctor*', 'api_cache:*search*')
        def create_doctor():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # Invalidate cache patterns after successful operation
            if isinstance(result, tuple):
                status_code = result[1] if len(result) > 1 else 200
            else:
                status_code = 200
            
            if 200 <= status_code < 300:
                # Try to clear cache for the patterns
                try:
                    # Redis wildcard clear (works with Redis backend)
                    for pattern in patterns:
                        try:
                            cache.delete_pattern(pattern)
                        except:
                            # Fallback: just clear cache
                            cache.clear()
                            break
                except:
                    pass  # Cache backend may not support pattern deletion
            
            return result
        
        return decorated_function
    return decorator


def cache_with_tag(tag, timeout=300):
    """Decorator to cache responses with a logical tag for grouped invalidation.
    
    Usage:
        @app.route('/api/doctor/<id>')
        @jwt_required()
        @cache_with_tag('doctors', timeout=600)
        def get_doctor(id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            cache_key = f"{tag}:{get_cache_key()}"
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Call the function
            response = f(*args, **kwargs)
            
            # Cache if successful
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
    """Helper class for managing cache invalidation by tags."""
    
    def __init__(self):
        self.tags = {}
    
    def register(self, tag, *patterns):
        """Register patterns for a tag."""
        self.tags[tag] = patterns
    
    def invalidate(self, tag):
        """Invalidate all patterns for a tag."""
        if tag in self.tags:
            for pattern in self.tags[tag]:
                try:
                    cache.delete_pattern(pattern)
                except:
                    cache.clear()
                    break


# Create a global cache invalidator instance
invalidator = CacheInvalidator()

# Pre-register common cache tags
invalidator.register('doctors', 'api_cache:*doctors*', 'api_cache:*doctor*', 'api_cache:*search*')
invalidator.register('patients', 'api_cache:*patients*', 'api_cache:*patient*', 'api_cache:*search*')
invalidator.register('appointments', 'api_cache:*appointments*', 'api_cache:*appointment*')
invalidator.register('payments', 'api_cache:*payments*', 'api_cache:*payment*')
invalidator.register('reports', 'api_cache:*reports*', 'api_cache:*analytics*')
