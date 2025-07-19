"""
Security module for NGX Agents.

This module provides security utilities including:
- Secret management
- Encryption services
- Log sanitization
- Security middleware
"""

from .secrets_manager import (
    SecretManager,
    get_secret_manager,
    get_secret,
    SecretKeys,
)

from .encryption_service import (
    EncryptionService,
    FieldEncryption,
    get_encryption_service,
    encrypt_data,
    decrypt_data,
    encrypt_string,
    decrypt_string,
)

from .log_sanitizer import (
    LogSanitizer,
    SanitizingFormatter,
    SanitizingFilter,
    configure_sanitized_logging,
    get_global_sanitizer,
    sanitize_message,
    enable_global_log_sanitization,
)

__all__ = [
    # Secret Management
    "SecretManager",
    "get_secret_manager", 
    "get_secret",
    "SecretKeys",
    
    # Encryption
    "EncryptionService",
    "FieldEncryption",
    "get_encryption_service",
    "encrypt_data",
    "decrypt_data",
    "encrypt_string",
    "decrypt_string",
    
    # Log Sanitization
    "LogSanitizer",
    "SanitizingFormatter",
    "SanitizingFilter",
    "configure_sanitized_logging",
    "get_global_sanitizer",
    "sanitize_message",
    "enable_global_log_sanitization",
]