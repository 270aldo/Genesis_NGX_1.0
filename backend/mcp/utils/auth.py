"""
Authentication utilities for MCP Gateway
"""

import os
import hashlib
import hmac
from typing import Optional
from mcp.config import settings


def verify_api_key(api_key: Optional[str]) -> bool:
    """
    Verify if the provided API key is valid
    
    Args:
        api_key: The API key to verify
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not settings.mcp_auth_enabled:
        return True
    
    if not api_key or not settings.mcp_api_key:
        return False
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(api_key, settings.mcp_api_key)


def generate_api_key() -> str:
    """
    Generate a secure API key for MCP access
    
    Returns:
        str: A secure API key
    """
    # Generate random bytes and create hash
    random_bytes = os.urandom(32)
    return hashlib.sha256(random_bytes).hexdigest()


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage
    
    Args:
        api_key: The API key to hash
        
    Returns:
        str: Hashed API key
    """
    salt = os.environ.get("MCP_API_KEY_SALT", "genesis-mcp-salt")
    return hashlib.pbkdf2_hmac('sha256', api_key.encode(), salt.encode(), 100000).hex()