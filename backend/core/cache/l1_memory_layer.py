"""
L1 Memory Cache Layer.

This module implements the fastest cache layer using in-memory storage
with intelligent eviction algorithms and compression.
"""

import asyncio
import pickle
import sys
import time
import zlib
from collections import OrderedDict
from typing import Dict, List, Optional, Set

from core.logging_config import get_logger

from .base_layer import BaseCacheLayer, CacheEntry, CacheLayer

logger = get_logger(__name__)


class EvictionPolicy:
    """Eviction policies for L1 cache"""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    HYBRID = "hybrid"  # Intelligent hybrid policy


class L1MemoryLayer(BaseCacheLayer):
    """
    L1 Memory Cache Layer - Ultra-fast in-memory caching.

    Features:
    - Multiple eviction policies (LRU, LFU, FIFO, HYBRID)
    - Automatic compression for large values
    - Memory usage tracking and optimization
    - Access pattern analysis
    """

    def __init__(
        self,
        max_size_mb: int = 100,
        eviction_policy: str = EvictionPolicy.HYBRID,
        compression_threshold: int = 1024,
        compression_level: int = 6,
    ):
        """
        Initialize L1 memory cache layer.

        Args:
            max_size_mb: Maximum cache size in MB
            eviction_policy: Eviction policy to use
            compression_threshold: Size threshold for compression (bytes)
            compression_level: Compression level (1-9)
        """
        super().__init__(CacheLayer.L1_MEMORY, max_size_mb)

        self.eviction_policy = eviction_policy
        self.compression_threshold = compression_threshold
        self.compression_level = compression_level

        # Storage structures
        self._storage: Dict[str, CacheEntry] = {}
        self._access_order: OrderedDict = OrderedDict()  # For LRU
        self._frequency: Dict[str, int] = {}  # For LFU
        self._insertion_order: OrderedDict = OrderedDict()  # For FIFO

        # Performance tracking
        self._access_patterns: Dict[str, List[float]] = {}
        self._hot_keys: Set[str] = set()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from L1 cache."""
        start_time = time.time()

        async with self._lock:
            if key not in self._storage:
                self._record_miss((time.time() - start_time) * 1000)
                return None

            entry = self._storage[key]

            # Check if expired
            if entry.is_expired():
                await self._remove_key(key)
                self._record_miss((time.time() - start_time) * 1000)
                return None

            # Update access patterns
            entry.touch()
            self._update_access_patterns(key)

            # Update tracking structures
            self._access_order.move_to_end(key)
            self._frequency[key] = self._frequency.get(key, 0) + 1

            # Decompress if needed
            if entry.compressed:
                try:
                    entry.value = pickle.loads(zlib.decompress(entry.value))
                    entry.compressed = False
                except Exception as e:
                    logger.warning(f"Failed to decompress cache entry {key}: {e}")
                    await self._remove_key(key)
                    self._record_miss((time.time() - start_time) * 1000)
                    return None

            self._record_hit((time.time() - start_time) * 1000)
            return entry

    async def set(self, entry: CacheEntry) -> bool:
        """Set entry in L1 cache."""
        async with self._lock:
            # Calculate size
            if not entry.size_bytes:
                entry.size_bytes = self._calculate_size(entry.value)

            # Compress large values
            if entry.size_bytes > self.compression_threshold and not entry.compressed:
                try:
                    compressed_value = zlib.compress(
                        pickle.dumps(entry.value), self.compression_level
                    )
                    if len(compressed_value) < entry.size_bytes:
                        entry.value = compressed_value
                        entry.compressed = True
                        entry.size_bytes = len(compressed_value)
                except Exception as e:
                    logger.warning(f"Failed to compress cache entry {entry.key}: {e}")

            # Check if we need to evict
            while (
                self.statistics.total_size_bytes + entry.size_bytes
                > self.max_size_bytes
                and len(self._storage) > 0
            ):
                if not await self._evict_one():
                    logger.warning("Failed to evict entry for new cache entry")
                    return False

            # Remove existing entry if present
            if entry.key in self._storage:
                await self._remove_key(entry.key)

            # Add new entry
            self._storage[entry.key] = entry
            self._access_order[entry.key] = True
            self._insertion_order[entry.key] = True
            self._frequency[entry.key] = 1

            # Update statistics
            self._update_size_stats(entry.size_bytes, 1)

            return True

    async def delete(self, key: str) -> bool:
        """Delete entry from L1 cache."""
        async with self._lock:
            if key not in self._storage:
                return False

            await self._remove_key(key)
            return True

    async def clear(self) -> None:
        """Clear all L1 cache."""
        async with self._lock:
            self._storage.clear()
            self._access_order.clear()
            self._frequency.clear()
            self._insertion_order.clear()
            self._access_patterns.clear()
            self._hot_keys.clear()

            # Reset statistics
            self.statistics.total_size_bytes = 0
            self.statistics.entry_count = 0

    async def size(self) -> int:
        """Get cache size in bytes."""
        return self.statistics.total_size_bytes

    async def keys(self) -> List[str]:
        """Get all cache keys."""
        return list(self._storage.keys())

    async def _evict_one(self) -> bool:
        """Evict one entry based on eviction policy."""
        if not self._storage:
            return False

        key_to_evict = None

        if self.eviction_policy == EvictionPolicy.LRU:
            # Least Recently Used
            key_to_evict = next(iter(self._access_order))

        elif self.eviction_policy == EvictionPolicy.LFU:
            # Least Frequently Used
            min_freq = min(self._frequency.values())
            for key, freq in self._frequency.items():
                if freq == min_freq and key in self._storage:
                    key_to_evict = key
                    break

        elif self.eviction_policy == EvictionPolicy.FIFO:
            # First In First Out
            key_to_evict = next(iter(self._insertion_order))

        elif self.eviction_policy == EvictionPolicy.HYBRID:
            # Intelligent hybrid policy
            key_to_evict = await self._hybrid_eviction_selection()

        if key_to_evict:
            await self._remove_key(key_to_evict)
            self._record_eviction()
            return True

        return False

    async def _hybrid_eviction_selection(self) -> Optional[str]:
        """Select key for eviction using hybrid policy."""
        if not self._storage:
            return None

        # Score each key based on multiple factors
        scores = {}
        current_time = time.time()

        for key, entry in self._storage.items():
            # Time since last access (higher = worse)
            time_factor = current_time - entry.last_accessed

            # Access frequency (lower = worse)
            freq_factor = 1.0 / max(self._frequency.get(key, 1), 1)

            # Size factor (larger = worse for eviction)
            size_factor = entry.size_bytes / (1024 * 1024)  # Convert to MB

            # Hot key bonus (hot keys are less likely to be evicted)
            hot_bonus = 0.5 if key in self._hot_keys else 1.0

            # Combined score (higher = more likely to evict)
            scores[key] = (
                time_factor * 0.4 + freq_factor * 0.3 + size_factor * 0.2
            ) * hot_bonus

        # Return key with highest eviction score
        return max(scores.keys(), key=lambda k: scores[k])

    async def _remove_key(self, key: str) -> None:
        """Remove key from all tracking structures."""
        if key in self._storage:
            entry = self._storage[key]
            self._update_size_stats(-entry.size_bytes, -1)
            del self._storage[key]

        self._access_order.pop(key, None)
        self._frequency.pop(key, None)
        self._insertion_order.pop(key, None)
        self._access_patterns.pop(key, None)
        self._hot_keys.discard(key)

    def _update_access_patterns(self, key: str) -> None:
        """Update access patterns for intelligent caching."""
        current_time = time.time()

        if key not in self._access_patterns:
            self._access_patterns[key] = []

        self._access_patterns[key].append(current_time)

        # Keep only recent accesses (last hour)
        cutoff_time = current_time - 3600  # 1 hour
        self._access_patterns[key] = [
            t for t in self._access_patterns[key] if t > cutoff_time
        ]

        # Mark as hot key if accessed frequently
        if len(self._access_patterns[key]) > 10:  # More than 10 accesses in last hour
            self._hot_keys.add(key)
        elif len(self._access_patterns[key]) < 2:
            self._hot_keys.discard(key)

    def _calculate_size(self, value) -> int:
        """Calculate approximate size of a value in bytes."""
        try:
            return sys.getsizeof(pickle.dumps(value))
        except Exception:
            # Fallback estimation
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, tuple)):
                return sum(self._calculate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(
                    self._calculate_size(k) + self._calculate_size(v)
                    for k, v in value.items()
                )
            else:
                return 1024  # Default estimate

    async def get_performance_metrics(self) -> Dict[str, any]:
        """Get detailed performance metrics."""
        stats = await self.get_statistics()

        return {
            "layer": "L1_MEMORY",
            "statistics": stats.to_dict(),
            "eviction_policy": self.eviction_policy,
            "compression_enabled": self.compression_threshold > 0,
            "hot_keys_count": len(self._hot_keys),
            "tracked_patterns": len(self._access_patterns),
            "storage_entries": len(self._storage),
            "memory_usage_mb": self.statistics.total_size_bytes / (1024 * 1024),
            "memory_utilization_percent": (
                self.statistics.total_size_bytes / self.max_size_bytes * 100
            ),
        }

    async def optimize(self) -> Dict[str, int]:
        """Optimize cache performance."""
        optimizations = {
            "compressed_entries": 0,
            "evicted_expired": 0,
            "cleaned_patterns": 0,
        }

        async with self._lock:
            current_time = time.time()
            expired_keys = []

            # Find expired entries
            for key, entry in self._storage.items():
                if entry.is_expired():
                    expired_keys.append(key)

            # Remove expired entries
            for key in expired_keys:
                await self._remove_key(key)
                optimizations["evicted_expired"] += 1

            # Compress large uncompressed entries
            for key, entry in self._storage.items():
                if (
                    entry.size_bytes > self.compression_threshold
                    and not entry.compressed
                ):
                    try:
                        compressed_value = zlib.compress(
                            pickle.dumps(entry.value), self.compression_level
                        )
                        if len(compressed_value) < entry.size_bytes:
                            entry.value = compressed_value
                            entry.compressed = True
                            old_size = entry.size_bytes
                            entry.size_bytes = len(compressed_value)
                            self._update_size_stats(entry.size_bytes - old_size, 0)
                            optimizations["compressed_entries"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to compress entry {key}: {e}")

            # Clean old access patterns
            cutoff_time = current_time - 7200  # 2 hours
            keys_to_clean = []
            for key, accesses in self._access_patterns.items():
                if accesses and max(accesses) < cutoff_time:
                    keys_to_clean.append(key)

            for key in keys_to_clean:
                self._access_patterns.pop(key, None)
                optimizations["cleaned_patterns"] += 1

        return optimizations
