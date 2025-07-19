"""
Log sanitization service to remove PII and sensitive data from logs.

This module provides utilities to automatically detect and redact sensitive
information from log messages to ensure compliance with privacy regulations.
"""

import re
import logging
from typing import Any, Dict, List, Pattern, Union, Optional
from functools import lru_cache
import json


class LogSanitizer:
    """
    Sanitizes log messages by detecting and redacting sensitive information.
    
    Detects and redacts:
    - Email addresses
    - JWT tokens
    - API keys
    - Passwords
    - Credit card numbers
    - Social Security Numbers
    - Phone numbers
    - IP addresses
    - URLs with sensitive parameters
    """
    
    # Patterns for sensitive data detection
    SENSITIVE_PATTERNS: Dict[str, Pattern] = {
        # Email addresses
        'email': re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        ),
        
        # JWT tokens (three base64 parts separated by dots)
        'jwt_token': re.compile(
            r'(Bearer\s+)?[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+',
            re.IGNORECASE
        ),
        
        # API keys (various formats)
        'api_key': re.compile(
            r'(api[_\-]?key|apikey|key|token|secret|credential)["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?',
            re.IGNORECASE
        ),
        
        # Passwords in various formats
        'password': re.compile(
            r'(password|passwd|pwd|pass|contrase[ñn]a)["\']?\s*[:=]\s*["\']?([^\s"\'{}]+)["\']?',
            re.IGNORECASE
        ),
        
        # Credit card numbers (basic pattern)
        'credit_card': re.compile(
            r'\b(?:\d{4}[\s\-]?){3}\d{4}\b'
        ),
        
        # SSN (US format)
        'ssn': re.compile(
            r'\b\d{3}-\d{2}-\d{4}\b'
        ),
        
        # Phone numbers (various formats)
        'phone': re.compile(
            r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ),
        
        # IP addresses (IPv4)
        'ip_address': re.compile(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ),
        
        # URLs with potential sensitive parameters
        'url_params': re.compile(
            r'(https?://[^\s]+[?&])(token|key|secret|password|auth|session|api[_\-]?key)=([^&\s]+)',
            re.IGNORECASE
        ),
        
        # Base64 encoded strings that might be sensitive
        'base64_long': re.compile(
            r'[A-Za-z0-9+/]{40,}={0,2}'
        ),
        
        # Supabase keys
        'supabase_key': re.compile(
            r'eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+',
        ),
        
        # Redis passwords in URLs
        'redis_url': re.compile(
            r'redis://([^:]+:)?([^@]+)@',
            re.IGNORECASE
        ),
    }
    
    # Fields that commonly contain sensitive data
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api_key',
        'apikey', 'auth', 'authorization', 'credential', 'private_key',
        'secret_key', 'access_token', 'refresh_token', 'session_id',
        'ssn', 'social_security_number', 'credit_card', 'card_number',
        'cvv', 'pin', 'tax_id', 'passport', 'license', 'bank_account'
    }
    
    def __init__(self, custom_patterns: Optional[Dict[str, Pattern]] = None):
        """
        Initialize the log sanitizer.
        
        Args:
            custom_patterns: Additional patterns to detect sensitive data
        """
        self.patterns = self.SENSITIVE_PATTERNS.copy()
        if custom_patterns:
            self.patterns.update(custom_patterns)
    
    def sanitize(self, message: Any) -> Any:
        """
        Sanitize a log message by redacting sensitive information.
        
        Args:
            message: The log message (string, dict, list, etc.)
            
        Returns:
            Sanitized version of the message
        """
        if isinstance(message, str):
            return self._sanitize_string(message)
        elif isinstance(message, dict):
            return self._sanitize_dict(message)
        elif isinstance(message, (list, tuple)):
            return [self.sanitize(item) for item in message]
        elif isinstance(message, (int, float, bool, type(None))):
            return message
        else:
            # Convert to string and sanitize
            return self._sanitize_string(str(message))
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize a string by applying all patterns."""
        sanitized = text
        
        # Apply each pattern
        for pattern_name, pattern in self.patterns.items():
            if pattern_name == 'api_key' or pattern_name == 'password':
                # Special handling for key=value patterns
                sanitized = pattern.sub(
                    lambda m: f"{m.group(1)}=[REDACTED_{pattern_name.upper()}]",
                    sanitized
                )
            elif pattern_name == 'url_params':
                # Special handling for URL parameters
                sanitized = pattern.sub(
                    lambda m: f"{m.group(1)}{m.group(2)}=[REDACTED_PARAM]",
                    sanitized
                )
            elif pattern_name == 'redis_url':
                # Special handling for Redis URLs
                sanitized = pattern.sub(
                    r'redis://\1[REDACTED_PASSWORD]@',
                    sanitized
                )
            else:
                # Standard redaction
                sanitized = pattern.sub(f'[REDACTED_{pattern_name.upper()}]', sanitized)
        
        return sanitized
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a dictionary by checking field names and values."""
        sanitized = {}
        
        for key, value in data.items():
            # Check if the field name suggests sensitive data
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                sanitized[key] = '[REDACTED_FIELD]'
            else:
                # Recursively sanitize the value
                sanitized[key] = self.sanitize(value)
        
        return sanitized
    
    @lru_cache(maxsize=1000)
    def is_sensitive(self, text: str) -> bool:
        """
        Check if a string contains sensitive information.
        
        Args:
            text: The string to check
            
        Returns:
            True if sensitive information is detected
        """
        for pattern in self.patterns.values():
            if pattern.search(text):
                return True
        return False
    
    def sanitize_exception(self, exc: Exception) -> str:
        """
        Sanitize an exception message and traceback.
        
        Args:
            exc: The exception to sanitize
            
        Returns:
            Sanitized exception string
        """
        # Get the exception message
        exc_str = str(exc)
        sanitized_msg = self._sanitize_string(exc_str)
        
        # Get the exception type
        exc_type = type(exc).__name__
        
        return f"{exc_type}: {sanitized_msg}"


class SanitizingFormatter(logging.Formatter):
    """
    Custom logging formatter that sanitizes log messages.
    
    This formatter can be used with Python's logging module to automatically
    sanitize all log messages.
    """
    
    def __init__(self, *args, sanitizer: Optional[LogSanitizer] = None, **kwargs):
        """
        Initialize the sanitizing formatter.
        
        Args:
            sanitizer: Optional LogSanitizer instance
            *args, **kwargs: Arguments passed to logging.Formatter
        """
        super().__init__(*args, **kwargs)
        self.sanitizer = sanitizer or LogSanitizer()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format and sanitize a log record."""
        # Sanitize the message
        original_msg = record.getMessage()
        record.msg = self.sanitizer.sanitize(original_msg)
        
        # Sanitize any additional arguments
        if hasattr(record, 'args') and record.args:
            record.args = tuple(self.sanitizer.sanitize(arg) for arg in record.args)
        
        # Format the record
        formatted = super().format(record)
        
        # Restore original message (don't modify the record permanently)
        record.msg = original_msg
        
        return formatted


class SanitizingFilter(logging.Filter):
    """
    Logging filter that sanitizes log records.
    
    This filter can be added to handlers or loggers to sanitize messages.
    """
    
    def __init__(self, sanitizer: Optional[LogSanitizer] = None):
        """
        Initialize the sanitizing filter.
        
        Args:
            sanitizer: Optional LogSanitizer instance
        """
        super().__init__()
        self.sanitizer = sanitizer or LogSanitizer()
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and sanitize a log record."""
        # Sanitize the message
        if hasattr(record, 'msg'):
            record.msg = self.sanitizer.sanitize(record.msg)
        
        # Sanitize arguments
        if hasattr(record, 'args') and record.args:
            record.args = tuple(self.sanitizer.sanitize(arg) for arg in record.args)
        
        # Always return True to pass the record through
        return True


def configure_sanitized_logging(
    logger_name: Optional[str] = None,
    sanitizer: Optional[LogSanitizer] = None
) -> logging.Logger:
    """
    Configure a logger with automatic sanitization.
    
    Args:
        logger_name: Name of the logger (None for root logger)
        sanitizer: Optional LogSanitizer instance
        
    Returns:
        Configured logger with sanitization
    """
    logger = logging.getLogger(logger_name)
    
    # Create sanitizer if not provided
    if sanitizer is None:
        sanitizer = LogSanitizer()
    
    # Add sanitizing filter to the logger
    sanitizing_filter = SanitizingFilter(sanitizer)
    logger.addFilter(sanitizing_filter)
    
    # If the logger has handlers, update their formatters
    for handler in logger.handlers:
        if handler.formatter:
            # Wrap the existing formatter
            original_formatter = handler.formatter
            sanitizing_formatter = SanitizingFormatter(
                fmt=original_formatter._fmt if hasattr(original_formatter, '_fmt') else None,
                datefmt=original_formatter.datefmt,
                sanitizer=sanitizer
            )
            handler.setFormatter(sanitizing_formatter)
    
    return logger


# Global sanitizer instance
_global_sanitizer: Optional[LogSanitizer] = None


def get_global_sanitizer() -> LogSanitizer:
    """Get the global LogSanitizer instance."""
    global _global_sanitizer
    if _global_sanitizer is None:
        _global_sanitizer = LogSanitizer()
    return _global_sanitizer


def sanitize_message(message: Any) -> Any:
    """Sanitize a message using the global sanitizer."""
    return get_global_sanitizer().sanitize(message)


def enable_global_log_sanitization():
    """Enable log sanitization globally for all loggers."""
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Add sanitizing filter
    sanitizing_filter = SanitizingFilter(get_global_sanitizer())
    root_logger.addFilter(sanitizing_filter)
    
    # Update existing handlers
    for handler in root_logger.handlers:
        if handler.formatter and not isinstance(handler.formatter, SanitizingFormatter):
            # Replace with sanitizing formatter
            original_formatter = handler.formatter
            sanitizing_formatter = SanitizingFormatter(
                fmt=original_formatter._fmt if hasattr(original_formatter, '_fmt') else None,
                datefmt=original_formatter.datefmt,
                sanitizer=get_global_sanitizer()
            )
            handler.setFormatter(sanitizing_formatter)