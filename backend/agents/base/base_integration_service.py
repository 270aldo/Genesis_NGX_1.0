"""
Base Integration Service for NGX Agents
=======================================

This module provides a base class for all integration services in the NGX ecosystem,
ensuring consistent patterns for external API integrations.

Features:
- Retry logic with exponential backoff
- Circuit breaker pattern
- Request/response logging
- Rate limiting
- Fallback responses
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json
import httpx

from core.logging_config import get_logger
from core.circuit_breaker import CircuitBreakerManager

logger = get_logger(__name__)


class IntegrationType(Enum):
    """Types of external integrations."""
    WEARABLE = "wearable"
    NUTRITION = "nutrition"
    FITNESS = "fitness"
    HEALTH = "health"
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"


class BaseIntegrationService(ABC):
    """
    Base class for all integration services in NGX agents.
    
    Provides common functionality for:
    - External API communication
    - Retry logic
    - Circuit breaker pattern
    - Rate limiting
    - Fallback mechanisms
    """
    
    def __init__(
        self,
        service_name: str,
        integration_type: IntegrationType,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 5
    ):
        """
        Initialize base integration service.
        
        Args:
            service_name: Name of the integration service
            integration_type: Type of integration
            base_url: Base URL for the external API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            circuit_breaker_threshold: Failure threshold for circuit breaker
        """
        self.service_name = service_name
        self.integration_type = integration_type
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout),
            headers=self._get_default_headers()
        )
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreakerManager.get_breaker(
            f"{service_name}_integration",
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=60
        )
        
        # Request history for debugging
        self._request_history: List[Dict[str, Any]] = []
        
        logger.info(
            f"Initialized {service_name} integration "
            f"(type: {integration_type.value}, base_url: {base_url})"
        )
    
    # ==================== Abstract Methods ====================
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for the API."""
        pass
    
    @abstractmethod
    def transform_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data before sending to external API."""
        pass
    
    @abstractmethod
    def transform_response_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data received from external API."""
        pass
    
    @abstractmethod
    def create_fallback_response(self, operation: str) -> Dict[str, Any]:
        """Create fallback response when API is unavailable."""
        pass
    
    # ==================== Common Integration Methods ====================
    
    async def sync_data(self, user_id: str, data_type: str, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Sync data from external service.
        
        Args:
            user_id: User identifier
            data_type: Type of data to sync
            date_range: Optional date range (start_date, end_date)
            
        Returns:
            Dict with sync results
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.can_execute():
                logger.warning(f"{self.service_name} circuit breaker is open")
                return self.create_fallback_response("sync_data")
            
            # Prepare request
            endpoint = f"/sync/{data_type}"
            params = {
                "user_id": user_id,
                **(date_range or {})
            }
            
            # Make request with circuit breaker
            response = await self.circuit_breaker.execute(
                lambda: self._make_request("GET", endpoint, params=params)
            )
            
            if response["success"]:
                # Transform and return data
                transformed_data = self.transform_response_data(response["data"])
                
                logger.info(
                    f"Successfully synced {data_type} data for user {user_id} "
                    f"from {self.service_name}"
                )
                
                return {
                    "success": True,
                    "data": transformed_data,
                    "sync_timestamp": datetime.now().isoformat()
                }
            else:
                return response
            
        except Exception as e:
            logger.error(f"Error syncing data from {self.service_name}: {e}")
            return self.create_fallback_response("sync_data")
    
    async def send_data(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send data to external service.
        
        Args:
            endpoint: API endpoint
            data: Data to send
            
        Returns:
            Dict with operation result
        """
        try:
            # Transform data
            transformed_data = self.transform_request_data(data)
            
            # Make request
            response = await self._make_request(
                "POST",
                endpoint,
                json_data=transformed_data
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending data to {self.service_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self.create_fallback_response("send_data")
            }
    
    async def fetch_resource(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific resource from external service.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            
        Returns:
            Resource data if found, None otherwise
        """
        try:
            endpoint = f"/{resource_type}/{resource_id}"
            response = await self._make_request("GET", endpoint)
            
            if response["success"]:
                return self.transform_response_data(response["data"])
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching resource from {self.service_name}: {e}")
            return None
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming webhook from external service.
        
        Args:
            webhook_data: Webhook payload
            
        Returns:
            Dict with processing result
        """
        try:
            # Log webhook
            self._log_request("webhook", webhook_data)
            
            # Validate webhook (override in subclass for specific validation)
            if not await self._validate_webhook(webhook_data):
                return {
                    "success": False,
                    "error": "Invalid webhook signature"
                }
            
            # Process webhook data
            processed_data = self.transform_response_data(webhook_data)
            
            logger.info(f"Successfully processed webhook from {self.service_name}")
            
            return {
                "success": True,
                "processed_data": processed_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling webhook from {self.service_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to external service.
        
        Returns:
            Dict with connection test results
        """
        try:
            # Most APIs have a health or status endpoint
            response = await self._make_request("GET", "/health", skip_retry=True)
            
            return {
                "success": response["success"],
                "service": self.service_name,
                "status": "connected" if response["success"] else "disconnected",
                "response_time": response.get("response_time", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Connection test failed for {self.service_name}: {e}")
            return {
                "success": False,
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_request_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request history for debugging."""
        return self._request_history[-limit:]
    
    # ==================== Private Methods ====================
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"NGX-Agents/{self.service_name}"
        }
        
        # Add auth headers
        headers.update(self.get_auth_headers())
        
        # Add API key if provided
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        skip_retry: bool = False
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body data
            skip_retry: Skip retry logic
            
        Returns:
            Dict with response data
        """
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"
        attempt = 0
        last_error = None
        
        while attempt <= (0 if skip_retry else self.max_retries):
            try:
                start_time = datetime.now()
                
                # Make request
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Log request
                self._log_request(method, {
                    "url": url,
                    "status": response.status_code,
                    "response_time": response_time,
                    "attempt": attempt + 1
                })
                
                # Check response
                response.raise_for_status()
                
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code,
                    "response_time": response_time
                }
                
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                
                # Don't retry on 4xx errors
                if 400 <= e.response.status_code < 500:
                    break
                    
            except Exception as e:
                last_error = str(e)
            
            # Exponential backoff
            if attempt < self.max_retries and not skip_retry:
                wait_time = min(2 ** attempt, 30)  # Max 30 seconds
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                    f"retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            
            attempt += 1
        
        # All attempts failed
        logger.error(f"All request attempts failed for {self.service_name}: {last_error}")
        
        return {
            "success": False,
            "error": last_error,
            "attempts": attempt
        }
    
    async def _validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Validate webhook signature.
        Override in subclass for specific validation logic.
        """
        # Basic validation - check for required fields
        return "event" in webhook_data and "data" in webhook_data
    
    def _log_request(self, method: str, details: Dict[str, Any]) -> None:
        """Log request for debugging."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "method": method,
            "details": details
        }
        
        self._request_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self._request_history) > 1000:
            self._request_history = self._request_history[-1000:]
    
    async def close(self) -> None:
        """Close HTTP client connection."""
        await self.client.aclose()