"""
Base Cache Layer Interface.

This module defines the base interface for cache layers,
providing the foundation for L1, L2, and L3 cache implementations.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class CacheLayer(Enum):
    """Cache layers available"""

    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""

    key: str
    value: Any
    created_at: float
    ttl: int
    access_count: int = 0
    last_accessed: float = 0.0
    compressed: bool = False
    size_bytes: int = 0
    tags: set = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = set()
        if self.last_accessed == 0.0:
            self.last_accessed = time.time()

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl <= 0:
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self) -> None:
        """Update access time and count"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheStatistics:
    """Cache performance statistics"""

    layer: CacheLayer
    hit_count: int
    miss_count: int
    eviction_count: int
    prefetch_count: int
    total_size_bytes: int
    entry_count: int
    average_access_time_ms: float
    hit_ratio: float
    memory_efficiency: float
    last_updated: datetime

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["layer"] = self.layer.value
        data["last_updated"] = self.last_updated.isoformat()
        return data

    def update_hit_ratio(self) -> None:
        """Update hit ratio based on hits and misses"""
        total = self.hit_count + self.miss_count
        self.hit_ratio = (self.hit_count / total * 100) if total > 0 else 0.0

    def update_memory_efficiency(self, max_size_bytes: int) -> None:
        """Update memory efficiency"""
        if max_size_bytes > 0:
            self.memory_efficiency = self.total_size_bytes / max_size_bytes * 100
        else:
            self.memory_efficiency = 0.0


class BaseCacheLayer(ABC):
    """Base class for cache layers"""

    def __init__(self, layer_type: CacheLayer, max_size_mb: int = 100):
        self.layer_type = layer_type
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.statistics = CacheStatistics(
            layer=layer_type,
            hit_count=0,
            miss_count=0,
            eviction_count=0,
            prefetch_count=0,
            total_size_bytes=0,
            entry_count=0,
            average_access_time_ms=0.0,
            hit_ratio=0.0,
            memory_efficiency=0.0,
            last_updated=datetime.utcnow(),
        )

    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from cache"""
        pass

    @abstractmethod
    async def set(self, entry: CacheEntry) -> bool:
        """Set entry in cache"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache"""
        pass

    @abstractmethod
    async def size(self) -> int:
        """Get cache size in bytes"""
        pass

    @abstractmethod
    async def keys(self) -> list:
        """Get all cache keys"""
        pass

    async def get_statistics(self) -> CacheStatistics:
        """Get cache statistics"""
        self.statistics.last_updated = datetime.utcnow()
        self.statistics.update_hit_ratio()
        self.statistics.update_memory_efficiency(self.max_size_bytes)
        return self.statistics

    def _record_hit(self, access_time_ms: float = 0.0) -> None:
        """Record cache hit"""
        self.statistics.hit_count += 1
        if access_time_ms > 0:
            # Update running average
            total_accesses = self.statistics.hit_count + self.statistics.miss_count
            current_avg = self.statistics.average_access_time_ms
            self.statistics.average_access_time_ms = (
                current_avg * (total_accesses - 1) + access_time_ms
            ) / total_accesses

    def _record_miss(self, access_time_ms: float = 0.0) -> None:
        """Record cache miss"""
        self.statistics.miss_count += 1
        if access_time_ms > 0:
            # Update running average
            total_accesses = self.statistics.hit_count + self.statistics.miss_count
            current_avg = self.statistics.average_access_time_ms
            self.statistics.average_access_time_ms = (
                current_avg * (total_accesses - 1) + access_time_ms
            ) / total_accesses

    def _record_eviction(self) -> None:
        """Record cache eviction"""
        self.statistics.eviction_count += 1

    def _record_prefetch(self) -> None:
        """Record cache prefetch"""
        self.statistics.prefetch_count += 1

    def _update_size_stats(self, size_delta: int, entry_delta: int) -> None:
        """Update size statistics"""
        self.statistics.total_size_bytes += size_delta
        self.statistics.entry_count += entry_delta

        # Ensure non-negative values
        self.statistics.total_size_bytes = max(0, self.statistics.total_size_bytes)
        self.statistics.entry_count = max(0, self.statistics.entry_count)
