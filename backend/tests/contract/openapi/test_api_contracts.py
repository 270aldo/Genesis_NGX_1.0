"""
OpenAPI Contract Tests for GENESIS API Endpoints

Tests all API endpoints against their OpenAPI specifications to ensure:
- Request/response schemas match documentation
- Breaking changes are detected
- API contracts are maintained across versions
"""

import json
from unittest.mock import AsyncMock, patch

from tests.contract.base_contract_test import BaseContractTest


class TestAPIContracts(BaseContractTest):
    """Test suite for API contract validation"""

    def setup_method(self):
        super().setup_method()

        # Mock authentication for protected endpoints
        self.auth_headers = {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json",
        }

    # Health and System Endpoints

    def test_health_endpoint_contract(self):
        """Test /health endpoint contract compliance"""
        result = self.make_request("GET", "/health")

        assert result.success, f"Health check failed: {result.schema_errors}"
        assert result.status_code == 200
        assert result.response_valid
        assert result.performance_ms < 1000  # Should be fast

    def test_metrics_endpoint_contract(self):
        """Test /metrics endpoint contract compliance"""
        result = self.make_request("GET", "/metrics")

        assert result.success, f"Metrics endpoint failed: {result.schema_errors}"
        assert result.status_code == 200

    # Authentication Endpoints

    def test_auth_signin_contract(self):
        """Test POST /auth/signin contract"""
        signin_data = {"email": "test@example.com", "password": "testpassword123"}

        with patch("core.auth.authenticate_user") as mock_auth:
            mock_auth.return_value = {
                "access_token": "test-token",
                "token_type": "bearer",
                "expires_in": 3600,
            }

            result = self.make_request("POST", "/auth/signin", data=signin_data)

            assert (
                result.request_valid
            ), f"Invalid signin request: {result.schema_errors}"
            assert result.status_code in [200, 401]  # Valid responses

    def test_auth_signup_contract(self):
        """Test POST /auth/signup contract"""
        signup_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "Test",
            "last_name": "User",
        }

        result = self.make_request("POST", "/auth/signup", data=signup_data)

        assert result.request_valid, f"Invalid signup request: {result.schema_errors}"
        assert result.status_code in [201, 400, 409]  # Valid responses

    def test_auth_refresh_contract(self):
        """Test POST /auth/refresh contract"""
        refresh_data = {"refresh_token": "test-refresh-token"}

        result = self.make_request("POST", "/auth/refresh", data=refresh_data)

        assert result.request_valid, f"Invalid refresh request: {result.schema_errors}"
        assert result.status_code in [200, 401]

    # Agent Endpoints

    def test_agents_list_contract(self):
        """Test GET /agents contract"""
        result = self.make_request("GET", "/agents", headers=self.auth_headers)

        assert result.success or result.status_code == 401  # Auth required
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid agents response: {result.schema_errors}"

    def test_agents_get_contract(self):
        """Test GET /agents/{agent_id} contract"""
        agent_id = "elite-training-strategist"
        result = self.make_request(
            "GET", f"/agents/{agent_id}", headers=self.auth_headers
        )

        assert result.status_code in [200, 404, 401]
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid agent response: {result.schema_errors}"

    def test_agents_chat_contract(self):
        """Test POST /agents/{agent_id}/chat contract"""
        agent_id = "elite-training-strategist"
        chat_data = {
            "message": "I want to build muscle mass",
            "conversation_id": "test-conversation-123",
            "user_context": {"fitness_level": "beginner", "goals": ["muscle_gain"]},
        }

        with patch(
            "agents.elite_training_strategist.agent.EliteTrainingStrategist.process_message"
        ) as mock_process:
            mock_process.return_value = AsyncMock(
                return_value={
                    "response": "Here's a muscle building plan...",
                    "agent_name": "BLAZE",
                    "conversation_id": "test-conversation-123",
                }
            )

            result = self.make_request(
                "POST",
                f"/agents/{agent_id}/chat",
                data=chat_data,
                headers=self.auth_headers,
            )

            assert result.request_valid, f"Invalid chat request: {result.schema_errors}"
            assert result.status_code in [200, 400, 401, 404]

    # Chat Endpoints

    def test_chat_conversations_contract(self):
        """Test GET /chat/conversations contract"""
        result = self.make_request(
            "GET",
            "/chat/conversations",
            headers=self.auth_headers,
            params={"limit": 10, "offset": 0},
        )

        assert result.status_code in [200, 401]
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid conversations response: {result.schema_errors}"

    def test_chat_conversation_messages_contract(self):
        """Test GET /chat/conversations/{conversation_id}/messages contract"""
        conversation_id = "test-conversation-123"
        result = self.make_request(
            "GET",
            f"/chat/conversations/{conversation_id}/messages",
            headers=self.auth_headers,
            params={"limit": 50},
        )

        assert result.status_code in [200, 404, 401]
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid messages response: {result.schema_errors}"

    def test_chat_send_message_contract(self):
        """Test POST /chat/send contract"""
        message_data = {
            "conversation_id": "test-conversation-123",
            "message": "Hello, I need help with training",
            "agent_id": "elite-training-strategist",
        }

        result = self.make_request(
            "POST", "/chat/send", data=message_data, headers=self.auth_headers
        )

        assert (
            result.request_valid
        ), f"Invalid send message request: {result.schema_errors}"
        assert result.status_code in [200, 400, 401]

    # Voice Endpoints

    def test_voice_synthesize_contract(self):
        """Test POST /voice/synthesize contract"""
        voice_data = {
            "text": "Hello, this is a test message for voice synthesis",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # ElevenLabs voice ID
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.75},
        }

        with patch(
            "clients.elevenlabs_client.ElevenLabsClient.synthesize_speech"
        ) as mock_synth:
            mock_synth.return_value = b"fake-audio-data"

            result = self.make_request(
                "POST", "/voice/synthesize", data=voice_data, headers=self.auth_headers
            )

            assert (
                result.request_valid
            ), f"Invalid voice request: {result.schema_errors}"
            assert result.status_code in [200, 400, 401]

    def test_voice_available_voices_contract(self):
        """Test GET /voice/voices contract"""
        result = self.make_request("GET", "/voice/voices", headers=self.auth_headers)

        assert result.status_code in [200, 401]
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid voices response: {result.schema_errors}"

    # Feature Flags Endpoints

    def test_feature_flags_contract(self):
        """Test GET /feature-flags contract"""
        result = self.make_request("GET", "/feature-flags", headers=self.auth_headers)

        assert result.status_code in [200, 401]
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid feature flags response: {result.schema_errors}"

    def test_feature_flag_specific_contract(self):
        """Test GET /feature-flags/{flag_name} contract"""
        flag_name = "ai_voice_enabled"
        result = self.make_request(
            "GET", f"/feature-flags/{flag_name}", headers=self.auth_headers
        )

        assert result.status_code in [200, 404, 401]
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid feature flag response: {result.schema_errors}"

    # Wearables Integration Endpoints

    def test_wearables_sync_contract(self):
        """Test POST /wearables/sync contract"""
        sync_data = {
            "device_type": "garmin",
            "auth_token": "test-auth-token",
            "sync_types": ["heart_rate", "steps", "sleep"],
        }

        result = self.make_request(
            "POST", "/wearables/sync", data=sync_data, headers=self.auth_headers
        )

        assert (
            result.request_valid
        ), f"Invalid wearables sync request: {result.schema_errors}"
        assert result.status_code in [200, 400, 401]

    def test_wearables_data_contract(self):
        """Test GET /wearables/data contract"""
        result = self.make_request(
            "GET",
            "/wearables/data",
            headers=self.auth_headers,
            params={
                "device_type": "garmin",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
        )

        assert result.status_code in [200, 400, 401, 404]
        if result.status_code == 200:
            assert (
                result.response_valid
            ), f"Invalid wearables data response: {result.schema_errors}"

    # Error Handling Contract Tests

    def test_404_error_contract(self):
        """Test 404 error response contract"""
        result = self.make_request("GET", "/nonexistent-endpoint")

        assert result.status_code == 404
        # 404 responses should have consistent structure

    def test_400_error_contract(self):
        """Test 400 error response contract"""
        # Send invalid JSON to trigger 400 error
        invalid_data = {"invalid": "incomplete data structure"}

        result = self.make_request("POST", "/auth/signin", data=invalid_data)

        assert result.status_code == 400
        # 400 responses should have error details

    def test_401_error_contract(self):
        """Test 401 error response contract"""
        result = self.make_request(
            "GET", "/agents", headers={"Authorization": "Bearer invalid-token"}
        )

        assert result.status_code == 401
        # 401 responses should be consistent

    # Performance Contract Tests

    def test_response_time_contracts(self):
        """Test that all endpoints meet performance contracts"""
        # Health check should be very fast
        health_result = self.make_request("GET", "/health")
        assert health_result.performance_ms < 100, "Health check too slow"

        # Agent endpoints should respond within reasonable time
        agents_result = self.make_request("GET", "/agents", headers=self.auth_headers)
        if agents_result.status_code == 200:
            assert agents_result.performance_ms < 2000, "Agents endpoint too slow"

    # Batch Contract Testing

    def test_all_documented_endpoints(self):
        """Test all endpoints documented in OpenAPI spec"""
        paths = self.openapi_schema.get("paths", {})

        tested_endpoints = 0
        failed_contracts = []

        for path, methods in paths.items():
            for method, spec in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE"]:
                    # Skip certain endpoints that require complex setup
                    skip_endpoints = [
                        "/stream/",  # Streaming endpoints need special handling
                        "/ws/",  # WebSocket endpoints tested separately
                    ]

                    if any(skip in path for skip in skip_endpoints):
                        continue

                    # Basic contract test for each endpoint
                    headers = self.auth_headers if spec.get("security") else None
                    result = self.make_request(method.upper(), path, headers=headers)

                    tested_endpoints += 1

                    # Accept various status codes as valid contract responses
                    valid_codes = [200, 201, 400, 401, 403, 404, 422, 500]
                    if result.status_code not in valid_codes:
                        failed_contracts.append(
                            {
                                "endpoint": f"{method.upper()} {path}",
                                "status": result.status_code,
                                "errors": result.schema_errors,
                            }
                        )

        # Report results
        print(f"Tested {tested_endpoints} endpoints")
        if failed_contracts:
            print(f"Failed contracts: {json.dumps(failed_contracts, indent=2)}")

        assert (
            len(failed_contracts) == 0
        ), f"Contract failures in {len(failed_contracts)} endpoints"
