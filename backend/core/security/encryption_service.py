"""
Centralized encryption service using AES-256-GCM.

This module provides secure encryption and decryption services for sensitive data,
using industry-standard AES-256-GCM encryption with proper key management.
"""

import os
import base64
import json
from typing import Any, Dict, Optional, Union
from datetime import datetime
import logging

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from core.security.secrets_manager import get_secret, SecretKeys

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Provides AES-256-GCM encryption for sensitive data.
    
    Features:
    - AES-256-GCM authenticated encryption
    - Automatic key rotation support
    - Secure key derivation with PBKDF2
    - JSON serialization for complex data types
    - Base64 encoding for storage
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize the encryption service.
        
        Args:
            key: Optional encryption key. If not provided, will be loaded from secrets.
        """
        if key:
            self._key = key
        else:
            self._key = self._load_or_generate_key()
        
        self._cipher = AESGCM(self._key)
        self._nonce_size = 12  # 96 bits for GCM
    
    def _load_or_generate_key(self) -> bytes:
        """Load encryption key from secrets or generate a new one."""
        try:
            # Try to load from Secret Manager
            key_b64 = get_secret(SecretKeys.ENCRYPTION_KEY)
            if key_b64:
                return base64.b64decode(key_b64)
        except Exception as e:
            logger.warning(f"Could not load encryption key from secrets: {e}")
        
        # Generate a new key if not found
        logger.warning("Generating new encryption key - this should only happen once!")
        key = AESGCM.generate_key(bit_length=256)
        
        # Log the key for manual storage (only in development!)
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Generated encryption key (base64): {base64.b64encode(key).decode()}")
            logger.info("Store this key in Secret Manager or .env as ENCRYPTION_KEY")
        
        return key
    
    def encrypt(self, plaintext: Union[str, bytes], associated_data: Optional[bytes] = None) -> str:
        """
        Encrypt data using AES-256-GCM.
        
        Args:
            plaintext: The data to encrypt (string or bytes)
            associated_data: Optional additional authenticated data
            
        Returns:
            Base64-encoded encrypted data with nonce prepended
        """
        # Convert string to bytes if needed
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Generate a random nonce
        nonce = os.urandom(self._nonce_size)
        
        # Encrypt the data
        ciphertext = self._cipher.encrypt(nonce, plaintext, associated_data)
        
        # Combine nonce and ciphertext
        encrypted = nonce + ciphertext
        
        # Return base64-encoded result
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, ciphertext_b64: str, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data encrypted with AES-256-GCM.
        
        Args:
            ciphertext_b64: Base64-encoded encrypted data with nonce
            associated_data: Optional additional authenticated data (must match encryption)
            
        Returns:
            Decrypted data as bytes
            
        Raises:
            ValueError: If decryption fails (wrong key, tampered data, etc.)
        """
        try:
            # Decode from base64
            encrypted = base64.b64decode(ciphertext_b64)
            
            # Extract nonce and ciphertext
            nonce = encrypted[:self._nonce_size]
            ciphertext = encrypted[self._nonce_size:]
            
            # Decrypt the data
            plaintext = self._cipher.decrypt(nonce, ciphertext, associated_data)
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data") from e
    
    def encrypt_string(self, plaintext: str, associated_data: Optional[str] = None) -> str:
        """
        Encrypt a string value.
        
        Args:
            plaintext: The string to encrypt
            associated_data: Optional additional authenticated data
            
        Returns:
            Base64-encoded encrypted string
        """
        ad = associated_data.encode('utf-8') if associated_data else None
        return self.encrypt(plaintext, ad)
    
    def decrypt_string(self, ciphertext_b64: str, associated_data: Optional[str] = None) -> str:
        """
        Decrypt a string value.
        
        Args:
            ciphertext_b64: Base64-encoded encrypted string
            associated_data: Optional additional authenticated data
            
        Returns:
            Decrypted string
        """
        ad = associated_data.encode('utf-8') if associated_data else None
        plaintext_bytes = self.decrypt(ciphertext_b64, ad)
        return plaintext_bytes.decode('utf-8')
    
    def encrypt_json(self, data: Any, associated_data: Optional[str] = None) -> str:
        """
        Encrypt JSON-serializable data.
        
        Args:
            data: Any JSON-serializable data (dict, list, etc.)
            associated_data: Optional additional authenticated data
            
        Returns:
            Base64-encoded encrypted JSON data
        """
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return self.encrypt_string(json_str, associated_data)
    
    def decrypt_json(self, ciphertext_b64: str, associated_data: Optional[str] = None) -> Any:
        """
        Decrypt JSON data.
        
        Args:
            ciphertext_b64: Base64-encoded encrypted JSON data
            associated_data: Optional additional authenticated data
            
        Returns:
            Deserialized JSON data
        """
        json_str = self.decrypt_string(ciphertext_b64, associated_data)
        return json.loads(json_str)
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Derive an encryption key from a password using PBKDF2.
        
        Args:
            password: The password to derive from
            salt: Optional salt (will be generated if not provided)
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)  # 128-bit salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # OWASP recommendation
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def encrypt_with_metadata(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Encrypt data with metadata for versioning and key rotation.
        
        Args:
            data: The data to encrypt
            metadata: Optional metadata to include
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        # Prepare metadata
        meta = metadata or {}
        meta.update({
            'version': '1.0',
            'algorithm': 'AES-256-GCM',
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Serialize metadata for AAD
        aad = json.dumps(meta, separators=(',', ':')).encode('utf-8')
        
        # Encrypt the data
        encrypted = self.encrypt_json(data, associated_data=aad.decode('utf-8'))
        
        return {
            'encrypted_data': encrypted,
            'metadata': meta,
        }
    
    def decrypt_with_metadata(self, encrypted_obj: Dict[str, Any]) -> Any:
        """
        Decrypt data that was encrypted with metadata.
        
        Args:
            encrypted_obj: Dictionary with encrypted_data and metadata
            
        Returns:
            Decrypted data
        """
        encrypted_data = encrypted_obj['encrypted_data']
        metadata = encrypted_obj['metadata']
        
        # Recreate AAD from metadata
        aad = json.dumps(metadata, separators=(',', ':')).encode('utf-8')
        
        # Decrypt the data
        return self.decrypt_json(encrypted_data, associated_data=aad.decode('utf-8'))


class FieldEncryption:
    """
    Helper class for encrypting specific fields in dictionaries.
    
    Useful for encrypting only sensitive fields while leaving others in plaintext.
    """
    
    def __init__(self, encryption_service: Optional[EncryptionService] = None):
        """
        Initialize field encryption helper.
        
        Args:
            encryption_service: Optional EncryptionService instance
        """
        self.encryption = encryption_service or EncryptionService()
    
    def encrypt_fields(self, data: Dict[str, Any], fields_to_encrypt: list[str]) -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing data
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dictionary with specified fields encrypted
        """
        result = data.copy()
        
        for field in fields_to_encrypt:
            if field in result and result[field] is not None:
                # Encrypt the field value
                if isinstance(result[field], (dict, list)):
                    encrypted = self.encryption.encrypt_json(result[field])
                else:
                    encrypted = self.encryption.encrypt_string(str(result[field]))
                
                # Store encrypted value with marker
                result[field] = {
                    '_encrypted': True,
                    'value': encrypted,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return result
    
    def decrypt_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt encrypted fields in a dictionary.
        
        Args:
            data: Dictionary potentially containing encrypted fields
            
        Returns:
            Dictionary with encrypted fields decrypted
        """
        result = data.copy()
        
        for field, value in data.items():
            if isinstance(value, dict) and value.get('_encrypted'):
                try:
                    # Decrypt the field
                    encrypted_value = value['value']
                    
                    # Try JSON first, fall back to string
                    try:
                        decrypted = self.encryption.decrypt_json(encrypted_value)
                    except json.JSONDecodeError:
                        decrypted = self.encryption.decrypt_string(encrypted_value)
                    
                    result[field] = decrypted
                    
                except Exception as e:
                    logger.error(f"Failed to decrypt field {field}: {e}")
                    # Leave the field encrypted if decryption fails
        
        return result


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get the global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# Convenience functions
def encrypt_data(data: Any) -> str:
    """Encrypt data using the global encryption service."""
    return get_encryption_service().encrypt_json(data)


def decrypt_data(encrypted: str) -> Any:
    """Decrypt data using the global encryption service."""
    return get_encryption_service().decrypt_json(encrypted)


def encrypt_string(plaintext: str) -> str:
    """Encrypt a string using the global encryption service."""
    return get_encryption_service().encrypt_string(plaintext)


def decrypt_string(ciphertext: str) -> str:
    """Decrypt a string using the global encryption service."""
    return get_encryption_service().decrypt_string(ciphertext)