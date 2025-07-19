"""
Secure configuration for NGX Agents with Google Secret Manager integration.

This module extends the base settings to use Google Secret Manager for
sensitive credentials in production environments.
"""

import os
from typing import Optional, Any
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.security import get_secret_manager, SecretKeys


class SecureSettings(BaseSettings):
    """Secure configuration with Secret Manager integration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    
    # Environment and Secret Manager
    env: str = Field(default="development", json_schema_extra={"env": "ENV"})
    use_secret_manager: bool = Field(
        default=False, 
        json_schema_extra={"env": "USE_SECRET_MANAGER"}
    )
    secret_manager_project_id: Optional[str] = Field(
        default=None,
        json_schema_extra={"env": "SECRET_MANAGER_PROJECT_ID"}
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", json_schema_extra={"env": "HOST"})
    port: int = Field(default=8000, json_schema_extra={"env": "PORT"})
    debug: bool = Field(default=False, json_schema_extra={"env": "DEBUG"})
    
    # JWT Configuration (with validation)
    jwt_secret: Optional[str] = Field(default=None, json_schema_extra={"env": "JWT_SECRET"})
    jwt_algorithm: str = Field(default="HS256", json_schema_extra={"env": "JWT_ALGORITHM"})
    jwt_expiration_minutes: int = Field(default=60, json_schema_extra={"env": "JWT_EXPIRATION_MINUTES"})
    
    # Google Cloud / Vertex AI
    gcp_project_id: Optional[str] = Field(default=None, json_schema_extra={"env": "GCP_PROJECT_ID"})
    vertex_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "VERTEX_API_KEY"})
    vertex_location: str = Field(default="us-central1", json_schema_extra={"env": "VERTEX_LOCATION"})
    google_application_credentials: Optional[str] = Field(
        default=None, 
        json_schema_extra={"env": "GOOGLE_APPLICATION_CREDENTIALS"}
    )
    
    # Supabase
    supabase_url: Optional[str] = Field(default=None, json_schema_extra={"env": "SUPABASE_URL"})
    supabase_anon_key: Optional[str] = Field(default=None, json_schema_extra={"env": "SUPABASE_ANON_KEY"})
    supabase_service_key: Optional[str] = Field(default=None, json_schema_extra={"env": "SUPABASE_KEY"})
    
    # Redis
    redis_host: str = Field(default="localhost", json_schema_extra={"env": "REDIS_HOST"})
    redis_port: int = Field(default=6379, json_schema_extra={"env": "REDIS_PORT"})
    redis_password: Optional[str] = Field(default=None, json_schema_extra={"env": "REDIS_PASSWORD"})
    redis_db: int = Field(default=1, json_schema_extra={"env": "REDIS_DB"})
    
    # External APIs
    elevenlabs_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "ELEVENLABS_API_KEY"})
    openai_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "OPENAI_API_KEY"})
    
    # Security Configuration
    enable_rate_limiting: bool = Field(default=True, json_schema_extra={"env": "ENABLE_RATE_LIMITING"})
    enable_security_headers: bool = Field(default=True, json_schema_extra={"env": "ENABLE_SECURITY_HEADERS"})
    enable_audit_trail: bool = Field(default=True, json_schema_extra={"env": "ENABLE_AUDIT_TRAIL"})
    
    # Rate Limiting
    rate_limit_auth_requests: int = Field(default=5, json_schema_extra={"env": "RATE_LIMIT_AUTH_REQUESTS"})
    rate_limit_auth_window: int = Field(default=60, json_schema_extra={"env": "RATE_LIMIT_AUTH_WINDOW"})
    rate_limit_chat_requests: int = Field(default=30, json_schema_extra={"env": "RATE_LIMIT_CHAT_REQUESTS"})
    rate_limit_chat_window: int = Field(default=60, json_schema_extra={"env": "RATE_LIMIT_CHAT_WINDOW"})
    
    # GDPR/HIPAA Compliance
    enable_gdpr_features: bool = Field(default=True, json_schema_extra={"env": "ENABLE_GDPR_FEATURES"})
    enable_hipaa_compliance: bool = Field(default=True, json_schema_extra={"env": "ENABLE_HIPAA_COMPLIANCE"})
    data_retention_days: int = Field(default=2555, json_schema_extra={"env": "DATA_RETENTION_DAYS"})
    audit_log_retention_days: int = Field(default=1095, json_schema_extra={"env": "AUDIT_LOG_RETENTION_DAYS"})
    
    # CORS Configuration
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        json_schema_extra={"env": "CORS_ALLOWED_ORIGINS"},
    )
    cors_allow_credentials: bool = Field(default=True, json_schema_extra={"env": "CORS_ALLOW_CREDENTIALS"})
    cors_allow_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        json_schema_extra={"env": "CORS_ALLOW_METHODS"},
    )
    cors_allow_headers: list[str] = Field(
        default_factory=lambda: ["*"],
        json_schema_extra={"env": "CORS_ALLOW_HEADERS"},
    )
    
    # Logging
    log_level: str = Field(default="INFO", json_schema_extra={"env": "LOG_LEVEL"})
    
    # A2A Configuration
    a2a_server_url: str = Field(default="http://localhost:8001", json_schema_extra={"env": "A2A_SERVER_URL"})
    a2a_websocket_url: str = Field(default="ws://localhost:8001", json_schema_extra={"env": "A2A_WEBSOCKET_URL"})
    
    @field_validator("jwt_secret")
    def validate_jwt_secret(cls, v: Optional[str], info) -> Optional[str]:
        """Validate JWT secret strength."""
        if v and len(v) < 32:
            raise ValueError(
                "JWT_SECRET must be at least 32 characters (256 bits). "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v
    
    @field_validator("cors_allowed_origins", mode="before")
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string if needed."""
        if isinstance(v, str):
            # Handle JSON-like string
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @model_validator(mode="after")
    def load_secrets_from_manager(self) -> "SecureSettings":
        """Load sensitive values from Secret Manager if enabled."""
        if not self.use_secret_manager:
            return self
        
        try:
            secret_manager = get_secret_manager()
            
            # Map of attribute names to secret keys
            secret_mappings = {
                "jwt_secret": SecretKeys.JWT_SECRET,
                "vertex_api_key": SecretKeys.VERTEX_API_KEY,
                "supabase_anon_key": SecretKeys.SUPABASE_ANON_KEY,
                "supabase_service_key": SecretKeys.SUPABASE_SERVICE_KEY,
                "redis_password": SecretKeys.REDIS_PASSWORD,
                "elevenlabs_api_key": SecretKeys.ELEVENLABS_API_KEY,
                "openai_api_key": SecretKeys.OPENAI_API_KEY,
            }
            
            # Load each secret
            for attr_name, secret_key in secret_mappings.items():
                try:
                    secret_value = secret_manager.get_secret(secret_key)
                    setattr(self, attr_name, secret_value)
                except Exception as e:
                    # Log error but don't fail initialization
                    print(f"Warning: Could not load secret {secret_key}: {e}")
                    
        except Exception as e:
            print(f"Warning: Secret Manager initialization failed: {e}")
            
        return self
    
    @model_validator(mode="after")
    def validate_production_settings(self) -> "SecureSettings":
        """Ensure production has proper security settings."""
        if self.env in ["production", "staging"]:
            # In production, certain features must be enabled
            if not self.enable_rate_limiting:
                raise ValueError("Rate limiting must be enabled in production")
            if not self.enable_security_headers:
                raise ValueError("Security headers must be enabled in production")
            if not self.enable_audit_trail:
                raise ValueError("Audit trail must be enabled in production")
            
            # Ensure we're using Secret Manager or have strong secrets
            if not self.use_secret_manager and self.jwt_secret:
                # At least validate the JWT secret is strong
                if len(self.jwt_secret) < 32:
                    raise ValueError("JWT secret is too weak for production")
                    
        return self
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL from components."""
        if self.redis_password:
            return f"redis://default:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env in ["development", "dev"]
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value, trying Secret Manager first if enabled.
        
        Args:
            key: The configuration key
            default: Default value if not found
            
        Returns:
            The configuration value
        """
        # First try to get from instance attributes
        if hasattr(self, key):
            return getattr(self, key)
        
        # Then try Secret Manager if enabled
        if self.use_secret_manager:
            try:
                secret_manager = get_secret_manager()
                return secret_manager.get_secret(key)
            except Exception:
                pass
        
        # Finally return default
        return default


# Create global settings instance
settings = SecureSettings()


# Export commonly used settings
def get_settings() -> SecureSettings:
    """Get the global settings instance."""
    return settings