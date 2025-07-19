"""
Google Secret Manager integration for secure credential management.

This module provides a centralized way to manage secrets using Google Secret Manager,
ensuring that sensitive credentials are never stored in code or configuration files.
"""

import os
from typing import Optional, Dict, Any
from functools import lru_cache
import logging

from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class SecretManagerConfig(BaseSettings):
    """Configuration for Google Secret Manager."""
    
    use_secret_manager: bool = False
    secret_manager_project_id: Optional[str] = None
    secret_prefix: str = "ngx-agents"
    
    class Config:
        env_file = ".env"


class SecretManager:
    """
    Manages secrets using Google Secret Manager.
    
    In development, falls back to environment variables.
    In production, uses Google Secret Manager for all sensitive data.
    """
    
    def __init__(self, config: Optional[SecretManagerConfig] = None):
        """Initialize the Secret Manager."""
        self.config = config or SecretManagerConfig()
        self._client = None
        self._cache: Dict[str, str] = {}
        
        if self.config.use_secret_manager:
            try:
                from google.cloud import secretmanager
                self._client = secretmanager.SecretManagerServiceClient()
                logger.info("Google Secret Manager initialized successfully")
            except ImportError:
                logger.error(
                    "google-cloud-secret-manager not installed. "
                    "Run: pip install google-cloud-secret-manager"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to initialize Secret Manager: {e}")
                raise
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Retrieve a secret value.
        
        Args:
            secret_id: The ID of the secret to retrieve
            version: The version of the secret (default: "latest")
            
        Returns:
            The secret value as a string
            
        Raises:
            ValueError: If the secret is not found
            Exception: If there's an error accessing the secret
        """
        # Check cache first
        cache_key = f"{secret_id}:{version}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try environment variable first (for development)
        env_value = os.getenv(secret_id.upper())
        if env_value and not self.config.use_secret_manager:
            logger.debug(f"Using environment variable for {secret_id}")
            return env_value
        
        # Use Secret Manager in production
        if self.config.use_secret_manager and self._client:
            try:
                # Build the resource name
                project_id = self.config.secret_manager_project_id
                secret_name = f"{self.config.secret_prefix}-{secret_id}"
                name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"
                
                # Access the secret
                response = self._client.access_secret_version(request={"name": name})
                secret_value = response.payload.data.decode("UTF-8")
                
                # Cache the value
                self._cache[cache_key] = secret_value
                logger.debug(f"Retrieved secret {secret_id} from Secret Manager")
                
                return secret_value
                
            except Exception as e:
                logger.error(f"Error accessing secret {secret_id}: {e}")
                # Fall back to environment variable if available
                if env_value:
                    logger.warning(f"Falling back to environment variable for {secret_id}")
                    return env_value
                raise
        
        # If we get here, the secret wasn't found
        raise ValueError(f"Secret {secret_id} not found in environment or Secret Manager")
    
    def create_secret(self, secret_id: str, secret_value: str) -> None:
        """
        Create a new secret in Secret Manager.
        
        Args:
            secret_id: The ID for the new secret
            secret_value: The value to store
            
        Note:
            This method is only available when using Secret Manager in production.
        """
        if not self.config.use_secret_manager or not self._client:
            raise RuntimeError("Secret Manager is not enabled")
        
        try:
            project_id = self.config.secret_manager_project_id
            parent = f"projects/{project_id}"
            secret_name = f"{self.config.secret_prefix}-{secret_id}"
            
            # Create the secret
            secret = {
                "replication": {
                    "automatic": {}
                }
            }
            
            response = self._client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_name,
                    "secret": secret
                }
            )
            
            # Add the secret version
            self._client.add_secret_version(
                request={
                    "parent": response.name,
                    "payload": {"data": secret_value.encode("UTF-8")}
                }
            )
            
            logger.info(f"Created secret {secret_id} in Secret Manager")
            
        except Exception as e:
            logger.error(f"Error creating secret {secret_id}: {e}")
            raise
    
    def update_secret(self, secret_id: str, secret_value: str) -> None:
        """
        Update an existing secret by adding a new version.
        
        Args:
            secret_id: The ID of the secret to update
            secret_value: The new value
        """
        if not self.config.use_secret_manager or not self._client:
            raise RuntimeError("Secret Manager is not enabled")
        
        try:
            project_id = self.config.secret_manager_project_id
            secret_name = f"{self.config.secret_prefix}-{secret_id}"
            parent = f"projects/{project_id}/secrets/{secret_name}"
            
            # Add a new version
            self._client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": secret_value.encode("UTF-8")}
                }
            )
            
            # Clear cache for this secret
            cache_keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{secret_id}:")]
            for key in cache_keys_to_remove:
                del self._cache[key]
            
            logger.info(f"Updated secret {secret_id} in Secret Manager")
            
        except Exception as e:
            logger.error(f"Error updating secret {secret_id}: {e}")
            raise
    
    def delete_secret(self, secret_id: str) -> None:
        """
        Delete a secret from Secret Manager.
        
        Args:
            secret_id: The ID of the secret to delete
            
        Warning:
            This permanently deletes the secret and all its versions.
        """
        if not self.config.use_secret_manager or not self._client:
            raise RuntimeError("Secret Manager is not enabled")
        
        try:
            project_id = self.config.secret_manager_project_id
            secret_name = f"{self.config.secret_prefix}-{secret_id}"
            name = f"projects/{project_id}/secrets/{secret_name}"
            
            # Delete the secret
            self._client.delete_secret(request={"name": name})
            
            # Clear cache for this secret
            cache_keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{secret_id}:")]
            for key in cache_keys_to_remove:
                del self._cache[key]
            
            logger.info(f"Deleted secret {secret_id} from Secret Manager")
            
        except Exception as e:
            logger.error(f"Error deleting secret {secret_id}: {e}")
            raise
    
    def list_secrets(self) -> list[str]:
        """
        List all secrets in the project.
        
        Returns:
            A list of secret IDs
        """
        if not self.config.use_secret_manager or not self._client:
            # In development, return environment variables that look like secrets
            return [
                key.lower() for key in os.environ.keys()
                if any(pattern in key.upper() for pattern in [
                    "KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL"
                ])
            ]
        
        try:
            project_id = self.config.secret_manager_project_id
            parent = f"projects/{project_id}"
            
            # List all secrets
            secrets = []
            for secret in self._client.list_secrets(request={"parent": parent}):
                # Extract the secret ID from the full name
                secret_id = secret.name.split("/")[-1]
                if secret_id.startswith(self.config.secret_prefix):
                    # Remove the prefix
                    clean_id = secret_id[len(self.config.secret_prefix) + 1:]
                    secrets.append(clean_id)
            
            return secrets
            
        except Exception as e:
            logger.error(f"Error listing secrets: {e}")
            raise


# Global instance
_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Get the global SecretManager instance."""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager


def get_secret(secret_id: str) -> str:
    """
    Convenience function to get a secret value.
    
    Args:
        secret_id: The ID of the secret to retrieve
        
    Returns:
        The secret value
    """
    return get_secret_manager().get_secret(secret_id)


# Common secret IDs
class SecretKeys:
    """Common secret key constants."""
    
    # Authentication
    JWT_SECRET = "jwt_secret"
    
    # Google Cloud
    VERTEX_API_KEY = "vertex_api_key"
    GCP_PROJECT_ID = "gcp_project_id"
    
    # Supabase
    SUPABASE_URL = "supabase_url"
    SUPABASE_ANON_KEY = "supabase_anon_key"
    SUPABASE_SERVICE_KEY = "supabase_service_key"
    
    # Redis
    REDIS_PASSWORD = "redis_password"
    
    # External APIs
    ELEVENLABS_API_KEY = "elevenlabs_api_key"
    OPENAI_API_KEY = "openai_api_key"
    
    # Encryption
    ENCRYPTION_KEY = "encryption_key"
    ENCRYPTION_SALT = "encryption_salt"