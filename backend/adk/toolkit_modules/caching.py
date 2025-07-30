"""
Caching Utilities for ADK
=========================

Provides decorators and utilities for caching agent results.
"""

from typing import Any, Callable, Optional, Union
from functools import wraps
import hashlib
import json
import pickle
from datetime import datetime, timedelta

from core.redis_pool import RedisPoolManager
from core.logging_config import get_logger
from ..core.exceptions import CacheError

logger = get_logger(__name__)


class CacheManager:
    """Manages caching operations for agents."""
    
    def __init__(self, prefix: str = "adk", redis_client: Optional[Any] = None):
        self.prefix = prefix
        self.redis_client = redis_client or RedisPoolManager().get_connection()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        # Create a string representation of all arguments
        key_parts = []
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))
        
        # Add keyword arguments
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (dict, list)):
                key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
            else:
                key_parts.append(f"{k}:{v}")
        
        # Create hash of the key parts
        key_string = "|".join(key_parts)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        
        return f"{self.prefix}:cache:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {str(e)}")
            raise CacheError(f"Failed to get from cache: {str(e)}", operation="get")
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            serialized = pickle.dumps(value)
            if ttl:
                await self.redis_client.setex(key, ttl, serialized)
            else:
                await self.redis_client.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {str(e)}")
            raise CacheError(f"Failed to set in cache: {str(e)}", operation="set")
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            result = await self.redis_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache delete error: {str(e)}")
            raise CacheError(f"Failed to delete from cache: {str(e)}", operation="delete")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists error: {str(e)}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=f"{self.prefix}:{pattern}"):
                keys.append(key)
            
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern error: {str(e)}")
            raise CacheError(f"Failed to clear cache pattern: {str(e)}", operation="clear_pattern")


def cache_result(
    ttl: Union[int, timedelta] = 3600,
    key_prefix: Optional[str] = None,
    cache_errors: bool = False,
    cache_none: bool = False
):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds or timedelta
        key_prefix: Optional prefix for cache keys
        cache_errors: Whether to cache exceptions
        cache_none: Whether to cache None results
    
    Example:
        @cache_result(ttl=3600)
        async def expensive_operation(param1, param2):
            # Expensive computation
            return result
    """
    if isinstance(ttl, timedelta):
        ttl = int(ttl.total_seconds())
    
    def decorator(func: Callable) -> Callable:
        cache_manager = CacheManager(prefix=key_prefix or func.__name__)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if explicitly disabled
            if kwargs.pop('_skip_cache', False):
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_manager._generate_key(*args, **kwargs)
            
            # Try to get from cache
            try:
                cached_value = await cache_manager.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    
                    # Check if it's a cached exception
                    if isinstance(cached_value, dict) and cached_value.get('_is_exception'):
                        raise cached_value['exception']
                    
                    return cached_value
            except CacheError:
                # If cache fails, continue with function execution
                pass
            
            # Execute function
            try:
                result = await func(*args, **kwargs)
                
                # Cache the result if appropriate
                if result is not None or cache_none:
                    try:
                        await cache_manager.set(cache_key, result, ttl)
                        logger.debug(f"Cached result for {func.__name__}: {cache_key}")
                    except CacheError:
                        # If caching fails, still return the result
                        pass
                
                return result
                
            except Exception as e:
                # Cache the exception if configured
                if cache_errors:
                    try:
                        await cache_manager.set(
                            cache_key,
                            {'_is_exception': True, 'exception': e},
                            ttl
                        )
                    except CacheError:
                        pass
                raise
        
        # Add method to invalidate cache for this function
        wrapper.invalidate_cache = lambda *args, **kwargs: invalidate_cache(
            cache_manager,
            *args,
            **kwargs
        )
        
        return wrapper
    
    return decorator


async def invalidate_cache(
    cache_manager: CacheManager,
    *args,
    **kwargs
) -> bool:
    """Invalidate cache for specific arguments."""
    cache_key = cache_manager._generate_key(*args, **kwargs)
    return await cache_manager.delete(cache_key)


class ConversationCache:
    """Specialized cache for conversation context."""
    
    def __init__(self, ttl: int = 3600):
        self.cache_manager = CacheManager(prefix="conversation")
        self.ttl = ttl
    
    async def get_context(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[dict]:
        """Get conversation context from cache."""
        key = f"{user_id}:{session_id}"
        return await self.cache_manager.get(key)
    
    async def set_context(
        self,
        user_id: str,
        session_id: str,
        context: dict
    ) -> bool:
        """Set conversation context in cache."""
        key = f"{user_id}:{session_id}"
        return await self.cache_manager.set(key, context, self.ttl)
    
    async def append_message(
        self,
        user_id: str,
        session_id: str,
        message: dict
    ) -> bool:
        """Append a message to the conversation context."""
        context = await self.get_context(user_id, session_id) or {
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        context["messages"].append(message)
        context["updated_at"] = datetime.utcnow().isoformat()
        
        # Limit message history
        if len(context["messages"]) > 50:
            context["messages"] = context["messages"][-50:]
        
        return await self.set_context(user_id, session_id, context)
    
    async def clear_context(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> int:
        """Clear conversation context."""
        if session_id:
            key = f"{user_id}:{session_id}"
            return await self.cache_manager.delete(key)
        else:
            # Clear all sessions for user
            pattern = f"conversation:{user_id}:*"
            return await self.cache_manager.clear_pattern(pattern)