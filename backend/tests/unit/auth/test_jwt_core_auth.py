"""
Unit tests for JWT authentication in core.auth module.

Tests the get_current_user and get_optional_user functions
with various token scenarios.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status


@pytest.fixture
def mock_modules():
    """Mock external modules before importing."""
    with patch.dict(
        "sys.modules",
        {"supabase": MagicMock(), "gotrue": MagicMock(), "gotrue.errors": MagicMock()},
    ):
        # Setup mock types
        import sys

        sys.modules["supabase"].Client = type("Client", (), {})
        sys.modules["supabase"].create_client = MagicMock()

        # Create AuthApiError mock
        class MockAuthApiError(Exception):
            def __init__(self, message, status_code=401):
                self.message = message
                self.status_code = status_code
                super().__init__(message)

        sys.modules["gotrue.errors"].AuthApiError = MockAuthApiError
        yield MockAuthApiError


@pytest.fixture
def mock_supabase_client():
    """Create a mock SupabaseClient."""
    client = MagicMock()
    client.client = MagicMock()
    client.client.auth = MagicMock()
    return client


@pytest.fixture
def valid_user_response():
    """Create a valid user response."""
    response = MagicMock()
    response.user = MagicMock()
    response.user.id = "test-user-123"
    return response


class TestGetCurrentUser:
    """Tests for get_current_user function."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user_id(
        self, mock_modules, mock_supabase_client, valid_user_response
    ):
        """Test that valid token returns user ID string."""
        from core.auth import get_current_user

        # Setup
        mock_supabase_client.client.auth.get_user = AsyncMock(
            return_value=valid_user_response
        )

        # Execute
        result = await get_current_user(
            token="valid-jwt-token", supabase_client=mock_supabase_client
        )

        # Assert
        assert result == "test-user-123"
        mock_supabase_client.client.auth.get_user.assert_called_once_with(
            "valid-jwt-token"
        )

    @pytest.mark.asyncio
    async def test_empty_token_raises_401(self, mock_modules, mock_supabase_client):
        """Test that empty token raises 401 Unauthorized."""
        from core.auth import get_current_user

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="", supabase_client=mock_supabase_client)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Could not validate credentials"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self, mock_modules, mock_supabase_client):
        """Test that invalid token raises 401 when AuthException occurs."""
        from core.auth import get_current_user

        # Setup
        AuthException = mock_modules
        mock_supabase_client.client.auth.get_user = AsyncMock(
            side_effect=AuthException("Invalid token")
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="invalid-token", supabase_client=mock_supabase_client
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_no_user_in_response_raises_401(
        self, mock_modules, mock_supabase_client
    ):
        """Test that response without user raises 401."""
        from core.auth import get_current_user

        # Setup - response with no user
        invalid_response = MagicMock()
        invalid_response.user = None
        mock_supabase_client.client.auth.get_user = AsyncMock(
            return_value=invalid_response
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="valid-token-no-user", supabase_client=mock_supabase_client
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_unexpected_error_raises_401(
        self, mock_modules, mock_supabase_client
    ):
        """Test that unexpected errors are caught and raise 401."""
        from core.auth import get_current_user

        # Setup
        mock_supabase_client.client.auth.get_user = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="valid-token", supabase_client=mock_supabase_client
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetOptionalUser:
    """Tests for get_optional_user function."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user_id(
        self, mock_modules, mock_supabase_client, valid_user_response
    ):
        """Test that valid token returns user ID string."""
        from core.auth import get_optional_user

        # Setup
        mock_supabase_client.client.auth.get_user = AsyncMock(
            return_value=valid_user_response
        )

        # Execute
        result = await get_optional_user(
            token="valid-jwt-token", supabase_client=mock_supabase_client
        )

        # Assert
        assert result == "test-user-123"

    @pytest.mark.asyncio
    async def test_empty_token_returns_none(self, mock_modules, mock_supabase_client):
        """Test that empty token returns None without calling Supabase."""
        from core.auth import get_optional_user

        # Execute
        result = await get_optional_user(token="", supabase_client=mock_supabase_client)

        # Assert
        assert result is None
        mock_supabase_client.client.auth.get_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_token_returns_none(self, mock_modules, mock_supabase_client):
        """Test that invalid token returns None when AuthException occurs."""
        from core.auth import get_optional_user

        # Setup
        AuthException = mock_modules
        mock_supabase_client.client.auth.get_user = AsyncMock(
            side_effect=AuthException("Invalid token")
        )

        # Execute
        result = await get_optional_user(
            token="invalid-token", supabase_client=mock_supabase_client
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_no_user_in_response_returns_none(
        self, mock_modules, mock_supabase_client
    ):
        """Test that response without user returns None."""
        from core.auth import get_optional_user

        # Setup - response with no user
        invalid_response = MagicMock()
        invalid_response.user = None
        mock_supabase_client.client.auth.get_user = AsyncMock(
            return_value=invalid_response
        )

        # Execute
        result = await get_optional_user(
            token="valid-token-no-user", supabase_client=mock_supabase_client
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_unexpected_error_returns_none(
        self, mock_modules, mock_supabase_client
    ):
        """Test that unexpected errors return None."""
        from core.auth import get_optional_user

        # Setup
        mock_supabase_client.client.auth.get_user = AsyncMock(
            side_effect=Exception("Network timeout")
        )

        # Execute
        result = await get_optional_user(
            token="valid-token", supabase_client=mock_supabase_client
        )

        # Assert
        assert result is None


@pytest.mark.unit
class TestOAuth2Scheme:
    """Tests for OAuth2PasswordBearer configuration."""

    def test_oauth2_scheme_configuration(self, mock_modules):
        """Test that OAuth2PasswordBearer is configured correctly."""
        from core.auth import oauth2_scheme

        assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"
        assert oauth2_scheme.tokenUrl == "/auth/token"
        assert oauth2_scheme.auto_error is True
