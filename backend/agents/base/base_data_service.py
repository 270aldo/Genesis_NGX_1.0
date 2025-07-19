"""
Base Data Service for NGX Agents
================================

This module provides a base class for all data services in the NGX ecosystem,
eliminating code duplication and providing consistent data handling patterns.

Features:
- Automatic caching with Redis
- Consistent CRUD operations
- Built-in error handling
- Audit logging support
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json

from core.logging_config import get_logger
from core.redis_pool import RedisPoolManager
from clients.supabase_client import SupabaseClient

logger = get_logger(__name__)

T = TypeVar('T')


class BaseDataService(ABC, Generic[T]):
    """
    Base class for all data services in NGX agents.
    
    Provides common functionality for:
    - CRUD operations
    - Caching with Redis
    - Error handling
    - Audit logging
    """
    
    def __init__(
        self,
        table_name: str,
        cache_prefix: str,
        cache_ttl: int = 3600,
        supabase_client: Optional[SupabaseClient] = None,
        redis_manager: Optional[RedisPoolManager] = None
    ):
        """
        Initialize base data service.
        
        Args:
            table_name: Supabase table name
            cache_prefix: Redis cache key prefix
            cache_ttl: Cache time-to-live in seconds
            supabase_client: Optional Supabase client instance
            redis_manager: Optional Redis manager instance
        """
        self.table_name = table_name
        self.cache_prefix = cache_prefix
        self.cache_ttl = cache_ttl
        
        # Initialize clients
        self.supabase = supabase_client or SupabaseClient()
        self.redis = redis_manager or RedisPoolManager.get_instance()
        
        # Cache for in-memory storage (fallback)
        self._memory_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        logger.info(f"Initialized {self.__class__.__name__} for table '{table_name}'")
    
    # ==================== Abstract Methods ====================
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data before saving. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def transform_for_storage(self, data: T) -> Dict[str, Any]:
        """Transform data for storage. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def transform_from_storage(self, data: Dict[str, Any]) -> T:
        """Transform data from storage. Must be implemented by subclasses."""
        pass
    
    # ==================== CRUD Operations ====================
    
    async def save(self, user_id: str, data: T) -> Dict[str, Any]:
        """
        Save data for a user.
        
        Args:
            user_id: User identifier
            data: Data to save
            
        Returns:
            Dict with operation result
        """
        try:
            # Validate data
            storage_data = self.transform_for_storage(data)
            if not self.validate_data(storage_data):
                raise ValueError("Data validation failed")
            
            # Add metadata
            storage_data.update({
                "user_id": user_id,
                "updated_at": datetime.now().isoformat(),
                "version": storage_data.get("version", 1) + 1
            })
            
            # Save to database
            result = await self._save_to_database(user_id, storage_data)
            
            # Update cache
            await self._update_cache(user_id, storage_data)
            
            # Audit log
            await self._audit_operation("save", user_id, result)
            
            logger.info(f"Saved data for user {user_id} in table {self.table_name}")
            return {
                "success": True,
                "data": result,
                "message": f"Data saved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error saving data for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to save data"
            }
    
    async def get(self, user_id: str) -> Optional[T]:
        """
        Get data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Data if found, None otherwise
        """
        try:
            # Check cache first
            cached = await self._get_from_cache(user_id)
            if cached:
                return self.transform_from_storage(cached)
            
            # Get from database
            data = await self._get_from_database(user_id)
            if data:
                # Update cache
                await self._update_cache(user_id, data)
                return self.transform_from_storage(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting data for user {user_id}: {e}")
            return None
    
    async def update(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data for a user.
        
        Args:
            user_id: User identifier
            updates: Fields to update
            
        Returns:
            Dict with operation result
        """
        try:
            # Get existing data
            existing = await self.get(user_id)
            if not existing:
                return {
                    "success": False,
                    "message": "No existing data found"
                }
            
            # Merge updates
            existing_dict = self.transform_for_storage(existing)
            existing_dict.update(updates)
            
            # Save updated data
            return await self.save(user_id, self.transform_from_storage(existing_dict))
            
        except Exception as e:
            logger.error(f"Error updating data for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update data"
            }
    
    async def delete(self, user_id: str) -> Dict[str, Any]:
        """
        Delete data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with operation result
        """
        try:
            # Delete from database
            result = await self._delete_from_database(user_id)
            
            # Remove from cache
            await self._remove_from_cache(user_id)
            
            # Audit log
            await self._audit_operation("delete", user_id, {"deleted": True})
            
            logger.info(f"Deleted data for user {user_id} from table {self.table_name}")
            return {
                "success": True,
                "message": "Data deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting data for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete data"
            }
    
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        List data with optional filters.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of data items
        """
        try:
            data = await self._list_from_database(filters)
            return [self.transform_from_storage(item) for item in data]
            
        except Exception as e:
            logger.error(f"Error listing data: {e}")
            return []
    
    # ==================== Private Methods ====================
    
    async def _save_to_database(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save data to Supabase."""
        if not self.supabase.client:
            raise ValueError("Supabase client not initialized")
        
        # Check if record exists
        existing = self.supabase.client.table(self.table_name).select("*").eq("user_id", user_id).single().execute()
        
        if existing.data:
            # Update existing record
            result = self.supabase.client.table(self.table_name).update(data).eq("user_id", user_id).execute()
        else:
            # Insert new record
            result = self.supabase.client.table(self.table_name).insert(data).execute()
        
        return result.data[0] if result.data else {}
    
    async def _get_from_database(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get data from Supabase."""
        if not self.supabase.client:
            return None
        
        result = self.supabase.client.table(self.table_name).select("*").eq("user_id", user_id).single().execute()
        return result.data if result.data else None
    
    async def _delete_from_database(self, user_id: str) -> bool:
        """Delete data from Supabase."""
        if not self.supabase.client:
            raise ValueError("Supabase client not initialized")
        
        self.supabase.client.table(self.table_name).delete().eq("user_id", user_id).execute()
        return True
    
    async def _list_from_database(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List data from Supabase."""
        if not self.supabase.client:
            return []
        
        query = self.supabase.client.table(self.table_name).select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data if result.data else []
    
    async def _get_from_cache(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get data from cache."""
        cache_key = f"{self.cache_prefix}:{user_id}"
        
        # Try Redis first
        if self.redis and await self.redis.is_connected():
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        # Fallback to memory cache
        if cache_key in self._memory_cache:
            timestamp = self._cache_timestamps.get(cache_key)
            if timestamp and (datetime.now() - timestamp).seconds < self.cache_ttl:
                return self._memory_cache[cache_key]
        
        return None
    
    async def _update_cache(self, user_id: str, data: Dict[str, Any]) -> None:
        """Update cache with data."""
        cache_key = f"{self.cache_prefix}:{user_id}"
        
        # Update Redis
        if self.redis and await self.redis.is_connected():
            try:
                await self.redis.set(
                    cache_key,
                    json.dumps(data),
                    ex=self.cache_ttl
                )
            except Exception as e:
                logger.warning(f"Redis cache update error: {e}")
        
        # Update memory cache
        self._memory_cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()
    
    async def _remove_from_cache(self, user_id: str) -> None:
        """Remove data from cache."""
        cache_key = f"{self.cache_prefix}:{user_id}"
        
        # Remove from Redis
        if self.redis and await self.redis.is_connected():
            try:
                await self.redis.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis cache delete error: {e}")
        
        # Remove from memory cache
        self._memory_cache.pop(cache_key, None)
        self._cache_timestamps.pop(cache_key, None)
    
    async def _audit_operation(self, operation: str, user_id: str, details: Dict[str, Any]) -> None:
        """Log operation for audit purposes."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": self.__class__.__name__,
            "table": self.table_name,
            "operation": operation,
            "user_id": user_id,
            "details": details
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")