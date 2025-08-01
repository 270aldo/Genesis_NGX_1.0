"""
Unit tests for PersistenceClient in clients.persistence module.

Tests cover user management and conversation logging functionality
with both mock and real modes.
"""

import uuid
from unittest.mock import MagicMock

import pytest

from clients.persistence import PersistenceClient


class TestPersistenceClient:
    """Test suite for PersistenceClient functionality."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create a mock SupabaseClient instance."""
        client = MagicMock()
        return client

    @pytest.fixture
    def persistence_client(self, mock_supabase_client):
        """Create a PersistenceClient instance with mock mode enabled."""
        client = PersistenceClient(mock_supabase_client)
        client.is_mock = True
        return client

    @pytest.fixture
    def test_api_key(self):
        """Test API key."""
        return "test-api-key-123"

    @pytest.fixture
    def test_user_id(self):
        """Test user ID."""
        return str(uuid.uuid4())


class TestUserManagement(TestPersistenceClient):
    """Tests for user management functionality."""

    def test_get_or_create_user_creates_new_user(
        self, persistence_client, test_api_key
    ):
        """Test creating a new user with API key."""
        # Execute
        user = persistence_client.get_or_create_user_by_api_key(test_api_key)

        # Assert
        assert user is not None
        assert "id" in user
        assert user["api_key"] == test_api_key
        assert "created_at" in user
        assert isinstance(user["id"], str)
        assert len(persistence_client._mock_users) == 1

    def test_get_or_create_user_returns_existing_user(
        self, persistence_client, test_api_key
    ):
        """Test retrieving an existing user by API key."""
        # Create user first
        user1 = persistence_client.get_or_create_user_by_api_key(test_api_key)

        # Get same user again
        user2 = persistence_client.get_or_create_user_by_api_key(test_api_key)

        # Assert
        assert user1["id"] == user2["id"]
        assert user1["api_key"] == user2["api_key"]
        assert len(persistence_client._mock_users) == 1

    def test_multiple_users_with_different_api_keys(self, persistence_client):
        """Test creating multiple users with different API keys."""
        # Create multiple users
        api_keys = ["key1", "key2", "key3"]
        users = []

        for key in api_keys:
            user = persistence_client.get_or_create_user_by_api_key(key)
            users.append(user)

        # Assert
        assert len(persistence_client._mock_users) == 3
        assert len(set(u["id"] for u in users)) == 3  # All IDs unique
        assert all(u["api_key"] == k for u, k in zip(users, api_keys))

    def test_real_mode_raises_not_implemented(self, mock_supabase_client):
        """Test that real mode raises NotImplementedError."""
        client = PersistenceClient(mock_supabase_client)
        client.is_mock = False

        with pytest.raises(NotImplementedError) as exc_info:
            client.get_or_create_user_by_api_key("test-key")

        assert "modo sincrónico" in str(exc_info.value)


class TestConversationLogging(TestPersistenceClient):
    """Tests for conversation logging functionality."""

    def test_log_single_message(self, persistence_client, test_user_id):
        """Test logging a single conversation message."""
        # Execute
        result = persistence_client.log_conversation_message(
            test_user_id, "user", "Hello, assistant!"
        )

        # Assert
        assert result is True
        assert len(persistence_client._mock_conversations) == 1

        message = persistence_client._mock_conversations[0]
        assert message["user_id"] == test_user_id
        assert message["role"] == "user"
        assert message["message"] == "Hello, assistant!"
        assert "id" in message
        assert "created_at" in message

    def test_log_multiple_messages(self, persistence_client, test_user_id):
        """Test logging multiple conversation messages."""
        messages = [
            ("user", "Question 1"),
            ("agent", "Answer 1"),
            ("user", "Question 2"),
            ("agent", "Answer 2"),
        ]

        # Log messages
        for role, content in messages:
            result = persistence_client.log_conversation_message(
                test_user_id, role, content
            )
            assert result is True

        # Assert
        assert len(persistence_client._mock_conversations) == 4

        for i, (role, content) in enumerate(messages):
            msg = persistence_client._mock_conversations[i]
            assert msg["role"] == role
            assert msg["message"] == content

    def test_log_system_messages(self, persistence_client, test_user_id):
        """Test logging system messages."""
        result = persistence_client.log_conversation_message(
            test_user_id, "system", "System initialization"
        )

        assert result is True
        message = persistence_client._mock_conversations[0]
        assert message["role"] == "system"

    def test_real_mode_raises_not_implemented(self, mock_supabase_client, test_user_id):
        """Test that real mode raises NotImplementedError."""
        client = PersistenceClient(mock_supabase_client)
        client.is_mock = False

        with pytest.raises(NotImplementedError) as exc_info:
            client.log_conversation_message(test_user_id, "user", "test")

        assert "modo sincrónico" in str(exc_info.value)


class TestConversationHistory(TestPersistenceClient):
    """Tests for conversation history retrieval."""

    def test_empty_history(self, persistence_client, test_user_id):
        """Test retrieving empty conversation history."""
        history = persistence_client.get_conversation_history(test_user_id)
        assert history == []

    def test_history_single_user(self, persistence_client, test_user_id):
        """Test retrieving history for a single user."""
        # Log messages
        messages = ["Message 1", "Message 2", "Message 3"]
        for msg in messages:
            persistence_client.log_conversation_message(test_user_id, "user", msg)

        # Get history
        history = persistence_client.get_conversation_history(test_user_id)

        # Assert
        assert len(history) == 3
        for i, msg in enumerate(messages):
            assert history[i]["message"] == msg
            assert history[i]["user_id"] == test_user_id

    def test_history_multiple_users_filtered(self, persistence_client):
        """Test that history is correctly filtered by user ID."""
        user1 = str(uuid.uuid4())
        user2 = str(uuid.uuid4())

        # Log messages for different users
        persistence_client.log_conversation_message(user1, "user", "User1 Message")
        persistence_client.log_conversation_message(user2, "user", "User2 Message")
        persistence_client.log_conversation_message(user1, "agent", "User1 Response")

        # Get history for each user
        history1 = persistence_client.get_conversation_history(user1)
        history2 = persistence_client.get_conversation_history(user2)

        # Assert
        assert len(history1) == 2
        assert all(msg["user_id"] == user1 for msg in history1)
        assert history1[0]["message"] == "User1 Message"
        assert history1[1]["message"] == "User1 Response"

        assert len(history2) == 1
        assert history2[0]["user_id"] == user2
        assert history2[0]["message"] == "User2 Message"

    def test_history_with_limit(self, persistence_client, test_user_id):
        """Test retrieving history with limit."""
        # Log 10 messages
        for i in range(10):
            persistence_client.log_conversation_message(
                test_user_id, "user", f"Message {i}"
            )

        # Get limited history
        history = persistence_client.get_conversation_history(test_user_id, limit=5)

        # Assert
        assert len(history) == 5
        for i in range(5):
            assert history[i]["message"] == f"Message {i}"

    def test_history_with_offset(self, persistence_client, test_user_id):
        """Test retrieving history with offset."""
        # Log 10 messages
        for i in range(10):
            persistence_client.log_conversation_message(
                test_user_id, "user", f"Message {i}"
            )

        # Get history with offset
        history = persistence_client.get_conversation_history(test_user_id, offset=5)

        # Assert
        assert len(history) == 5
        for i in range(5):
            assert history[i]["message"] == f"Message {i + 5}"

    def test_history_with_limit_and_offset(self, persistence_client, test_user_id):
        """Test pagination with both limit and offset."""
        # Log 20 messages
        for i in range(20):
            persistence_client.log_conversation_message(
                test_user_id, "user", f"Message {i}"
            )

        # Get different pages
        page1 = persistence_client.get_conversation_history(
            test_user_id, limit=5, offset=0
        )
        page2 = persistence_client.get_conversation_history(
            test_user_id, limit=5, offset=5
        )
        page3 = persistence_client.get_conversation_history(
            test_user_id, limit=5, offset=10
        )

        # Assert
        assert len(page1) == 5
        assert [m["message"] for m in page1] == [f"Message {i}" for i in range(5)]

        assert len(page2) == 5
        assert [m["message"] for m in page2] == [f"Message {i}" for i in range(5, 10)]

        assert len(page3) == 5
        assert [m["message"] for m in page3] == [f"Message {i}" for i in range(10, 15)]

    def test_history_offset_beyond_messages(self, persistence_client, test_user_id):
        """Test offset beyond available messages."""
        # Log 5 messages
        for i in range(5):
            persistence_client.log_conversation_message(
                test_user_id, "user", f"Message {i}"
            )

        # Get history with large offset
        history = persistence_client.get_conversation_history(test_user_id, offset=10)

        # Assert
        assert history == []

    def test_real_mode_raises_not_implemented(self, mock_supabase_client, test_user_id):
        """Test that real mode raises NotImplementedError."""
        client = PersistenceClient(mock_supabase_client)
        client.is_mock = False

        with pytest.raises(NotImplementedError) as exc_info:
            client.get_conversation_history(test_user_id)

        assert "modo sincrónico" in str(exc_info.value)


class TestEdgeCases(TestPersistenceClient):
    """Tests for edge cases and error scenarios."""

    def test_empty_api_key(self, persistence_client):
        """Test handling empty API key."""
        user = persistence_client.get_or_create_user_by_api_key("")
        assert user["api_key"] == ""
        assert "id" in user

    def test_none_api_key(self, persistence_client):
        """Test handling None API key."""
        user = persistence_client.get_or_create_user_by_api_key(None)
        assert user["api_key"] is None
        assert "id" in user

    def test_very_long_message(self, persistence_client, test_user_id):
        """Test logging very long messages."""
        long_message = "x" * 10000
        result = persistence_client.log_conversation_message(
            test_user_id, "user", long_message
        )

        assert result is True
        assert persistence_client._mock_conversations[0]["message"] == long_message

    def test_special_characters_in_message(self, persistence_client, test_user_id):
        """Test logging messages with special characters."""
        special_message = "Hello 👋 \n\t@user #test $pecial \"quoted\" 'text'"
        result = persistence_client.log_conversation_message(
            test_user_id, "user", special_message
        )

        assert result is True
        assert persistence_client._mock_conversations[0]["message"] == special_message

    def test_concurrent_user_creation(self, persistence_client):
        """Test that same API key always returns same user (simulating concurrency)."""
        api_key = "concurrent-test-key"  # pragma: allowlist secret

        # Simulate multiple "concurrent" calls
        users = []
        for _ in range(5):
            user = persistence_client.get_or_create_user_by_api_key(api_key)
            users.append(user)

        # All should be the same user
        assert all(u["id"] == users[0]["id"] for u in users)
        assert len(persistence_client._mock_users) == 1
