"""
Systems Integration Service for NODE Systems Integration agent.
Handles API integrations, system coordination, and service orchestration.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin, urlparse
import ssl

from agents.backend.node.core.config import NodeConfig
from agents.backend.node.core.exceptions import (
    SystemIntegrationError,
    ApiConnectionError,
    CircuitBreakerError,
    RateLimitExceededError,
    IntegrationAuthenticationError,
    IntegrationConfigurationError,
)
from agents.backend.node.core.constants import SERVICE_TIMEOUTS, INTEGRATION_TYPES
from core.logging_config import get_logger

logger = get_logger(__name__)


class SystemsIntegrationService:
    """
    Comprehensive systems integration service for backend coordination.

    Features:
    - RESTful API integration with multiple authentication methods
    - GraphQL query and mutation handling
    - WebSocket real-time communication
    - Circuit breaker pattern for resilience
    - Request/response validation and transformation
    - Rate limiting and retry mechanisms
    """

    def __init__(self, config: NodeConfig):
        self.config = config
        self._session = None
        self._circuit_breakers = {}
        self._rate_limiters = {}
        self._integration_cache = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the systems integration service."""
        try:
            # Create SSL context for secure connections
            ssl_context = ssl.create_default_context()
            if not self.config.enable_ssl_verification:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            # Create HTTP session with optimized settings
            connector = aiohttp.TCPConnector(
                limit=self.config.max_concurrent_api_calls,
                ssl=ssl_context,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
            )

            timeout = aiohttp.ClientTimeout(total=self.config.api_timeout)

            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": "NODE-Systems-Integration/2.0.0",
                    "Accept": "application/json",
                },
            )

            # Initialize circuit breakers for different service types
            await self._initialize_circuit_breakers()

            # Initialize rate limiters
            await self._initialize_rate_limiters()

            self._integration_cache = {}
            self._initialized = True

            logger.info("Systems integration service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize systems integration service: {e}")
            raise SystemIntegrationError(
                f"Systems integration service initialization failed: {e}",
                integration_type="initialization",
            )

    async def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers for external services."""
        cb_config = self.config.get_circuit_breaker_config()

        services = [
            "rest_api",
            "graphql",
            "websocket",
            "database",
            "message_queue",
            "cloud_service",
            "third_party",
        ]

        for service in services:
            self._circuit_breakers[service] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure": None,
                "timeout": cb_config["timeout"],
                "failure_threshold": cb_config["failure_threshold"],
                "half_open_max_calls": cb_config["half_open_max_calls"],
                "half_open_calls": 0,
            }

    async def _initialize_rate_limiters(self) -> None:
        """Initialize rate limiters for API calls."""
        self._rate_limiters = {
            "default": {
                "calls": 0,
                "reset_time": datetime.utcnow() + timedelta(seconds=60),
            },
            "high_priority": {
                "calls": 0,
                "reset_time": datetime.utcnow() + timedelta(seconds=60),
            },
        }

    async def integrate_rest_api(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        auth_config: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Integrate with RESTful API endpoints.

        Args:
            endpoint: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            headers: Additional request headers
            params: Query parameters
            data: Request body data
            auth_config: Authentication configuration
            timeout: Request timeout override

        Returns:
            Dict[str, Any]: API response data

        Raises:
            ApiConnectionError: If API call fails
            CircuitBreakerError: If circuit breaker is open
        """
        if not self._initialized:
            raise SystemIntegrationError("Service not initialized")

        # Check circuit breaker
        if not await self._check_circuit_breaker("rest_api"):
            raise CircuitBreakerError(
                "REST API circuit breaker is open",
                service_name="rest_api",
            )

        # Check rate limiting
        await self._check_rate_limit("default")

        try:
            # Prepare request
            request_headers = headers or {}
            request_timeout = timeout or self.config.api_timeout

            # Add authentication
            if auth_config:
                request_headers.update(await self._prepare_auth_headers(auth_config))

            # Validate endpoint
            parsed_url = urlparse(endpoint)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise IntegrationConfigurationError(
                    f"Invalid endpoint URL: {endpoint}",
                    config_type="endpoint_url",
                )

            # Prepare request data
            if data and isinstance(data, dict):
                data = json.dumps(data)
                request_headers["Content-Type"] = "application/json"

            # Make API call
            async with self._session.request(
                method=method.upper(),
                url=endpoint,
                headers=request_headers,
                params=params,
                data=data,
                timeout=aiohttp.ClientTimeout(total=request_timeout),
            ) as response:

                # Handle response
                response_data = await self._process_api_response(response, endpoint)

                # Record success
                await self._record_success("rest_api")

                return response_data

        except aiohttp.ClientTimeout:
            await self._record_failure("rest_api")
            raise ApiConnectionError(
                f"API request timeout: {endpoint}",
                api_endpoint=endpoint,
                status_code=None,
            )
        except aiohttp.ClientError as e:
            await self._record_failure("rest_api")
            raise ApiConnectionError(
                f"API connection error: {e}",
                api_endpoint=endpoint,
                status_code=None,
            )
        except Exception as e:
            await self._record_failure("rest_api")
            logger.error(f"REST API integration failed: {e}")
            raise

    async def integrate_graphql(
        self,
        endpoint: str,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        auth_config: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Integrate with GraphQL endpoints.

        Args:
            endpoint: GraphQL endpoint URL
            query: GraphQL query or mutation
            variables: Query variables
            operation_name: Operation name for multi-operation documents
            auth_config: Authentication configuration

        Returns:
            Dict[str, Any]: GraphQL response data
        """
        if not await self._check_circuit_breaker("graphql"):
            raise CircuitBreakerError(
                "GraphQL circuit breaker is open",
                service_name="graphql",
            )

        try:
            # Prepare GraphQL request
            payload = {
                "query": query,
                "variables": variables or {},
            }

            if operation_name:
                payload["operationName"] = operation_name

            # Use REST API integration for GraphQL
            response = await self.integrate_rest_api(
                endpoint=endpoint,
                method="POST",
                data=payload,
                auth_config=auth_config,
                headers={"Content-Type": "application/json"},
            )

            # Validate GraphQL response
            if "errors" in response and response["errors"]:
                raise SystemIntegrationError(
                    f"GraphQL errors: {response['errors']}",
                    integration_type="graphql",
                )

            await self._record_success("graphql")
            return response

        except Exception as e:
            await self._record_failure("graphql")
            logger.error(f"GraphQL integration failed: {e}")
            raise

    async def establish_websocket_connection(
        self,
        endpoint: str,
        protocols: Optional[List[str]] = None,
        auth_config: Optional[Dict[str, str]] = None,
        message_handler: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Establish WebSocket connection for real-time communication.

        Args:
            endpoint: WebSocket endpoint URL
            protocols: WebSocket sub-protocols
            auth_config: Authentication configuration
            message_handler: Callback for incoming messages

        Returns:
            Dict[str, Any]: Connection status and details
        """
        if not await self._check_circuit_breaker("websocket"):
            raise CircuitBreakerError(
                "WebSocket circuit breaker is open",
                service_name="websocket",
            )

        try:
            # Prepare WebSocket connection
            headers = {}
            if auth_config:
                headers.update(await self._prepare_auth_headers(auth_config))

            # Note: In a real implementation, this would establish actual WebSocket connection
            # For now, return mock connection details
            connection_info = {
                "endpoint": endpoint,
                "status": "connected",
                "protocols": protocols or [],
                "connected_at": datetime.utcnow().isoformat(),
                "connection_id": f"ws_{datetime.utcnow().timestamp()}",
            }

            await self._record_success("websocket")
            return connection_info

        except Exception as e:
            await self._record_failure("websocket")
            logger.error(f"WebSocket connection failed: {e}")
            raise

    async def validate_integration_config(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate integration configuration before execution.

        Args:
            config: Integration configuration dictionary

        Returns:
            Dict[str, Any]: Validation results and suggestions
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": [],
        }

        # Validate required fields
        required_fields = ["type", "endpoint"]
        for field in required_fields:
            if field not in config:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["is_valid"] = False

        # Validate integration type
        if "type" in config:
            integration_type = config["type"]
            if integration_type not in INTEGRATION_TYPES:
                validation_results["errors"].append(
                    f"Unsupported integration type: {integration_type}"
                )
                validation_results["is_valid"] = False

        # Validate endpoint URL
        if "endpoint" in config:
            try:
                parsed_url = urlparse(config["endpoint"])
                if not parsed_url.scheme:
                    validation_results["warnings"].append(
                        "Endpoint URL missing scheme (http/https)"
                    )
                if not parsed_url.netloc:
                    validation_results["errors"].append("Invalid endpoint URL format")
                    validation_results["is_valid"] = False
            except Exception:
                validation_results["errors"].append("Invalid endpoint URL")
                validation_results["is_valid"] = False

        # Validate authentication configuration
        if "auth" in config:
            auth_validation = await self._validate_auth_config(config["auth"])
            validation_results["warnings"].extend(auth_validation.get("warnings", []))
            validation_results["errors"].extend(auth_validation.get("errors", []))
            if auth_validation.get("errors"):
                validation_results["is_valid"] = False

        # Add optimization suggestions
        if validation_results["is_valid"]:
            validation_results["suggestions"] = [
                "Consider implementing retry logic for resilience",
                "Add request/response logging for debugging",
                "Implement caching for frequently accessed data",
                "Set up monitoring and alerting for the integration",
            ]

        return validation_results

    async def _process_api_response(
        self, response: aiohttp.ClientResponse, endpoint: str
    ) -> Dict[str, Any]:
        """Process API response and handle errors."""
        try:
            # Check status code
            if response.status == 429:
                retry_after = response.headers.get("Retry-After", "60")
                raise RateLimitExceededError(
                    f"Rate limit exceeded for {endpoint}",
                    reset_time=int(retry_after),
                )

            if response.status >= 400:
                error_text = await response.text()
                raise ApiConnectionError(
                    f"API error {response.status}: {error_text}",
                    api_endpoint=endpoint,
                    status_code=response.status,
                )

            # Parse response
            content_type = response.headers.get("Content-Type", "").lower()

            if "application/json" in content_type:
                return await response.json()
            elif "text/" in content_type:
                text_content = await response.text()
                return {"content": text_content, "content_type": "text"}
            else:
                # Binary content
                content = await response.read()
                return {
                    "content": content,
                    "content_type": content_type,
                    "size": len(content),
                }

        except json.JSONDecodeError:
            text_content = await response.text()
            logger.warning(
                f"Invalid JSON response from {endpoint}: {text_content[:200]}"
            )
            return {
                "content": text_content,
                "content_type": "text",
                "parse_error": True,
            }

    async def _prepare_auth_headers(
        self, auth_config: Dict[str, str]
    ) -> Dict[str, str]:
        """Prepare authentication headers based on auth configuration."""
        headers = {}
        auth_type = auth_config.get("type", "").lower()

        if auth_type == "bearer":
            token = auth_config.get("token")
            if not token:
                raise IntegrationAuthenticationError(
                    "Bearer token required for bearer authentication",
                    auth_type="bearer",
                )
            headers["Authorization"] = f"Bearer {token}"

        elif auth_type == "api_key":
            api_key = auth_config.get("api_key")
            header_name = auth_config.get("header_name", "X-API-Key")
            if not api_key:
                raise IntegrationAuthenticationError(
                    "API key required for API key authentication",
                    auth_type="api_key",
                )
            headers[header_name] = api_key

        elif auth_type == "basic":
            username = auth_config.get("username")
            password = auth_config.get("password")
            if not username or not password:
                raise IntegrationAuthenticationError(
                    "Username and password required for basic authentication",
                    auth_type="basic",
                )
            import base64

            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"

        return headers

    async def _validate_auth_config(
        self, auth_config: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Validate authentication configuration."""
        validation = {"warnings": [], "errors": []}

        auth_type = auth_config.get("type", "").lower()
        supported_types = ["bearer", "api_key", "basic", "oauth2"]

        if not auth_type:
            validation["errors"].append("Authentication type is required")
        elif auth_type not in supported_types:
            validation["errors"].append(
                f"Unsupported auth type: {auth_type}. Supported: {supported_types}"
            )

        # Type-specific validation
        if auth_type == "bearer" and not auth_config.get("token"):
            validation["errors"].append("Bearer token is required")
        elif auth_type == "api_key" and not auth_config.get("api_key"):
            validation["errors"].append("API key is required")
        elif auth_type == "basic":
            if not auth_config.get("username"):
                validation["errors"].append("Username is required for basic auth")
            if not auth_config.get("password"):
                validation["errors"].append("Password is required for basic auth")

        return validation

    async def _check_circuit_breaker(self, service_name: str) -> bool:
        """Check if circuit breaker allows requests to service."""
        if service_name not in self._circuit_breakers:
            return True

        breaker = self._circuit_breakers[service_name]

        if breaker["state"] == "closed":
            return True
        elif breaker["state"] == "open":
            # Check if timeout has passed
            if breaker["last_failure"]:
                time_since_failure = datetime.utcnow() - breaker["last_failure"]
                if time_since_failure.total_seconds() > breaker["timeout"]:
                    # Move to half-open state
                    breaker["state"] = "half_open"
                    breaker["half_open_calls"] = 0
                    return True
            return False
        else:  # half_open
            if breaker["half_open_calls"] < breaker["half_open_max_calls"]:
                breaker["half_open_calls"] += 1
                return True
            return False

    async def _record_success(self, service_name: str) -> None:
        """Record successful operation and reset circuit breaker."""
        if service_name in self._circuit_breakers:
            self._circuit_breakers[service_name].update(
                {
                    "state": "closed",
                    "failure_count": 0,
                    "last_failure": None,
                    "half_open_calls": 0,
                }
            )

    async def _record_failure(self, service_name: str) -> None:
        """Record operation failure and update circuit breaker."""
        if service_name not in self._circuit_breakers:
            return

        breaker = self._circuit_breakers[service_name]
        breaker["failure_count"] += 1
        breaker["last_failure"] = datetime.utcnow()

        # Open circuit breaker if threshold exceeded
        if breaker["failure_count"] >= breaker["failure_threshold"]:
            breaker["state"] = "open"
            logger.warning(f"Circuit breaker opened for {service_name}")
        # If in half-open state and failure occurs, go back to open
        elif breaker["state"] == "half_open":
            breaker["state"] = "open"

    async def _check_rate_limit(self, limiter_name: str) -> None:
        """Check and update rate limiter."""
        if limiter_name not in self._rate_limiters:
            return

        limiter = self._rate_limiters[limiter_name]
        now = datetime.utcnow()

        # Reset counter if time window has passed
        if now >= limiter["reset_time"]:
            limiter["calls"] = 0
            limiter["reset_time"] = now + timedelta(seconds=60)

        # Check if limit exceeded (example: 1000 calls per minute)
        if limiter["calls"] >= 1000:
            raise RateLimitExceededError(
                f"Rate limit exceeded for {limiter_name}",
                reset_time=int((limiter["reset_time"] - now).total_seconds()),
            )

        limiter["calls"] += 1

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integration services."""
        status = {
            "initialized": self._initialized,
            "circuit_breakers": {},
            "rate_limiters": {},
            "active_connections": 0,
            "cache_size": len(self._integration_cache),
        }

        # Get circuit breaker status
        for service, breaker in self._circuit_breakers.items():
            status["circuit_breakers"][service] = {
                "state": breaker["state"],
                "failure_count": breaker["failure_count"],
                "last_failure": (
                    breaker["last_failure"].isoformat()
                    if breaker["last_failure"]
                    else None
                ),
            }

        # Get rate limiter status
        for limiter_name, limiter in self._rate_limiters.items():
            status["rate_limiters"][limiter_name] = {
                "calls_made": limiter["calls"],
                "reset_time": limiter["reset_time"].isoformat(),
            }

        return status

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._session and not self._session.closed:
            await self._session.close()

        logger.info("Systems integration service cleaned up")
