"""
Cache utilities for faster data loading using Redis.
"""
from functools import wraps
import hashlib
import json
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def sanitize_cache_key(key_component):
    """
    Sanitize a cache key component by replacing problematic characters.
    
    Memcached and some other cache backends have issues with spaces and certain
    special characters in keys. This function replaces them with safe alternatives.
    
    Args:
        key_component: The string component to sanitize (e.g., team name)
    
    Returns:
        Sanitized string safe for use in cache keys
    """
    if not isinstance(key_component, str):
        key_component = str(key_component)
    
    # Replace spaces and other problematic characters with underscores
    # Characters that can cause issues: spaces, colons (outside of key separators), etc.
    # Also handle None, empty strings, and strip whitespace
    if not key_component:
        return 'empty'
    
    # Strip leading/trailing whitespace
    key_component = key_component.strip()
    
    # Replace problematic characters with underscores
    # Note: We preserve colons that are part of Django's cache key structure
    # but replace spaces and other special characters
    sanitized = key_component.replace(' ', '_')
    sanitized = sanitized.replace('/', '_')
    sanitized = sanitized.replace('\\', '_')
    sanitized = sanitized.replace('\t', '_')
    sanitized = sanitized.replace('\n', '_')
    sanitized = sanitized.replace('\r', '_')
    
    # Remove any remaining problematic characters (but keep alphanumeric, underscore, dash, dot)
    import re
    sanitized = re.sub(r'[^\w\-\.]', '_', sanitized)
    
    # Collapse multiple underscores into one
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure we have something to return
    if not sanitized:
        return 'empty'
    
    return sanitized

def make_cache_key(*components, separator='_'):
    """
    Create a safe cache key from multiple components, sanitizing each one.
    
    Args:
        *components: Variable number of key components to join
        separator: Separator to use between components (default: '_')
    
    Returns:
        Sanitized cache key string
    """
    sanitized_components = [sanitize_cache_key(str(comp)) for comp in components if comp is not None]
    return separator.join(sanitized_components)

def cache_result(timeout=300, key_prefix=''):
    """
    Decorator to cache function results in Redis.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [func.__name__, key_prefix]
            
            # Add args to cache key (skip self if it's a method)
            if args:
                # Convert args to strings, skip first if it looks like 'self'
                args_str = [str(arg) if not hasattr(arg, '__dict__') else str(type(arg)) for arg in args[1:]]
                cache_key_parts.extend(args_str)
            
            # Add kwargs to cache key
            if kwargs:
                kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
                cache_key_parts.append(kwargs_str)
            
            # Create cache key
            cache_key = ':'.join(str(part) for part in cache_key_parts)
            # Hash long keys to keep them reasonable
            if len(cache_key) > 200:
                cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try to get from cache
            try:
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache HIT for {func.__name__}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache GET error for {func.__name__}: {e}")
            
            # Cache miss - execute function
            logger.debug(f"Cache MISS for {func.__name__}")
            result = func(*args, **kwargs)
            
            # Store in cache
            try:
                # Only cache if result is not None and not empty
                if result is not None:
                    # For DataFrames, check if they're not empty
                    if hasattr(result, 'empty'):
                        if not result.empty:
                            cache.set(cache_key, result, timeout)
                    else:
                        cache.set(cache_key, result, timeout)
            except Exception as e:
                logger.warning(f"Cache SET error for {func.__name__}: {e}")
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern):
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Pattern to match cache keys (e.g., 'load_football_data:*')
    """
    try:
        # Get all keys matching pattern
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        
        # Note: This requires Redis to support pattern matching
        # For production, consider using a more specific approach
        keys = redis_client.keys(f"football_predictor:{pattern}")
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache entries matching {pattern}")
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")

