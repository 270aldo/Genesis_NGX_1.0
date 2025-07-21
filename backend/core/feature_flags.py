"""
Feature Flags System for GENESIS
================================

A robust feature flag system for controlling feature rollout,
A/B testing, and graceful degradation.
"""

from typing import Dict, Any, Optional, List, Union, Callable
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, validator
from redis import Redis
import asyncio

from core.logging_config import get_logger
from core.redis_pool import RedisPoolManager
from clients.supabase_client import supabase_client

logger = get_logger(__name__)


class FlagType(str, Enum):
    """Types of feature flags."""
    BOOLEAN = "boolean"          # Simple on/off
    PERCENTAGE = "percentage"     # Gradual rollout
    USER_LIST = "user_list"      # Specific users
    USER_SEGMENT = "user_segment" # User segments
    VARIANT = "variant"          # A/B testing
    SCHEDULE = "schedule"        # Time-based
    OPERATIONAL = "operational"   # System operations


class FlagStatus(str, Enum):
    """Feature flag status."""
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


@dataclass
class FlagRule:
    """Rule for evaluating feature flags."""
    
    type: str
    value: Any
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if rule applies to given context."""
        if self.type == "percentage":
            # Use consistent hashing for user
            user_id = context.get("user_id", "anonymous")
            flag_name = context.get("flag_name", "")
            hash_input = f"{flag_name}:{user_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            return (hash_value % 100) < self.value
            
        elif self.type == "user_list":
            user_id = context.get("user_id")
            return user_id in self.value
            
        elif self.type == "user_segment":
            # Check user segment
            user_segment = context.get("user_segment", "default")
            return user_segment in self.value
            
        elif self.type == "schedule":
            # Check if current time is within schedule
            now = datetime.utcnow()
            start = datetime.fromisoformat(self.value.get("start"))
            end = datetime.fromisoformat(self.value.get("end"))
            return start <= now <= end
            
        return False


class FeatureFlag(BaseModel):
    """Feature flag configuration."""
    
    name: str = Field(..., description="Unique flag name")
    description: str = Field(..., description="Flag description")
    type: FlagType = Field(default=FlagType.BOOLEAN)
    status: FlagStatus = Field(default=FlagStatus.ACTIVE)
    default_value: Any = Field(default=False)
    rules: List[FlagRule] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Targeting
    target_percentage: Optional[int] = Field(None, ge=0, le=100)
    target_users: List[str] = Field(default_factory=list)
    target_segments: List[str] = Field(default_factory=list)
    
    # Variants for A/B testing
    variants: Dict[str, Any] = Field(default_factory=dict)
    
    # Schedule
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Validate flag name format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Flag name must be alphanumeric with _ or -")
        return v.lower()
    
    def evaluate(self, context: Dict[str, Any]) -> Any:
        """Evaluate flag value for given context."""
        # Check if flag is active
        if self.status != FlagStatus.ACTIVE:
            return self.default_value
        
        # Check schedule
        if self.start_date and datetime.utcnow() < self.start_date:
            return self.default_value
        if self.end_date and datetime.utcnow() > self.end_date:
            return self.default_value
        
        # Add flag name to context
        context["flag_name"] = self.name
        
        # Evaluate rules in order
        for rule in self.rules:
            if rule.evaluate(context):
                return rule.value
        
        # Check targeting
        if self.type == FlagType.PERCENTAGE and self.target_percentage is not None:
            rule = FlagRule(type="percentage", value=self.target_percentage)
            if rule.evaluate(context):
                return True
        
        if self.type == FlagType.USER_LIST and self.target_users:
            user_id = context.get("user_id")
            if user_id in self.target_users:
                return True
        
        if self.type == FlagType.VARIANT and self.variants:
            # Determine variant based on user
            user_id = context.get("user_id", "anonymous")
            hash_value = int(hashlib.md5(f"{self.name}:{user_id}".encode()).hexdigest(), 16)
            variant_index = hash_value % len(self.variants)
            variant_names = list(self.variants.keys())
            return variant_names[variant_index]
        
        return self.default_value


class FlagProvider(ABC):
    """Abstract base for feature flag providers."""
    
    @abstractmethod
    async def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get a feature flag by name."""
        pass
    
    @abstractmethod
    async def get_all_flags(self) -> List[FeatureFlag]:
        """Get all feature flags."""
        pass
    
    @abstractmethod
    async def save_flag(self, flag: FeatureFlag) -> bool:
        """Save or update a feature flag."""
        pass
    
    @abstractmethod
    async def delete_flag(self, name: str) -> bool:
        """Delete a feature flag."""
        pass


class SupabaseFlagProvider(FlagProvider):
    """Feature flag provider using Supabase."""
    
    def __init__(self, table_name: str = "feature_flags"):
        self.table_name = table_name
        self.client = supabase_client
    
    async def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get flag from Supabase."""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("name", name)\
                .single()\
                .execute()
            
            if response.data:
                return FeatureFlag(**response.data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting flag {name}: {e}")
            return None
    
    async def get_all_flags(self) -> List[FeatureFlag]:
        """Get all flags from Supabase."""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("status", FlagStatus.ACTIVE.value)\
                .execute()
            
            return [FeatureFlag(**data) for data in response.data]
            
        except Exception as e:
            logger.error(f"Error getting all flags: {e}")
            return []
    
    async def save_flag(self, flag: FeatureFlag) -> bool:
        """Save flag to Supabase."""
        try:
            flag.updated_at = datetime.utcnow()
            data = flag.dict()
            
            # Convert datetime to ISO format
            for key in ['created_at', 'updated_at', 'start_date', 'end_date']:
                if data.get(key):
                    data[key] = data[key].isoformat()
            
            # Upsert flag
            response = self.client.table(self.table_name)\
                .upsert(data)\
                .execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error saving flag {flag.name}: {e}")
            return False
    
    async def delete_flag(self, name: str) -> bool:
        """Delete flag from Supabase."""
        try:
            # Soft delete - just change status
            response = self.client.table(self.table_name)\
                .update({"status": FlagStatus.ARCHIVED.value})\
                .eq("name", name)\
                .execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error deleting flag {name}: {e}")
            return False


class RedisFlagCache:
    """Redis cache for feature flags."""
    
    def __init__(self, redis_client: Redis, ttl: int = 300):
        self.redis = redis_client
        self.ttl = ttl  # 5 minutes default
        self.prefix = "feature_flags:"
    
    async def get(self, name: str) -> Optional[FeatureFlag]:
        """Get flag from cache."""
        try:
            key = f"{self.prefix}{name}"
            data = await self.redis.get(key)
            if data:
                return FeatureFlag(**json.loads(data))
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def set(self, flag: FeatureFlag):
        """Set flag in cache."""
        try:
            key = f"{self.prefix}{flag.name}"
            data = flag.json()
            await self.redis.setex(key, self.ttl, data)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    async def invalidate(self, name: str):
        """Invalidate cached flag."""
        try:
            key = f"{self.prefix}{name}"
            await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache invalidate error: {e}")
    
    async def invalidate_all(self):
        """Invalidate all cached flags."""
        try:
            pattern = f"{self.prefix}*"
            async for key in self.redis.scan_iter(match=pattern):
                await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache invalidate all error: {e}")


class FeatureFlagManager:
    """Main feature flag manager."""
    
    def __init__(
        self,
        provider: Optional[FlagProvider] = None,
        cache_ttl: int = 300,
        enable_cache: bool = True
    ):
        self.provider = provider or SupabaseFlagProvider()
        self.enable_cache = enable_cache
        
        if enable_cache:
            redis_manager = RedisPoolManager()
            self.cache = RedisFlagCache(
                redis_manager.get_connection(),
                ttl=cache_ttl
            )
        else:
            self.cache = None
        
        # Local memory cache for critical flags
        self._memory_cache: Dict[str, FeatureFlag] = {}
        self._memory_cache_ttl: Dict[str, datetime] = {}
    
    async def is_enabled(
        self,
        flag_name: str,
        context: Optional[Dict[str, Any]] = None,
        default: bool = False
    ) -> bool:
        """Check if a feature flag is enabled."""
        flag = await self.get_flag(flag_name)
        if not flag:
            return default
        
        context = context or {}
        result = flag.evaluate(context)
        
        # Log flag evaluation
        logger.debug(
            f"Feature flag '{flag_name}' evaluated to {result}",
            extra={
                "flag_name": flag_name,
                "context": context,
                "result": result
            }
        )
        
        return bool(result)
    
    async def get_variant(
        self,
        flag_name: str,
        context: Optional[Dict[str, Any]] = None,
        default: str = "control"
    ) -> str:
        """Get variant for A/B testing."""
        flag = await self.get_flag(flag_name)
        if not flag or flag.type != FlagType.VARIANT:
            return default
        
        context = context or {}
        result = flag.evaluate(context)
        
        return str(result) if result else default
    
    async def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get a feature flag with caching."""
        # Check memory cache first
        if name in self._memory_cache:
            ttl = self._memory_cache_ttl.get(name)
            if ttl and datetime.utcnow() < ttl:
                return self._memory_cache[name]
        
        # Check Redis cache
        if self.cache:
            flag = await self.cache.get(name)
            if flag:
                return flag
        
        # Get from provider
        flag = await self.provider.get_flag(name)
        
        # Cache if found
        if flag and self.cache:
            await self.cache.set(flag)
        
        return flag
    
    async def get_all_flags(self) -> List[FeatureFlag]:
        """Get all active feature flags."""
        return await self.provider.get_all_flags()
    
    async def create_flag(self, flag: FeatureFlag) -> bool:
        """Create a new feature flag."""
        success = await self.provider.save_flag(flag)
        
        if success and self.cache:
            await self.cache.invalidate(flag.name)
        
        return success
    
    async def update_flag(self, flag: FeatureFlag) -> bool:
        """Update an existing feature flag."""
        success = await self.provider.save_flag(flag)
        
        if success:
            # Invalidate caches
            if self.cache:
                await self.cache.invalidate(flag.name)
            
            # Remove from memory cache
            self._memory_cache.pop(flag.name, None)
            self._memory_cache_ttl.pop(flag.name, None)
        
        return success
    
    async def delete_flag(self, name: str) -> bool:
        """Delete a feature flag."""
        success = await self.provider.delete_flag(name)
        
        if success:
            if self.cache:
                await self.cache.invalidate(name)
            
            self._memory_cache.pop(name, None)
            self._memory_cache_ttl.pop(name, None)
        
        return success
    
    def cache_in_memory(self, flag: FeatureFlag, ttl_seconds: int = 60):
        """Cache flag in local memory for critical paths."""
        self._memory_cache[flag.name] = flag
        self._memory_cache_ttl[flag.name] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    async def refresh_cache(self):
        """Refresh all cached flags."""
        if self.cache:
            await self.cache.invalidate_all()
        
        self._memory_cache.clear()
        self._memory_cache_ttl.clear()
        
        # Pre-cache all active flags
        flags = await self.get_all_flags()
        for flag in flags:
            if self.cache:
                await self.cache.set(flag)


# Global feature flag manager instance
_feature_flag_manager: Optional[FeatureFlagManager] = None
_init_lock = asyncio.Lock()


async def get_feature_flags() -> FeatureFlagManager:
    """Get or create feature flag manager singleton."""
    global _feature_flag_manager
    
    async with _init_lock:
        if _feature_flag_manager is None:
            _feature_flag_manager = FeatureFlagManager()
            logger.info("Feature flag manager initialized")
    
    return _feature_flag_manager


# Convenience decorators
def feature_flag(
    flag_name: str,
    default: bool = False,
    context_func: Optional[Callable] = None
):
    """
    Decorator to control function execution with feature flag.
    
    Args:
        flag_name: Name of the feature flag
        default: Default value if flag not found
        context_func: Function to get context (receives same args as decorated function)
    
    Example:
        @feature_flag("new_algorithm", default=False)
        async def process_data(user_id: str, data: dict):
            # This only runs if flag is enabled
            return new_algorithm(data)
    """
    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            manager = await get_feature_flags()
            
            # Get context
            context = {}
            if context_func:
                context = context_func(*args, **kwargs)
            
            # Check flag
            if await manager.is_enabled(flag_name, context, default):
                return await func(*args, **kwargs)
            else:
                # Return None or raise based on function signature
                return None
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, use asyncio.run
            import asyncio
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def variant_flag(
    flag_name: str,
    default_variant: str = "control"
):
    """
    Decorator for A/B testing with variants.
    
    Example:
        @variant_flag("checkout_flow")
        async def checkout(variant: str, user_id: str, cart: dict):
            if variant == "new_flow":
                return await new_checkout_flow(cart)
            else:
                return await classic_checkout_flow(cart)
    """
    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            manager = await get_feature_flags()
            
            # Get user context from args/kwargs
            context = {}
            if "user_id" in kwargs:
                context["user_id"] = kwargs["user_id"]
            elif len(args) > 0 and isinstance(args[0], str):
                context["user_id"] = args[0]
            
            # Get variant
            variant = await manager.get_variant(flag_name, context, default_variant)
            
            # Inject variant as first parameter
            return await func(variant, *args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            import asyncio
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator