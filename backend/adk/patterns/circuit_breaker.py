"""
Circuit Breaker Pattern for ADK
===============================

Implements the circuit breaker pattern to prevent cascading failures
and provide graceful degradation of services.
"""

from typing import Callable, Optional, Any, Dict
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import time

from core.logging_config import get_logger
from ..core.exceptions import CircuitBreakerError

logger = get_logger(__name__)


class CircuitState(Enum):
    """States of the circuit breaker."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures exceeded threshold
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.
    
    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are rejected
    - HALF_OPEN: Testing if the service has recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: Optional[str] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to catch
            name: Name for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name or "CircuitBreaker"
        
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = CircuitState.CLOSED
        self._half_open_attempts = 0
        self._success_count = 0
        self._total_calls = 0
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting requests)."""
        return self._state == CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return False
        
        return (
            datetime.utcnow() - self._last_failure_time
        ).total_seconds() >= self.recovery_timeout
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: If function fails
        """
        self._total_calls += 1
        
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN and self._should_attempt_reset():
            self._state = CircuitState.HALF_OPEN
            self._half_open_attempts = 0
            logger.info(f"{self.name}: Transitioning to HALF_OPEN state")
        
        # Reject calls if circuit is OPEN
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"{self.name}: Circuit breaker is OPEN",
                service=self.name,
                reset_time=int(
                    self.recovery_timeout - 
                    (datetime.utcnow() - self._last_failure_time).total_seconds()
                )
            )
        
        try:
            # Attempt the call
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def async_call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call async function through circuit breaker.
        
        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: If function fails
        """
        self._total_calls += 1
        
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN and self._should_attempt_reset():
            self._state = CircuitState.HALF_OPEN
            self._half_open_attempts = 0
            logger.info(f"{self.name}: Transitioning to HALF_OPEN state")
        
        # Reject calls if circuit is OPEN
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"{self.name}: Circuit breaker is OPEN",
                service=self.name,
                reset_time=int(
                    self.recovery_timeout - 
                    (datetime.utcnow() - self._last_failure_time).total_seconds()
                )
            )
        
        try:
            # Attempt the call
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        self._success_count += 1
        
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_attempts += 1
            if self._half_open_attempts >= 3:  # Configurable threshold
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info(f"{self.name}: Circuit recovered, transitioning to CLOSED")
        else:
            # Reset failure count on success in CLOSED state
            self._failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()
        
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning(f"{self.name}: Recovery failed, circuit remains OPEN")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.error(
                f"{self.name}: Failure threshold reached ({self._failure_count}), "
                f"circuit is now OPEN"
            )
    
    def reset(self):
        """Manually reset the circuit breaker."""
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
        self._half_open_attempts = 0
        logger.info(f"{self.name}: Circuit manually reset to CLOSED")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        success_rate = (
            self._success_count / self._total_calls 
            if self._total_calls > 0 
            else 0
        )
        
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_calls": self._total_calls,
            "success_rate": success_rate,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "last_failure_time": (
                self._last_failure_time.isoformat() 
                if self._last_failure_time 
                else None
            )
        }
    
    def __call__(self, func: Callable) -> Callable:
        """Use as decorator."""
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self.async_call(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self.call(func, *args, **kwargs)
            return sync_wrapper


class CircuitBreakerMixin:
    """
    Mixin to add circuit breaker functionality to agents.
    
    Example:
        class MyAgent(BaseADKAgent, CircuitBreakerMixin):
            def __init__(self):
                super().__init__()
                self.init_circuit_breakers()
                
            @with_circuit_breaker("external_api")
            async def call_external_api(self):
                # Make external API call
                pass
    """
    
    def init_circuit_breakers(self):
        """Initialize circuit breakers for the agent."""
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def add_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ) -> CircuitBreaker:
        """Add a circuit breaker."""
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=name
        )
        self._circuit_breakers[name] = cb
        return cb
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self._circuit_breakers.get(name)
    
    def with_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        """Decorator to apply circuit breaker to a method."""
        def decorator(func: Callable) -> Callable:
            # Get or create circuit breaker
            if name not in self._circuit_breakers:
                self.add_circuit_breaker(
                    name,
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout
                )
            
            cb = self._circuit_breakers[name]
            
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(self_inner, *args, **kwargs):
                    return await cb.async_call(func, self_inner, *args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(self_inner, *args, **kwargs):
                    return cb.call(func, self_inner, *args, **kwargs)
                return sync_wrapper
        
        return decorator
    
    def get_circuit_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {
            name: cb.get_stats()
            for name, cb in self._circuit_breakers.items()
        }


# Convenience decorator
def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception,
    name: Optional[str] = None
):
    """
    Decorator to apply circuit breaker pattern.
    
    Args:
        failure_threshold: Number of failures before opening
        recovery_timeout: Seconds before attempting recovery
        expected_exception: Exception type to catch
        name: Circuit breaker name
    
    Example:
        @circuit_breaker(failure_threshold=3, recovery_timeout=30)
        async def risky_operation():
            # Operation that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        cb_name = name or f"{func.__module__}.{func.__name__}"
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=cb_name
        )
        return cb(func)
    
    return decorator