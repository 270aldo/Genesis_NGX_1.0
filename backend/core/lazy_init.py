"""
Lazy initialization module for GENESIS.

This module provides lazy initialization for global instances to prevent
hanging during module imports. All heavy resources are initialized only
when first accessed, not during import time.
"""

import asyncio
import functools
from typing import Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class LazyInstance:
    """
    A lazy instance wrapper that defers initialization until first access.
    """
    
    def __init__(self, factory: Callable[[], Any], name: str):
        """
        Initialize lazy instance.
        
        Args:
            factory: Factory function to create the instance
            name: Name of the instance for logging
        """
        self._factory = factory
        self._name = name
        self._instance: Optional[Any] = None
        self._lock = asyncio.Lock()
        
    def __getattr__(self, name: str) -> Any:
        """
        Lazy initialization on attribute access.
        """
        if self._instance is None:
            # Use synchronous initialization for simplicity
            logger.info(f"Lazy initializing {self._name}")
            self._instance = self._factory()
            logger.info(f"{self._name} initialized")
        return getattr(self._instance, name)
    
    def __call__(self, *args, **kwargs):
        """
        Support calling the instance if it's callable.
        """
        if self._instance is None:
            logger.info(f"Lazy initializing {self._name} (on call)")
            self._instance = self._factory()
            logger.info(f"{self._name} initialized")
        return self._instance(*args, **kwargs)
    
    @property
    def is_initialized(self) -> bool:
        """Check if the instance has been initialized."""
        return self._instance is not None
    
    def get_instance(self) -> Any:
        """Get the actual instance, initializing if needed."""
        if self._instance is None:
            logger.info(f"Lazy initializing {self._name} (explicit get)")
            self._instance = self._factory()
            logger.info(f"{self._name} initialized")
        return self._instance


def lazy_singleton(name: str):
    """
    Decorator to make a class a lazy singleton.
    
    Args:
        name: Name for logging
    """
    def decorator(cls):
        _instance = None
        _lock = asyncio.Lock()
        
        @functools.wraps(cls)
        def wrapper(*args, **kwargs):
            nonlocal _instance
            if _instance is None:
                logger.info(f"Creating lazy singleton instance of {name}")
                _instance = cls(*args, **kwargs)
            return _instance
        
        wrapper._original_class = cls
        wrapper._instance = lambda: _instance
        return wrapper
    
    return decorator