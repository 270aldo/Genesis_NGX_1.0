"""
Retry Pattern for ADK
====================

Implements retry logic with exponential backoff and jitter
for handling transient failures gracefully.
"""

from typing import Callable, Optional, Union, Type, Tuple, List, Any
from functools import wraps
import asyncio
import time
import random
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.logging_config import get_logger
from ..core.exceptions import RetryExhaustedError, ADKError

logger = get_logger(__name__)


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_factor: float = 2.0
    jitter: bool = True
    jitter_range: Tuple[float, float] = (0.8, 1.2)
    
    # Exceptions to retry on
    retry_on: Tuple[Type[Exception], ...] = (Exception,)
    
    # Exceptions to NOT retry on (takes precedence)
    dont_retry_on: Tuple[Type[Exception], ...] = ()
    
    # Custom retry predicate
    retry_predicate: Optional[Callable[[Exception], bool]] = None
    
    # Callbacks
    on_retry: Optional[Callable[[Exception, int], None]] = None
    on_success: Optional[Callable[[Any, int], None]] = None
    on_failure: Optional[Callable[[Exception, int], None]] = None
    
    def should_retry(self, exception: Exception) -> bool:
        """Determine if exception should trigger a retry."""
        # Check dont_retry_on first (takes precedence)
        if isinstance(exception, self.dont_retry_on):
            return False
        
        # Check retry_on
        if not isinstance(exception, self.retry_on):
            return False
        
        # Apply custom predicate if provided
        if self.retry_predicate:
            return self.retry_predicate(exception)
        
        return True
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry attempt."""
        # Exponential backoff
        delay = min(
            self.initial_delay * (self.backoff_factor ** (attempt - 1)),
            self.max_delay
        )
        
        # Add jitter if enabled
        if self.jitter:
            jitter_min, jitter_max = self.jitter_range
            delay *= random.uniform(jitter_min, jitter_max)
        
        return delay


def retry(
    max_attempts: Optional[int] = None,
    initial_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    backoff_factor: Optional[float] = None,
    jitter: Optional[bool] = None,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    dont_retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    retry_predicate: Optional[Callable[[Exception], bool]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
    policy: Optional[RetryPolicy] = None
):
    """
    Decorator to add retry logic to functions.
    
    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for exponential backoff
        jitter: Whether to add jitter to delays
        retry_on: Tuple of exceptions to retry on
        dont_retry_on: Tuple of exceptions to never retry on
        retry_predicate: Custom function to determine if retry should occur
        on_retry: Callback when retry occurs
        policy: Pre-configured RetryPolicy (overrides other args)
    
    Example:
        @retry(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
        async def unstable_api_call():
            response = await external_api.call()
            return response
        
        # With custom policy
        policy = RetryPolicy(
            max_attempts=5,
            retry_on=(HTTPError, TimeoutError),
            dont_retry_on=(ValueError,)
        )
        
        @retry(policy=policy)
        async def another_api_call():
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Create or use provided policy
        if policy:
            retry_policy = policy
        else:
            # Build policy from arguments
            kwargs = {}
            if max_attempts is not None:
                kwargs['max_attempts'] = max_attempts
            if initial_delay is not None:
                kwargs['initial_delay'] = initial_delay
            if max_delay is not None:
                kwargs['max_delay'] = max_delay
            if backoff_factor is not None:
                kwargs['backoff_factor'] = backoff_factor
            if jitter is not None:
                kwargs['jitter'] = jitter
            if retry_on is not None:
                kwargs['retry_on'] = retry_on
            if dont_retry_on is not None:
                kwargs['dont_retry_on'] = dont_retry_on
            if retry_predicate is not None:
                kwargs['retry_predicate'] = retry_predicate
            if on_retry is not None:
                kwargs['on_retry'] = on_retry
            
            retry_policy = RetryPolicy(**kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            start_time = time.time()
            
            for attempt in range(1, retry_policy.max_attempts + 1):
                try:
                    # Execute function
                    result = await func(*args, **kwargs)
                    
                    # Success callback
                    if retry_policy.on_success:
                        retry_policy.on_success(result, attempt)
                    
                    # Log success if it was a retry
                    if attempt > 1:
                        logger.info(
                            f"Retry successful for {func.__name__} "
                            f"after {attempt} attempts",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt,
                                "total_duration": time.time() - start_time
                            }
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if not retry_policy.should_retry(e):
                        logger.debug(
                            f"Exception {type(e).__name__} is not retryable "
                            f"for {func.__name__}"
                        )
                        raise
                    
                    # Check if we have attempts left
                    if attempt >= retry_policy.max_attempts:
                        break
                    
                    # Calculate delay
                    delay = retry_policy.calculate_delay(attempt)
                    
                    # Retry callback
                    if retry_policy.on_retry:
                        retry_policy.on_retry(e, attempt)
                    
                    # Log retry attempt
                    logger.warning(
                        f"Retry attempt {attempt}/{retry_policy.max_attempts} "
                        f"for {func.__name__} after {type(e).__name__}: {str(e)}. "
                        f"Waiting {delay:.2f}s before next attempt.",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": retry_policy.max_attempts,
                            "delay": delay,
                            "error_type": type(e).__name__
                        }
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
            
            # All attempts exhausted
            if retry_policy.on_failure:
                retry_policy.on_failure(last_exception, retry_policy.max_attempts)
            
            raise RetryExhaustedError(
                f"All {retry_policy.max_attempts} retry attempts failed for {func.__name__}",
                attempts=retry_policy.max_attempts,
                last_error=str(last_exception)
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            start_time = time.time()
            
            for attempt in range(1, retry_policy.max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    if retry_policy.on_success:
                        retry_policy.on_success(result, attempt)
                    
                    if attempt > 1:
                        logger.info(
                            f"Retry successful for {func.__name__} "
                            f"after {attempt} attempts",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt,
                                "total_duration": time.time() - start_time
                            }
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if not retry_policy.should_retry(e):
                        logger.debug(
                            f"Exception {type(e).__name__} is not retryable "
                            f"for {func.__name__}"
                        )
                        raise
                    
                    if attempt >= retry_policy.max_attempts:
                        break
                    
                    delay = retry_policy.calculate_delay(attempt)
                    
                    if retry_policy.on_retry:
                        retry_policy.on_retry(e, attempt)
                    
                    logger.warning(
                        f"Retry attempt {attempt}/{retry_policy.max_attempts} "
                        f"for {func.__name__} after {type(e).__name__}: {str(e)}. "
                        f"Waiting {delay:.2f}s before next attempt.",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": retry_policy.max_attempts,
                            "delay": delay,
                            "error_type": type(e).__name__
                        }
                    )
                    
                    time.sleep(delay)
            
            if retry_policy.on_failure:
                retry_policy.on_failure(last_exception, retry_policy.max_attempts)
            
            raise RetryExhaustedError(
                f"All {retry_policy.max_attempts} retry attempts failed for {func.__name__}",
                attempts=retry_policy.max_attempts,
                last_error=str(last_exception)
            )
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    factor: float = 2.0
) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Current attempt number (1-based)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        factor: Multiplication factor
    
    Returns:
        Calculated delay in seconds
    """
    return min(base_delay * (factor ** (attempt - 1)), max_delay)


class RetryableOperation:
    """
    Context manager for retryable operations.
    
    Example:
        async with RetryableOperation(max_attempts=3) as retry:
            result = await retry.execute(risky_operation, arg1, arg2)
    """
    
    def __init__(self, policy: Optional[RetryPolicy] = None, **kwargs):
        self.policy = policy or RetryPolicy(**kwargs)
        self._attempt = 0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        @retry(policy=self.policy)
        async def wrapped():
            self._attempt += 1
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return await wrapped()
    
    @property
    def attempts(self) -> int:
        """Get number of attempts made."""
        return self._attempt


# Predefined retry policies for common scenarios
class CommonRetryPolicies:
    """Common retry policies for different scenarios."""
    
    @staticmethod
    def api_calls() -> RetryPolicy:
        """Policy for external API calls."""
        return RetryPolicy(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=10.0,
            backoff_factor=2.0,
            retry_on=(ConnectionError, TimeoutError),
            dont_retry_on=(ValueError, TypeError, ADKError)
        )
    
    @staticmethod
    def database() -> RetryPolicy:
        """Policy for database operations."""
        return RetryPolicy(
            max_attempts=5,
            initial_delay=0.1,
            max_delay=5.0,
            backoff_factor=2.0,
            jitter=True
        )
    
    @staticmethod
    def critical() -> RetryPolicy:
        """Policy for critical operations."""
        return RetryPolicy(
            max_attempts=10,
            initial_delay=0.5,
            max_delay=30.0,
            backoff_factor=1.5,
            jitter=True
        )
    
    @staticmethod
    def fast_fail() -> RetryPolicy:
        """Policy for operations that should fail fast."""
        return RetryPolicy(
            max_attempts=2,
            initial_delay=0.1,
            max_delay=0.5,
            backoff_factor=2.0,
            jitter=False
        )