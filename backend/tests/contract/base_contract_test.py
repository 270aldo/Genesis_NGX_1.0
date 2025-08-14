"""
Base Contract Test Class for GENESIS API Testing

Provides common functionality for contract testing including:
- OpenAPI schema validation
- Request/response validation
- A2A communication testing
- WebSocket contract validation
"""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import websockets
from fastapi.testclient import TestClient
from websockets.exceptions import WebSocketException

from app.main import app
from core.settings import get_settings


@dataclass
class ContractTestResult:
    """Result of a contract test execution"""

    endpoint: str
    method: str
    status_code: int
    request_valid: bool
    response_valid: bool
    schema_errors: List[str]
    performance_ms: float
    success: bool


@dataclass
class A2AMessage:
    """A2A message structure for testing"""

    agent_from: str
    agent_to: str
    message_type: str
    payload: Dict[str, Any]
    correlation_id: str
    timestamp: float


class BaseContractTest:
    """
    Base class for all contract tests in GENESIS platform

    Provides utilities for:
    - API endpoint testing
    - Schema validation
    - A2A communication testing
    - WebSocket testing
    - Performance validation
    """

    def __init__(self):
        self.app = app
        self.client = TestClient(app)
        self.settings = get_settings()
        self.test_results: List[ContractTestResult] = []

        # Load OpenAPI schema for validation
        self.openapi_schema = self.app.openapi()

        # Test data directory
        self.test_data_dir = Path(__file__).parent / "data"
        self.test_data_dir.mkdir(exist_ok=True)

    def setup_method(self):
        """Setup for each test method"""
        self.test_results.clear()

    def teardown_method(self):
        """Cleanup after each test method"""
        # Generate test report if there were failures
        failures = [r for r in self.test_results if not r.success]
        if failures:
            self._generate_failure_report(failures)

    # OpenAPI Contract Testing

    def validate_request_schema(
        self, endpoint: str, method: str, request_data: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate request data against OpenAPI schema

        Args:
            endpoint: API endpoint path
            method: HTTP method
            request_data: Request payload to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            # Get endpoint schema from OpenAPI spec
            paths = self.openapi_schema.get("paths", {})
            endpoint_schema = paths.get(endpoint, {}).get(method.lower(), {})

            if not endpoint_schema:
                errors.append(f"No schema found for {method} {endpoint}")
                return False, errors

            # Validate request body if present
            request_body_schema = endpoint_schema.get("requestBody", {})
            if request_body_schema and request_data:
                content_schemas = request_body_schema.get("content", {})
                json_schema = content_schemas.get("application/json", {}).get(
                    "schema", {}
                )

                if json_schema:
                    validation_errors = self._validate_json_schema(
                        request_data, json_schema
                    )
                    errors.extend(validation_errors)

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")
            return False, errors

    def validate_response_schema(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_data: Dict[str, Any],
    ) -> tuple[bool, List[str]]:
        """
        Validate response data against OpenAPI schema

        Args:
            endpoint: API endpoint path
            method: HTTP method
            status_code: HTTP response status code
            response_data: Response payload to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            # Get response schema from OpenAPI spec
            paths = self.openapi_schema.get("paths", {})
            endpoint_schema = paths.get(endpoint, {}).get(method.lower(), {})

            if not endpoint_schema:
                errors.append(f"No schema found for {method} {endpoint}")
                return False, errors

            # Get response schema for specific status code
            responses = endpoint_schema.get("responses", {})
            response_schema = responses.get(str(status_code), {})

            if not response_schema:
                # Try default response schema
                response_schema = responses.get("default", {})

            if not response_schema:
                errors.append(f"No response schema found for {status_code}")
                return False, errors

            # Validate response content
            content_schemas = response_schema.get("content", {})
            json_schema = content_schemas.get("application/json", {}).get("schema", {})

            if json_schema and response_data:
                validation_errors = self._validate_json_schema(
                    response_data, json_schema
                )
                errors.extend(validation_errors)

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Response schema validation error: {str(e)}")
            return False, errors

    def _validate_json_schema(
        self, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[str]:
        """
        Basic JSON schema validation
        In production, would use jsonschema library
        """
        errors = []

        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Check field types
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type:
                    actual_type = self._get_json_type(value)
                    if actual_type != expected_type:
                        errors.append(
                            f"Field {field}: expected {expected_type}, got {actual_type}"
                        )

        return errors

    def _get_json_type(self, value: Any) -> str:
        """Get JSON type string for Python value"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        elif value is None:
            return "null"
        else:
            return "unknown"

    # API Testing Utilities

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> ContractTestResult:
        """
        Make HTTP request and validate contract

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request payload
            headers: Request headers
            params: URL parameters

        Returns:
            ContractTestResult with validation results
        """
        import time

        start_time = time.time()

        # Validate request schema
        request_valid, request_errors = self.validate_request_schema(
            endpoint, method, data or {}
        )

        # Make request
        try:
            response = self.client.request(
                method=method, url=endpoint, json=data, headers=headers, params=params
            )

            response_data = {}
            try:
                response_data = response.json()
            except:
                # Response might not be JSON
                pass

            # Validate response schema
            response_valid, response_errors = self.validate_response_schema(
                endpoint, method, response.status_code, response_data
            )

            performance_ms = (time.time() - start_time) * 1000

            result = ContractTestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                request_valid=request_valid,
                response_valid=response_valid,
                schema_errors=request_errors + response_errors,
                performance_ms=performance_ms,
                success=request_valid
                and response_valid
                and 200 <= response.status_code < 400,
            )

            self.test_results.append(result)
            return result

        except Exception as e:
            result = ContractTestResult(
                endpoint=endpoint,
                method=method,
                status_code=500,
                request_valid=request_valid,
                response_valid=False,
                schema_errors=request_errors + [f"Request failed: {str(e)}"],
                performance_ms=(time.time() - start_time) * 1000,
                success=False,
            )

            self.test_results.append(result)
            return result

    # A2A Contract Testing

    async def send_a2a_message(
        self, message: A2AMessage, timeout: float = 10.0
    ) -> Dict[str, Any]:
        """
        Send A2A message and validate contract

        Args:
            message: A2A message to send
            timeout: Response timeout in seconds

        Returns:
            Response from target agent
        """
        # This would integrate with actual A2A infrastructure
        # For now, simulate A2A communication

        # Validate message structure
        if not all([message.agent_from, message.agent_to, message.message_type]):
            raise ValueError("Invalid A2A message structure")

        # Simulate sending message via A2A server
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.api_base_url}/a2a/send",
                json={
                    "from_agent": message.agent_from,
                    "to_agent": message.agent_to,
                    "message_type": message.message_type,
                    "payload": message.payload,
                    "correlation_id": message.correlation_id,
                    "timestamp": message.timestamp,
                },
                timeout=timeout,
            )

            if response.status_code != 200:
                raise Exception(f"A2A message failed: {response.status_code}")

            return response.json()

    async def validate_a2a_response(
        self, response: Dict[str, Any], expected_message_type: str
    ) -> tuple[bool, List[str]]:
        """
        Validate A2A response structure

        Args:
            response: A2A response to validate
            expected_message_type: Expected message type

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = ["agent_from", "message_type", "payload", "timestamp"]
        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required A2A field: {field}")

        # Validate message type
        if response.get("message_type") != expected_message_type:
            errors.append(
                f"Expected message type {expected_message_type}, got {response.get('message_type')}"
            )

        # Validate payload structure
        payload = response.get("payload", {})
        if not isinstance(payload, dict):
            errors.append("Payload must be a dictionary")

        return len(errors) == 0, errors

    # WebSocket Contract Testing

    async def test_websocket_contract(
        self, endpoint: str, test_messages: List[Dict[str, Any]], timeout: float = 10.0
    ) -> tuple[bool, List[str]]:
        """
        Test WebSocket contract compliance

        Args:
            endpoint: WebSocket endpoint
            test_messages: Messages to send for testing
            timeout: Connection timeout

        Returns:
            Tuple of (success, list_of_errors)
        """
        errors = []

        try:
            # Construct WebSocket URL
            ws_url = f"ws://localhost:8000{endpoint}"

            async with websockets.connect(ws_url) as websocket:
                # Test connection establishment
                await websocket.ping()

                # Test message sending and receiving
                for message in test_messages:
                    await websocket.send(json.dumps(message))

                    # Wait for response
                    try:
                        response = await asyncio.wait_for(
                            websocket.recv(), timeout=timeout
                        )

                        # Validate response format
                        response_data = json.loads(response)
                        if not isinstance(response_data, dict):
                            errors.append("WebSocket response must be JSON object")

                    except asyncio.TimeoutError:
                        errors.append(
                            f"WebSocket response timeout for message: {message}"
                        )
                    except json.JSONDecodeError:
                        errors.append("WebSocket response is not valid JSON")

        except WebSocketException as e:
            errors.append(f"WebSocket connection failed: {str(e)}")
        except Exception as e:
            errors.append(f"WebSocket test failed: {str(e)}")

        return len(errors) == 0, errors

    # Reporting and Utilities

    def _generate_failure_report(self, failures: List[ContractTestResult]):
        """Generate detailed failure report"""
        report_path = self.test_data_dir / "contract_failures.json"

        failure_data = []
        for failure in failures:
            failure_data.append(
                {
                    "endpoint": failure.endpoint,
                    "method": failure.method,
                    "status_code": failure.status_code,
                    "request_valid": failure.request_valid,
                    "response_valid": failure.response_valid,
                    "schema_errors": failure.schema_errors,
                    "performance_ms": failure.performance_ms,
                }
            )

        with open(report_path, "w") as f:
            json.dump(
                {
                    "timestamp": time.time(),
                    "total_failures": len(failures),
                    "failures": failure_data,
                },
                f,
                indent=2,
            )

        print(f"Contract test failure report written to: {report_path}")

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests

        avg_performance = 0
        if self.test_results:
            avg_performance = (
                sum(r.performance_ms for r in self.test_results) / total_tests
            )

        return {
            "total_tests": total_tests,
            "successful": successful_tests,
            "failed": failed_tests,
            "success_rate": (
                (successful_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "average_response_time_ms": avg_performance,
            "slowest_endpoint": max(
                self.test_results, key=lambda r: r.performance_ms, default=None
            ),
            "most_errors": max(
                self.test_results, key=lambda r: len(r.schema_errors), default=None
            ),
        }
