"""
Unit tests for StateManager and LRUCache in core.state_manager_optimized module.

Tests cover singleton pattern, caching functionality, conversation state management,
temp context operations, and statistics tracking.
"""

import asyncio
import time

import pytest

from core.state_manager_optimized import LRUCache, StateManager


class TestLRUCache:
    """Test suite for LRUCache implementation."""

    def test_basic_get_set(self):
        """Test basic cache get and set operations."""
        cache = LRUCache(capacity=10)

        # Set value
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Overwrite value
        cache.set("key1", "value2")
        assert cache.get("key1") == "value2"

        # Non-existent key
        assert cache.get("nonexistent") is None

    def test_capacity_eviction(self):
        """Test LRU eviction when capacity is reached."""
        cache = LRUCache(capacity=3)

        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Add one more - should evict key1
        cache.set("key4", "value4")

        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_lru_order_update(self):
        """Test that accessing items updates LRU order."""
        cache = LRUCache(capacity=3)

        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it most recently used
        cache.get("key1")

        # Add new item - should evict key2 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # Still in cache
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_clear_cache(self):
        """Test clearing the cache."""
        cache = LRUCache(capacity=10)

        # Add items
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Clear
        cache.clear()

        # Should be empty
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert len(cache.cache) == 0

    def test_ttl_expiration(self):
        """Test TTL expiration functionality."""
        cache = LRUCache(capacity=10, default_ttl=0.1)  # 100ms TTL

        # Set value with TTL
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None

    def test_custom_ttl(self):
        """Test custom TTL per item."""
        cache = LRUCache(capacity=10)

        # Set with custom TTL
        cache.set("key1", "value1", ttl=0.1)
        cache.set("key2", "value2", ttl=1.0)

        # After 200ms, key1 should expire but not key2
        time.sleep(0.2)
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_size_method(self):
        """Test cache size tracking."""
        cache = LRUCache(capacity=10)

        assert cache.size() == 0

        cache.set("key1", "value1")
        assert cache.size() == 1

        cache.set("key2", "value2")
        assert cache.size() == 2

        cache.clear()
        assert cache.size() == 0

    def test_contains_method(self):
        """Test checking if key exists in cache."""
        cache = LRUCache(capacity=10)

        cache.set("key1", "value1")

        assert cache.contains("key1") is True
        assert cache.contains("key2") is False

        # Expired items should not be contained
        cache.set("key3", "value3", ttl=0.1)
        time.sleep(0.2)
        assert cache.contains("key3") is False


class TestStateManager:
    """Test suite for StateManager functionality."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        StateManager._instance = None
        yield
        StateManager._instance = None

    def test_singleton_pattern(self):
        """Test that StateManager follows singleton pattern."""
        manager1 = StateManager()
        manager2 = StateManager()
        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_get_conversation_state(self):
        """Test getting and creating conversation state."""
        manager = StateManager()

        # New conversation
        state = await manager.get_conversation_state("conv1")
        assert state["conversation_id"] == "conv1"
        assert state["messages"] == []
        assert state["metadata"] == {}  # Use metadata instead of agent_context
        assert "created_at" in state
        assert "updated_at" in state

        # Existing conversation
        state2 = await manager.get_conversation_state("conv1")
        assert state2["conversation_id"] == state["conversation_id"]
        assert state2["created_at"] == state["created_at"]

    @pytest.mark.asyncio
    async def test_update_conversation_state(self):
        """Test updating conversation state."""
        manager = StateManager()

        # Create initial state
        await manager.get_conversation_state("conv1")

        # Update state
        updates = {
            "messages": [{"role": "user", "content": "Hello"}],
            "metadata": {"key": "value"},  # Use metadata instead of agent_context
        }

        # Use save_conversation since update_conversation_state doesn't exist
        current_state = await manager.get_conversation_state("conv1")
        current_state.update(updates)
        await manager.save_conversation("conv1", current_state)
        updated = await manager.get_conversation_state("conv1")

        # Verify updates
        assert updated["messages"] == updates["messages"]
        assert updated["metadata"] == updates["metadata"]
        assert updated["updated_at"] > updated["created_at"]

    @pytest.mark.asyncio
    async def test_delete_conversation_state(self):
        """Test deleting conversation state."""
        manager = StateManager()

        # Create state
        await manager.get_conversation_state("conv1")

        # Delete
        result = await manager.delete_conversation_state("conv1")
        assert result is True

        # Should create new state
        state = await manager.get_conversation_state("conv1")
        assert state["messages"] == []

    @pytest.mark.asyncio
    async def test_set_get_temp_context(self):
        """Test temporary context storage."""
        manager = StateManager()

        # Set context with TTL
        await manager.set_temp_context("user1", "key1", {"data": "value"}, ttl=1.0)

        # Get context
        data = await manager.get_temp_context("user1", "key1")
        assert data == {"data": "value"}

        # Non-existent context
        assert await manager.get_temp_context("user1", "key2") is None

    @pytest.mark.asyncio
    async def test_temp_context_expiration(self):
        """Test temp context TTL expiration."""
        manager = StateManager()

        # Set with short TTL
        await manager.set_temp_context("user1", "key1", "data", ttl=0.1)

        # Should exist immediately
        assert await manager.get_temp_context("user1", "key1") == "data"

        # Wait for expiration
        await asyncio.sleep(0.2)
        assert await manager.get_temp_context("user1", "key1") is None

    @pytest.mark.asyncio
    async def test_delete_temp_context(self):
        """Test deleting temp context."""
        manager = StateManager()

        # Set context
        await manager.set_temp_context("user1", "key1", "data")

        # Delete
        result = await manager.delete_temp_context("user1", "key1")
        assert result is True

        # Should be gone
        assert await manager.get_temp_context("user1", "key1") is None

        # Delete non-existent
        result = await manager.delete_temp_context("user1", "key2")
        assert result is False

    def test_track_request(self):
        """Test request tracking statistics."""
        manager = StateManager()

        # Track requests
        manager.track_request("agent1", 100)
        manager.track_request("agent1", 200)
        manager.track_request("agent2", 150)

        stats = manager.get_stats()

        # Verify stats
        assert stats["total_requests"] == 3
        assert "agent1" in stats["requests_by_agent"]
        assert stats["requests_by_agent"]["agent1"]["count"] == 2
        assert stats["requests_by_agent"]["agent1"]["total_time"] == 300
        assert stats["requests_by_agent"]["agent1"]["avg_time"] == 150

        assert "agent2" in stats["requests_by_agent"]
        assert stats["requests_by_agent"]["agent2"]["count"] == 1
        assert stats["requests_by_agent"]["agent2"]["avg_time"] == 150

    def test_clear_stats(self):
        """Test clearing statistics."""
        manager = StateManager()

        # Track and clear
        manager.track_request("agent1", 100)
        manager.clear_stats()

        stats = manager.get_stats()
        assert stats["total_requests"] == 0
        assert stats["requests_by_agent"] == {}

    def test_clear_all(self):
        """Test clearing all state."""
        manager = StateManager()

        # Add various data
        asyncio.run(manager.get_conversation_state("conv1"))
        asyncio.run(manager.set_temp_context("user1", "key1", "data"))
        manager.track_request("agent1", 100)

        # Clear all
        manager.clear_all()

        # Everything should be empty
        assert manager.conversation_cache.size() == 0
        assert manager.temp_context_cache.size() == 0
        stats = manager.get_stats()
        assert stats["total_requests"] == 0

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent access to state manager."""
        manager = StateManager()

        # Concurrent conversation updates
        async def update_conversation(conv_id, message):
            state = await manager.get_conversation_state(conv_id)
            messages = state["messages"] + [message]
            state = await manager.get_conversation_state(conv_id)
            state["messages"] = messages
            await manager.save_conversation(conv_id, state)

        # Run concurrent updates
        tasks = []
        for i in range(10):
            task = update_conversation("conv1", {"id": i, "content": f"Message {i}"})
            tasks.append(task)

        await asyncio.gather(*tasks)

        # Check final state
        state = await manager.get_conversation_state("conv1")
        assert len(state["messages"]) == 10

    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test that caching improves performance."""
        manager = StateManager()

        # First access - creates state
        start = time.time()
        await manager.get_conversation_state("perf_test")
        first_time = time.time() - start

        # Second access - should be cached
        start = time.time()
        await manager.get_conversation_state("perf_test")
        cached_time = time.time() - start

        # Cached access should be faster
        # Note: This might be flaky on slow systems
        assert cached_time < first_time
