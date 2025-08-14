"""
Enhanced Circuit Breaker Implementation for Agent Communication
===============================================================

Implements the Circuit Breaker pattern to prevent cascading failures
between agents and external services.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is failing, requests are blocked
- HALF_OPEN: Testing if service has recovered

Features:
- Automatic state transitions based on failure thresholds
- Configurable timeout and failure thresholds
- Fallback strategies for graceful degradation
- Metrics and monitoring integration
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    name: str
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Number of successes in half-open before closing
    timeout: float = 60.0  # Seconds before attempting to close from open state
    failure_rate_threshold: float = 0.5  # Failure rate to trigger open state
    min_requests: int = 10  # Minimum requests before calculating failure rate
    fallback_function: Optional[Callable] = None
    exclude_exceptions: tuple = ()  # Exceptions that don't count as failures


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    fallback_requests: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    state_changes: list = field(default_factory=list)


class CircuitBreaker(Generic[T]):
    """
    Circuit breaker implementation for fault tolerance.

    Usage:
        config = CircuitBreakerConfig(
            name="vertex_ai",
            failure_threshold=5,
            timeout=60.0,
            fallback_function=lambda: {"error": "Service unavailable"}
        )

        breaker = CircuitBreaker(config)

        @breaker.protect
        async def call_service():
            return await external_service.call()
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._last_state_change = time.time()
        self._lock = asyncio.Lock()

        logger.info(f"Circuit breaker '{config.name}' initialized in CLOSED state")

    async def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self._last_state_change = time.time()

            self.metrics.state_changes.append(
                {
                    "from": old_state.value,
                    "to": new_state.value,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.warning(
                f"Circuit breaker '{self.config.name}' state changed: "
                f"{old_state.value} -> {new_state.value}"
            )

    async def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return time.time() - self._last_state_change >= self.config.timeout

    async def _record_success(self):
        """Record a successful request."""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.consecutive_successes += 1
            self.metrics.consecutive_failures = 0
            self.metrics.last_success_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                if self.metrics.consecutive_successes >= self.config.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)

    async def _record_failure(self):
        """Record a failed request."""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.consecutive_failures += 1
            self.metrics.consecutive_successes = 0
            self.metrics.last_failure_time = datetime.now()

            # Check if we should open the circuit
            if self.state == CircuitState.CLOSED:
                # Check failure threshold
                if self.metrics.consecutive_failures >= self.config.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)
                # Check failure rate
                elif self.metrics.total_requests >= self.config.min_requests:
                    failure_rate = (
                        self.metrics.failed_requests / self.metrics.total_requests
                    )
                    if failure_rate >= self.config.failure_rate_threshold:
                        await self._transition_to(CircuitState.OPEN)

            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state reopens the circuit
                await self._transition_to(CircuitState.OPEN)

    async def _execute_fallback(self) -> Any:
        """Execute fallback function if configured."""
        self.metrics.fallback_requests += 1

        if self.config.fallback_function:
            try:
                if asyncio.iscoroutinefunction(self.config.fallback_function):
                    return await self.config.fallback_function()
                else:
                    return self.config.fallback_function()
            except Exception as e:
                logger.error(f"Fallback function failed for '{self.config.name}': {e}")
                raise
        else:
            raise CircuitBreakerOpen(f"Circuit breaker '{self.config.name}' is OPEN")

    def protect(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to protect a function with circuit breaker.

        Args:
            func: Function to protect

        Returns:
            Protected function
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if circuit should attempt reset
            if self.state == CircuitState.OPEN:
                if await self._should_attempt_reset():
                    await self._transition_to(CircuitState.HALF_OPEN)
                else:
                    return await self._execute_fallback()

            # Attempt to execute the function
            try:
                result = await func(*args, **kwargs)
                await self._record_success()
                return result

            except Exception as e:
                # Check if this exception should be excluded
                if isinstance(e, self.config.exclude_exceptions):
                    raise

                await self._record_failure()

                # If circuit is now open, execute fallback
                if self.state == CircuitState.OPEN:
                    return await self._execute_fallback()

                raise

        return wrapper

    async def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "fallback_requests": self.metrics.fallback_requests,
                "failure_rate": (
                    self.metrics.failed_requests / self.metrics.total_requests
                    if self.metrics.total_requests > 0
                    else 0
                ),
                "consecutive_failures": self.metrics.consecutive_failures,
                "consecutive_successes": self.metrics.consecutive_successes,
                "last_failure": (
                    self.metrics.last_failure_time.isoformat()
                    if self.metrics.last_failure_time
                    else None
                ),
                "last_success": (
                    self.metrics.last_success_time.isoformat()
                    if self.metrics.last_success_time
                    else None
                ),
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
                "failure_rate_threshold": self.config.failure_rate_threshold,
            },
        }

    async def reset(self):
        """Manually reset the circuit breaker to closed state."""
        async with self._lock:
            await self._transition_to(CircuitState.CLOSED)
            self.metrics.consecutive_failures = 0
            self.metrics.consecutive_successes = 0
            logger.info(
                f"Circuit breaker '{self.config.name}' manually reset to CLOSED"
            )


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different services.

    Usage:
        manager = CircuitBreakerManager()

        # Register circuit breakers
        manager.register("vertex_ai", CircuitBreakerConfig(...))
        manager.register("supabase", CircuitBreakerConfig(...))

        # Get breaker for protection
        breaker = manager.get("vertex_ai")

        @breaker.protect
        async def call_vertex_ai():
            ...
    """

    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        logger.info("Circuit breaker manager initialized")

    def register(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """Register a new circuit breaker."""
        if config is None:
            config = CircuitBreakerConfig(name=name)

        if name in self._breakers:
            logger.warning(f"Overwriting existing circuit breaker: {name}")

        self._breakers[name] = CircuitBreaker(config)
        logger.info(f"Registered circuit breaker: {name}")

    def get(self, name: str) -> CircuitBreaker:
        """Get a circuit breaker by name."""
        if name not in self._breakers:
            # Auto-register with default config if not exists
            self.register(name)

        return self._breakers[name]

    async def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers."""
        status = {}
        for name, breaker in self._breakers.items():
            status[name] = await breaker.get_status()
        return status

    async def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            await breaker.reset()
        logger.info("All circuit breakers reset")


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()


# Pre-configured circuit breakers for common services
def initialize_default_breakers():
    """Initialize default circuit breakers for common services."""

    # Vertex AI circuit breaker
    circuit_breaker_manager.register(
        "vertex_ai",
        CircuitBreakerConfig(
            name="vertex_ai",
            failure_threshold=3,
            success_threshold=2,
            timeout=30.0,
            failure_rate_threshold=0.5,
            fallback_function=lambda: {
                "error": "AI service temporarily unavailable",
                "fallback": True,
            },
        ),
    )

    # Supabase circuit breaker
    circuit_breaker_manager.register(
        "supabase",
        CircuitBreakerConfig(
            name="supabase",
            failure_threshold=5,
            success_threshold=3,
            timeout=60.0,
            failure_rate_threshold=0.3,
        ),
    )

    # Redis circuit breaker
    circuit_breaker_manager.register(
        "redis",
        CircuitBreakerConfig(
            name="redis",
            failure_threshold=10,
            success_threshold=5,
            timeout=30.0,
            failure_rate_threshold=0.7,
            fallback_function=lambda: None,  # Graceful degradation without cache
        ),
    )

    # Agent communication circuit breakers
    for agent in [
        "NEXUS",
        "BLAZE",
        "SAGE",
        "SPARK",
        "WAVE",
        "LUNA",
        "STELLA",
        "NOVA",
        "CODE",
        "GUARDIAN",
        "NODE",
    ]:
        circuit_breaker_manager.register(
            f"agent_{agent}",
            CircuitBreakerConfig(
                name=f"agent_{agent}",
                failure_threshold=3,
                success_threshold=2,
                timeout=20.0,
                failure_rate_threshold=0.4,
                fallback_function=lambda: {
                    "error": f"Agent {agent} temporarily unavailable",
                    "fallback": True,
                    "agent": agent,
                },
            ),
        )

    logger.info("Default circuit breakers initialized")
