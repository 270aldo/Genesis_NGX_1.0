"""
Enhanced Database Connection Manager for GENESIS Performance Optimization.

This module provides elite-level database performance optimizations including:
- Connection pooling with intelligent sizing
- Query result caching with automatic invalidation
- Batch operations for bulk inserts/updates
- Query performance monitoring and analytics
- Automatic connection health checks
- Circuit breaker pattern for resilience
"""

import hashlib
import json
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
from asyncpg.pool import Pool
from fastapi import HTTPException
from pydantic import BaseSettings

from core.circuit_breaker import CircuitBreaker
from core.logging_config import get_logger
from core.redis_pool import get_redis_pool
from core.settings import Settings

logger = get_logger(__name__)


class DatabaseConfig(BaseSettings):
    """Database configuration with performance tuning."""

    # Connection pool settings
    min_pool_size: int = 5
    max_pool_size: int = 20
    pool_recycle_time: int = 3600  # 1 hour
    command_timeout: float = 30.0

    # Performance settings
    enable_query_cache: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    enable_batch_operations: bool = True
    batch_size: int = 1000

    # Monitoring settings
    enable_query_monitoring: bool = True
    slow_query_threshold: float = 1.0  # 1 second


class QueryCache:
    """Advanced query caching with Redis backend."""

    def __init__(self, redis_pool, ttl: int = 300):
        self.redis = redis_pool
        self.ttl = ttl

    def _generate_key(self, query: str, params: tuple = ()) -> str:
        """Generate cache key for query and parameters."""
        query_hash = hashlib.md5(f"{query}{params}".encode()).hexdigest()
        return f"db_query:{query_hash}"

    async def get(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Get cached query result."""
        try:
            key = self._generate_key(query, params)
            cached_data = await self.redis.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None

    async def set(self, query: str, params: tuple, result: Any):
        """Cache query result."""
        try:
            key = self._generate_key(query, params)
            serialized_result = json.dumps(result, default=str)
            await self.redis.setex(key, self.ttl, serialized_result)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    async def invalidate_pattern(self, pattern: str):
        """Invalidate cached queries matching pattern."""
        try:
            keys = await self.redis.keys(f"db_query:*{pattern}*")
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cached queries")
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")


class QueryMonitor:
    """Query performance monitoring and analytics."""

    def __init__(self, slow_query_threshold: float = 1.0):
        self.slow_query_threshold = slow_query_threshold
        self.query_stats = {}

    async def record_query(self, query: str, duration: float, result_count: int = 0):
        """Record query execution metrics."""
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]

        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                "query_sample": query[:100],
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "slow_queries": 0,
            }

        stats = self.query_stats[query_hash]
        stats["count"] += 1
        stats["total_time"] += duration
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], duration)

        if duration > self.slow_query_threshold:
            stats["slow_queries"] += 1
            logger.warning(f"Slow query detected: {duration:.3f}s - {query[:100]}...")

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        return {
            "total_queries": sum(s["count"] for s in self.query_stats.values()),
            "slow_queries": sum(s["slow_queries"] for s in self.query_stats.values()),
            "avg_query_time": sum(
                s["avg_time"] * s["count"] for s in self.query_stats.values()
            )
            / max(sum(s["count"] for s in self.query_stats.values()), 1),
            "top_slow_queries": sorted(
                self.query_stats.values(), key=lambda x: x["avg_time"], reverse=True
            )[:10],
        }


class DatabaseManager:
    """Elite database manager with advanced performance optimizations."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.config = DatabaseConfig()
        self.pool: Optional[Pool] = None
        self.cache = None
        self.monitor = QueryMonitor(self.config.slow_query_threshold)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=30, expected_exception=Exception
        )

    async def initialize(self):
        """Initialize database connection pool and dependencies."""
        try:
            # Initialize connection pool
            self.pool = await asyncpg.create_pool(
                str(self.settings.supabase_url).replace("https://", "postgresql://"),
                min_size=self.config.min_pool_size,
                max_size=self.config.max_pool_size,
                command_timeout=self.config.command_timeout,
                server_settings={"jit": "off", "application_name": "genesis-api"},
            )

            # Initialize query cache
            if self.config.enable_query_cache:
                redis_pool = get_redis_pool()
                self.cache = QueryCache(redis_pool, self.config.cache_ttl_seconds)

            # Test connection
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")

            logger.info(
                f"Database pool initialized: {self.config.min_pool_size}-{self.config.max_pool_size} connections"
            )

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def close(self):
        """Close database connections."""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with circuit breaker protection."""
        if not self.pool:
            raise HTTPException(500, "Database pool not initialized")

        async with self.circuit_breaker:
            async with self.pool.acquire() as connection:
                yield connection

    async def execute_query(
        self,
        query: str,
        *args,
        fetch_mode: str = "all",
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ) -> Any:
        """
        Execute query with advanced optimizations.

        Args:
            query: SQL query string
            *args: Query parameters
            fetch_mode: "all", "one", "val", or "none"
            use_cache: Whether to use query caching
            cache_ttl: Override default cache TTL

        Returns:
            Query result based on fetch_mode
        """
        start_time = time.time()

        # Check cache first
        if use_cache and self.cache and fetch_mode in ["all", "one", "val"]:
            cached_result = await self.cache.get(query, args)
            if cached_result is not None:
                logger.debug("Query served from cache")
                return cached_result

        # Execute query
        async with self.get_connection() as conn:
            try:
                if fetch_mode == "all":
                    result = await conn.fetch(query, *args)
                    result = [dict(row) for row in result] if result else []
                elif fetch_mode == "one":
                    result = await conn.fetchrow(query, *args)
                    result = dict(result) if result else None
                elif fetch_mode == "val":
                    result = await conn.fetchval(query, *args)
                elif fetch_mode == "none":
                    result = await conn.execute(query, *args)
                else:
                    raise ValueError(f"Invalid fetch_mode: {fetch_mode}")

                # Cache result
                if (
                    use_cache
                    and self.cache
                    and fetch_mode in ["all", "one", "val"]
                    and result is not None
                ):
                    await self.cache.set(query, args, result)

                # Record performance metrics
                duration = time.time() - start_time
                result_count = len(result) if isinstance(result, list) else 1

                if self.config.enable_query_monitoring:
                    await self.monitor.record_query(query, duration, result_count)

                return result

            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise

    async def execute_batch(
        self, query: str, data: List[Tuple], batch_size: Optional[int] = None
    ) -> int:
        """
        Execute batch operations with optimal performance.

        Args:
            query: SQL query with parameter placeholders
            data: List of parameter tuples
            batch_size: Override default batch size

        Returns:
            Number of affected rows
        """
        if not self.config.enable_batch_operations:
            raise HTTPException(500, "Batch operations disabled")

        batch_size = batch_size or self.config.batch_size
        total_affected = 0
        start_time = time.time()

        async with self.get_connection() as conn:
            async with conn.transaction():
                for i in range(0, len(data), batch_size):
                    batch = data[i : i + batch_size]
                    try:
                        # Use executemany for better performance
                        await conn.executemany(query, batch)
                        total_affected += len(batch)
                    except Exception as e:
                        logger.error(f"Batch execution failed at offset {i}: {e}")
                        raise

        duration = time.time() - start_time
        logger.info(
            f"Batch operation completed: {total_affected} rows in {duration:.3f}s"
        )

        return total_affected

    async def execute_transaction(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute multiple operations in a single transaction.

        Args:
            operations: List of operation dictionaries with 'query', 'args', 'fetch_mode'

        Returns:
            List of results for each operation
        """
        results = []
        start_time = time.time()

        async with self.get_connection() as conn:
            async with conn.transaction():
                for op in operations:
                    query = op["query"]
                    args = op.get("args", ())
                    fetch_mode = op.get("fetch_mode", "none")

                    if fetch_mode == "all":
                        result = await conn.fetch(query, *args)
                        result = [dict(row) for row in result] if result else []
                    elif fetch_mode == "one":
                        result = await conn.fetchrow(query, *args)
                        result = dict(result) if result else None
                    elif fetch_mode == "val":
                        result = await conn.fetchval(query, *args)
                    else:
                        result = await conn.execute(query, *args)

                    results.append(result)

        duration = time.time() - start_time
        logger.info(
            f"Transaction completed: {len(operations)} operations in {duration:.3f}s"
        )

        return results

    async def get_health_status(self) -> Dict[str, Any]:
        """Get database health status and metrics."""
        try:
            async with self.get_connection() as conn:
                # Test query
                await conn.execute("SELECT 1")

                # Get connection stats
                pool_stats = {
                    "size": self.pool.get_size(),
                    "min_size": self.pool.get_min_size(),
                    "max_size": self.pool.get_max_size(),
                    "idle": self.pool.get_idle_size(),
                }

                # Get performance report
                performance = self.monitor.get_performance_report()

                return {
                    "status": "healthy",
                    "pool": pool_stats,
                    "performance": performance,
                    "cache_enabled": self.config.enable_query_cache,
                    "circuit_breaker": {
                        "state": self.circuit_breaker.state,
                        "failure_count": self.circuit_breaker.failure_count,
                    },
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def invalidate_cache(self, pattern: str = "*"):
        """Invalidate cached queries."""
        if self.cache:
            await self.cache.invalidate_pattern(pattern)


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        from core.settings import Settings

        settings = Settings()
        _db_manager = DatabaseManager(settings)
        await _db_manager.initialize()
    return _db_manager


async def get_db():
    """FastAPI dependency for database manager."""
    db_manager = await get_database_manager()
    return db_manager
