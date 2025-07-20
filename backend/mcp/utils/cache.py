"""
Cache utilities for MCP Gateway
"""

import json
import asyncio
from typing import Any, Optional
from datetime import datetime, timedelta
from core.cache_manager import CacheManager as CoreCacheManager


class CacheManager:
    """
    Cache manager for MCP Gateway responses
    Wraps the core cache manager with MCP-specific functionality
    """
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache manager
        
        Args:
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.ttl = ttl
        self.core_cache = CoreCacheManager()
        self._cache_prefix = "mcp:"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        prefixed_key = f"{self._cache_prefix}{key}"
        cached_data = await self.core_cache.get(prefixed_key)
        
        if cached_data:
            try:
                data = json.loads(cached_data) if isinstance(cached_data, str) else cached_data
                # Check if expired
                if "expires_at" in data:
                    expires_at = datetime.fromisoformat(data["expires_at"])
                    if datetime.utcnow() > expires_at:
                        await self.delete(key)
                        return None
                return data.get("value")
            except (json.JSONDecodeError, KeyError):
                return cached_data
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Override default TTL in seconds
            
        Returns:
            bool: Success status
        """
        prefixed_key = f"{self._cache_prefix}{key}"
        cache_ttl = ttl or self.ttl
        
        cache_data = {
            "value": value,
            "expires_at": (datetime.utcnow() + timedelta(seconds=cache_ttl)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self.core_cache.set(
            prefixed_key,
            json.dumps(cache_data, default=str),
            ttl=cache_ttl
        )
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            bool: Success status
        """
        prefixed_key = f"{self._cache_prefix}{key}"
        return await self.core_cache.delete(prefixed_key)
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern
        
        Args:
            pattern: Pattern to match (e.g., "tool:nexus_core:*")
            
        Returns:
            int: Number of keys deleted
        """
        # This would need Redis SCAN implementation
        # For now, return 0
        return 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            dict: Cache statistics
        """
        # Get stats from core cache if available
        return {
            "type": "mcp_cache",
            "ttl": self.ttl,
            "prefix": self._cache_prefix
        }