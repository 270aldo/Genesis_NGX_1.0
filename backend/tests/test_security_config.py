"""
Test security configuration changes.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from core.settings_lazy import settings


class TestSecurityConfiguration:
    """Test security configuration is properly set."""
    
    def test_jwt_secret_is_set(self):
        """Test that JWT secret is properly configured."""
        # Should not have default value
        assert hasattr(settings, 'jwt_secret')
        assert settings.jwt_secret != "dev-secret-key"
        assert len(settings.jwt_secret) > 32  # At least 32 characters
    
    def test_environment_is_set(self):
        """Test that environment is properly configured."""
        assert hasattr(settings, 'env')
        assert settings.env in ['development', 'staging', 'production', 'testing']
    
    def test_redis_configuration(self):
        """Test Redis configuration."""
        assert hasattr(settings, 'redis_host')
        assert hasattr(settings, 'redis_port')
        assert hasattr(settings, 'redis_password')
        # Password should not be default
        assert settings.redis_password != "your-redis-password-here"
    
    def test_cors_configuration(self):
        """Test CORS is not wide open."""
        # In production, should not allow all origins
        if settings.env == "production":
            # Should have specific origins configured
            assert hasattr(settings, 'cors_allowed_origins')
    
    def test_security_features_enabled(self):
        """Test security features are enabled."""
        # Rate limiting should be enabled
        assert getattr(settings, 'enable_rate_limiting', True) == True
        
        # Security headers should be enabled
        assert getattr(settings, 'enable_security_headers', True) == True
        
        # Audit trail should be enabled
        assert getattr(settings, 'enable_audit_trail', True) == True


class TestSecurityMiddleware:
    """Test security middleware configuration."""
    
    def test_rate_limit_configuration(self):
        """Test rate limit values are reasonable."""
        # Auth endpoints
        auth_limit = getattr(settings, 'rate_limit_auth_requests', 5)
        assert auth_limit > 0 and auth_limit <= 10  # Max 10 auth attempts per minute
        
        # Chat endpoints
        chat_limit = getattr(settings, 'rate_limit_chat_requests', 30)
        assert chat_limit > 0 and chat_limit <= 100  # Reasonable chat limit
        
        # Heavy operations
        heavy_limit = getattr(settings, 'rate_limit_heavy_requests', 10)
        assert heavy_limit > 0 and heavy_limit <= 20  # Limited heavy operations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])