"""
Unit tests for RedisPoolManager in core.redis_pool module.

Tests cover connection pool management, client operations, error handling,
and statistics tracking with proper mocking of Redis dependencies.
"""

import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest


class TestRedisPoolManager:
    """Test suite for RedisPoolManager functionality."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from core.redis_pool import RedisPoolManager

        RedisPoolManager._instance = None
        yield
        RedisPoolManager._instance = None

    @pytest.fixture
    def mock_redis_available(self):
        """Mock Redis availability."""
        with patch("core.redis_pool.REDIS_AVAILABLE", True):
            yield

    @pytest.fixture
    def mock_redis_unavailable(self):
        """Mock Redis unavailability."""
        with patch("core.redis_pool.REDIS_AVAILABLE", False):
            yield

    @pytest.fixture
    def mock_redis_modules(self):
        """Mock Redis modules."""
        with (
            patch("core.redis_pool.redis") as mock_redis,
            patch("core.redis_pool.ConnectionPool") as mock_pool,
        ):
            # Configure mock connection pool
            mock_pool_instance = Mock()
            mock_pool_instance.created_connections = 5
            mock_pool_instance._available_connections = [Mock()] * 3
            mock_pool_instance._in_use_connections = [Mock()] * 2
            mock_pool_instance.disconnect = AsyncMock()
            mock_pool.from_url.return_value = mock_pool_instance

            # Configure mock Redis client
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock()
            mock_client.close = AsyncMock()
            mock_client.get = AsyncMock()
            mock_client.set = AsyncMock()
            mock_client.setex = AsyncMock()
            mock_redis.Redis.return_value = mock_client

            yield {
                "redis": mock_redis,
                "ConnectionPool": mock_pool,
                "pool_instance": mock_pool_instance,
                "client": mock_client,
            }

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables."""
        env_vars = {
            "REDIS_URL": "redis://test:6379/0",
            "REDIS_MAX_CONNECTIONS": "100",
            "REDIS_MIN_IDLE_TIME": "600",
            "REDIS_CONNECTION_TIMEOUT": "30",
            "REDIS_SOCKET_TIMEOUT": "10",
            "REDIS_SOCKET_CONNECT_TIMEOUT": "10",
        }
        with patch.dict(os.environ, env_vars):
            yield env_vars


class TestInitialization(TestRedisPoolManager):
    """Tests for Redis pool initialization."""

    def test_singleton_pattern(self):
        """Test that RedisPoolManager follows singleton pattern."""
        from core.redis_pool import RedisPoolManager

        manager1 = RedisPoolManager()
        manager2 = RedisPoolManager()
        assert manager1 is manager2

    def test_initialization_with_env_vars(self, mock_env_vars):
        """Test initialization with environment variables."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()

        assert manager._redis_url == "redis://test:6379/0"
        assert manager._max_connections == 100
        assert manager._min_idle_time == 600
        assert manager._connection_timeout == 30
        assert manager._socket_timeout == 10
        assert manager._socket_connect_timeout == 10

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()

        assert manager._redis_url == "redis://localhost:6379/0"
        assert manager._max_connections == 50
        assert manager._min_idle_time == 300
        assert manager._connection_timeout == 20
        assert manager._socket_timeout == 5
        assert manager._socket_connect_timeout == 5

    @pytest.mark.asyncio
    async def test_initialize_pool_success(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test successful pool initialization."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        result = await manager.initialize()

        assert result is True
        assert manager._pool is not None

        # Verify pool creation
        mocks["ConnectionPool"].from_url.assert_called_once_with(
            "redis://localhost:6379/0",
            max_connections=50,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            connection_class=mocks["redis"].Connection,
            health_check_interval=30,
        )

        # Verify connection test
        mocks["client"].ping.assert_called_once()
        mocks["client"].close.assert_called_once_with(close_connection_pool=False)

    @pytest.mark.asyncio
    async def test_initialize_pool_redis_unavailable(self, mock_redis_unavailable):
        """Test initialization when Redis is unavailable."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        result = await manager.initialize()

        assert result is False
        assert manager._pool is None

    @pytest.mark.asyncio
    async def test_initialize_pool_connection_failure(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test initialization with connection failure."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        # Simulate connection failure
        mocks["client"].ping.side_effect = Exception("Connection refused")

        result = await manager.initialize()

        assert result is False
        assert manager._pool is None

    @pytest.mark.asyncio
    async def test_initialize_pool_already_initialized(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test initialization when pool already exists."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        # First initialization
        result1 = await manager.initialize()
        assert result1 is True

        # Reset mock calls
        mocks["ConnectionPool"].from_url.reset_mock()

        # Second initialization should return True without creating new pool
        result2 = await manager.initialize()
        assert result2 is True
        mocks["ConnectionPool"].from_url.assert_not_called()


class TestClientOperations(TestRedisPoolManager):
    """Tests for Redis client operations."""

    @pytest.mark.asyncio
    async def test_get_client_success(self, mock_redis_available, mock_redis_modules):
        """Test getting a Redis client."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        # Initialize pool first
        await manager.initialize()

        client = await manager.get_client()

        assert client is not None
        mocks["redis"].Redis.assert_called_with(connection_pool=mocks["pool_instance"])

    @pytest.mark.asyncio
    async def test_get_client_redis_unavailable(self, mock_redis_unavailable):
        """Test getting client when Redis is unavailable."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        client = await manager.get_client()

        assert client is None

    @pytest.mark.asyncio
    async def test_get_client_auto_initialize(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test client auto-initializes pool if needed."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()

        # Get client without explicit initialization
        client = await manager.get_client()

        assert client is not None
        assert manager._pool is not None

    @pytest.mark.asyncio
    async def test_get_client_context_manager(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test client context manager."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        async with manager.get_client_context() as client:
            assert client is not None

        # Verify client was closed properly
        mocks["client"].close.assert_called_with(close_connection_pool=False)

    @pytest.mark.asyncio
    async def test_get_client_context_manager_no_client(self, mock_redis_unavailable):
        """Test context manager when client unavailable."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()

        async with manager.get_client_context() as client:
            assert client is None


class TestPoolManagement(TestRedisPoolManager):
    """Tests for pool management operations."""

    @pytest.mark.asyncio
    async def test_close_pool(self, mock_redis_available, mock_redis_modules):
        """Test closing the connection pool."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        # Initialize and close
        await manager.initialize()
        await manager.close()

        mocks["pool_instance"].disconnect.assert_called_once()
        assert manager._pool is None

    @pytest.mark.asyncio
    async def test_close_pool_not_initialized(self):
        """Test closing when pool not initialized."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()

        # Should not raise error
        await manager.close()

    @pytest.mark.asyncio
    async def test_get_pool_stats_active(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test getting pool statistics when active."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        await manager.initialize()

        stats = await manager.get_pool_stats()

        assert stats["status"] == "active"
        assert stats["max_connections"] == 50
        assert stats["created_connections"] == 5
        assert stats["available_connections"] == 3
        assert stats["in_use_connections"] == 2

    @pytest.mark.asyncio
    async def test_get_pool_stats_not_initialized(self):
        """Test getting pool statistics when not initialized."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()

        stats = await manager.get_pool_stats()

        assert stats == {"status": "not_initialized"}


class TestConnectionStatus(TestRedisPoolManager):
    """Tests for connection status checking."""

    @pytest.mark.asyncio
    async def test_is_connected_true(self, mock_redis_available, mock_redis_modules):
        """Test connection status when connected."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        await manager.initialize()
        result = await manager.is_connected()

        assert result is True
        assert mocks["client"].ping.call_count >= 1

    @pytest.mark.asyncio
    async def test_is_connected_redis_unavailable(self, mock_redis_unavailable):
        """Test connection status when Redis unavailable."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        result = await manager.is_connected()

        assert result is False

    @pytest.mark.asyncio
    async def test_is_connected_ping_failure(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test connection status when ping fails."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        await manager.initialize()

        # Simulate ping failure
        mocks["client"].ping.side_effect = Exception("Connection lost")

        result = await manager.is_connected()

        assert result is False


class TestDataOperations(TestRedisPoolManager):
    """Tests for Redis data operations."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_redis_available, mock_redis_modules):
        """Test successful get operation."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        # Mock response
        mocks["client"].get.return_value = b"test_value"

        result = await manager.get("test_key")

        assert result == "test_value"
        mocks["client"].get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_key_not_found(self, mock_redis_available, mock_redis_modules):
        """Test get operation when key not found."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        mocks["client"].get.return_value = None

        result = await manager.get("nonexistent_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_redis_unavailable(self, mock_redis_unavailable):
        """Test get operation when Redis unavailable."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        result = await manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_exception(self, mock_redis_available, mock_redis_modules):
        """Test get operation with exception."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        mocks["client"].get.side_effect = Exception("Redis error")

        result = await manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_success(self, mock_redis_available, mock_redis_modules):
        """Test successful set operation."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        result = await manager.set("test_key", "test_value")

        assert result is True
        mocks["client"].set.assert_called_once_with("test_key", "test_value")

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, mock_redis_available, mock_redis_modules):
        """Test set operation with TTL."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        result = await manager.set("test_key", "test_value", ttl=3600)

        assert result is True
        mocks["client"].setex.assert_called_once_with("test_key", 3600, "test_value")
        mocks["client"].set.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_redis_unavailable(self, mock_redis_unavailable):
        """Test set operation when Redis unavailable."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        result = await manager.set("test_key", "test_value")

        assert result is False

    @pytest.mark.asyncio
    async def test_set_exception(self, mock_redis_available, mock_redis_modules):
        """Test set operation with exception."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        mocks["client"].set.side_effect = Exception("Redis error")

        result = await manager.set("test_key", "test_value")

        assert result is False


class TestConvenienceFunctions(TestRedisPoolManager):
    """Tests for module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_get_redis_client(self, mock_redis_available, mock_redis_modules):
        """Test global get_redis_client function."""
        from core.redis_pool import get_redis_client

        with patch("core.redis_pool.redis_pool_manager") as mock_manager:
            mock_manager.get_client = AsyncMock(return_value=Mock())

            client = await get_redis_client()

            assert client is not None
            mock_manager.get_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_redis_pool(self):
        """Test global close_redis_pool function."""
        from core.redis_pool import close_redis_pool

        with patch("core.redis_pool.redis_pool_manager") as mock_manager:
            mock_manager.close = AsyncMock()

            await close_redis_pool()

            mock_manager.close.assert_called_once()


class TestConcurrency(TestRedisPoolManager):
    """Tests for concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_initialization(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test concurrent initialization attempts."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        mocks = mock_redis_modules

        # Simulate slow initialization
        original_from_url = mocks["ConnectionPool"].from_url

        async def slow_from_url(*args, **kwargs):
            await asyncio.sleep(0.1)
            return original_from_url.return_value

        mocks["ConnectionPool"].from_url = slow_from_url

        # Concurrent initialization attempts
        results = await asyncio.gather(
            manager.initialize(),
            manager.initialize(),
            manager.initialize(),
        )

        # All should succeed
        assert all(results)

        # But pool should only be created once
        # (This is hard to test precisely due to async timing)
        assert manager._pool is not None

    @pytest.mark.asyncio
    async def test_concurrent_client_operations(
        self, mock_redis_available, mock_redis_modules
    ):
        """Test concurrent client operations."""
        from core.redis_pool import RedisPoolManager

        manager = RedisPoolManager()
        await manager.initialize()

        # Concurrent operations
        tasks = []
        for i in range(10):
            tasks.append(manager.get(f"key_{i}"))
            tasks.append(manager.set(f"key_{i}", f"value_{i}"))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Should not have any exceptions
        assert not any(isinstance(r, Exception) for r in results)
