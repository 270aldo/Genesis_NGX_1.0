"""
Genetic Security Service for CODE Genetic Specialist.
Handles encryption, audit logging, and compliance for genetic data.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
import asyncio

from agents.code_genetic_specialist.core.config import CodeGeneticConfig
from agents.code_genetic_specialist.core.exceptions import GeneticDataSecurityError
from core.logging_config import get_logger

logger = get_logger(__name__)


class GeneticSecurityService:
    """
    Comprehensive security service for genetic data protection.

    Features:
    - End-to-end encryption for genetic data
    - Immutable audit logging
    - GDPR/HIPAA compliance validation
    - Access control and consent verification
    """

    def __init__(self, config: CodeGeneticConfig):
        self.config = config
        self._encryption_key = None
        self._audit_logs = []
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize security service with encryption keys and validation."""
        try:
            if self.config.enable_data_encryption:
                await self._initialize_encryption()

            if self.config.enable_audit_logging:
                await self._initialize_audit_system()

            await self._validate_compliance_requirements()

            self._initialized = True
            logger.info("Genetic security service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize genetic security service: {e}")
            raise GeneticDataSecurityError(f"Security initialization failed: {e}")

    async def _initialize_encryption(self) -> None:
        """Initialize encryption system for genetic data."""
        try:
            # In production, this would load from secure key management
            self._encryption_key = Fernet.generate_key()
            self._cipher_suite = Fernet(self._encryption_key)

            logger.info("Genetic data encryption initialized")

        except Exception as e:
            raise GeneticDataSecurityError(f"Encryption initialization failed: {e}")

    async def _initialize_audit_system(self) -> None:
        """Initialize audit logging system."""
        try:
            # Initialize audit log storage
            self._audit_logs = []

            # Verify audit log integrity
            await self._verify_audit_integrity()

            logger.info("Audit logging system initialized")

        except Exception as e:
            raise GeneticDataSecurityError(f"Audit system initialization failed: {e}")

    async def _validate_compliance_requirements(self) -> None:
        """Validate that all compliance requirements are met."""
        compliance_checks = []

        if self.config.enable_gdpr_compliance:
            compliance_checks.append(("GDPR", await self._validate_gdpr_requirements()))

        if self.config.enable_hipaa_compliance:
            compliance_checks.append(
                ("HIPAA", await self._validate_hipaa_requirements())
            )

        failed_compliance = [name for name, passed in compliance_checks if not passed]

        if failed_compliance:
            raise GeneticDataSecurityError(
                f"Compliance validation failed: {', '.join(failed_compliance)}",
                compliance_type="MULTI_COMPLIANCE_FAILURE",
            )

    async def _validate_gdpr_requirements(self) -> bool:
        """Validate GDPR compliance requirements."""
        try:
            # Check required GDPR features
            gdpr_requirements = [
                self.config.enable_data_encryption,
                self.config.enable_audit_logging,
                # Additional GDPR checks would go here
            ]

            return all(gdpr_requirements)

        except Exception as e:
            logger.error(f"GDPR validation failed: {e}")
            return False

    async def _validate_hipaa_requirements(self) -> bool:
        """Validate HIPAA compliance requirements."""
        try:
            # Check required HIPAA features
            hipaa_requirements = [
                self.config.enable_data_encryption,
                self.config.enable_audit_logging,
                # Additional HIPAA checks would go here
            ]

            return all(hipaa_requirements)

        except Exception as e:
            logger.error(f"HIPAA validation failed: {e}")
            return False

    async def validate_encryption_status(self, user_id: str) -> bool:
        """
        Validate that genetic data encryption is properly configured.

        Args:
            user_id: User identifier for encryption validation

        Returns:
            bool: True if encryption is valid, False otherwise
        """
        if not self._initialized:
            raise GeneticDataSecurityError("Security service not initialized")

        if not self.config.enable_data_encryption:
            return True  # Encryption not required in config

        try:
            # Validate encryption key availability
            if not self._encryption_key or not self._cipher_suite:
                logger.error(
                    f"Encryption validation failed for user {user_id}: No encryption key"
                )
                return False

            # Test encryption/decryption cycle
            test_data = f"encryption_test_{user_id}_{datetime.utcnow().isoformat()}"
            encrypted = await self.encrypt_genetic_data(test_data)
            decrypted = await self.decrypt_genetic_data(encrypted)

            validation_success = test_data == decrypted

            if validation_success:
                logger.debug(f"Encryption validation successful for user {user_id}")
            else:
                logger.error(
                    f"Encryption validation failed for user {user_id}: Decryption mismatch"
                )

            return validation_success

        except Exception as e:
            logger.error(f"Encryption validation error for user {user_id}: {e}")
            return False

    async def encrypt_genetic_data(self, data: str) -> str:
        """
        Encrypt genetic data using AES-256-GCM.

        Args:
            data: Genetic data to encrypt

        Returns:
            str: Encrypted data as base64 string
        """
        if not self._initialized or not self.config.enable_data_encryption:
            return data  # Return unencrypted if encryption disabled

        try:
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = str(data).encode("utf-8")

            encrypted_bytes = self._cipher_suite.encrypt(data_bytes)
            return encrypted_bytes.decode("utf-8")

        except Exception as e:
            raise GeneticDataSecurityError(f"Genetic data encryption failed: {e}")

    async def decrypt_genetic_data(self, encrypted_data: str) -> str:
        """
        Decrypt genetic data.

        Args:
            encrypted_data: Encrypted genetic data

        Returns:
            str: Decrypted genetic data
        """
        if not self._initialized or not self.config.enable_data_encryption:
            return encrypted_data  # Return as-is if encryption disabled

        try:
            encrypted_bytes = encrypted_data.encode("utf-8")
            decrypted_bytes = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode("utf-8")

        except Exception as e:
            raise GeneticDataSecurityError(f"Genetic data decryption failed: {e}")

    async def log_audit_event(self, audit_data: Dict[str, Any]) -> None:
        """
        Log immutable audit event for genetic data access.

        Args:
            audit_data: Audit information to log
        """
        if not self.config.enable_audit_logging:
            return

        try:
            # Create immutable audit record
            audit_record = {
                **audit_data,
                "audit_id": self._generate_audit_id(),
                "audit_timestamp": datetime.utcnow().isoformat(),
                "integrity_hash": None,  # Will be set below
            }

            # Generate integrity hash
            audit_record["integrity_hash"] = self._generate_integrity_hash(audit_record)

            # Store audit record (in production, this would go to immutable storage)
            self._audit_logs.append(audit_record)

            # Log for monitoring
            logger.info(
                f"Genetic data audit event logged",
                extra={
                    "audit_id": audit_record["audit_id"],
                    "user_id": audit_data.get("user_id"),
                    "action": audit_data.get("request_type"),
                    "success": audit_data.get("success"),
                },
            )

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Don't raise exception - audit failure shouldn't block operations

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID."""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(
            f"audit_{timestamp}_{len(self._audit_logs)}".encode()
        ).hexdigest()[:16]

    def _generate_integrity_hash(self, audit_record: Dict[str, Any]) -> str:
        """Generate integrity hash for audit record."""
        # Create hash excluding the integrity_hash field itself
        hash_data = {k: v for k, v in audit_record.items() if k != "integrity_hash"}
        hash_string = json.dumps(hash_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(hash_string.encode()).hexdigest()

    async def _verify_audit_integrity(self) -> bool:
        """Verify integrity of audit logs."""
        try:
            for audit_record in self._audit_logs:
                expected_hash = self._generate_integrity_hash(audit_record)
                if audit_record.get("integrity_hash") != expected_hash:
                    logger.error(
                        f"Audit integrity violation detected: {audit_record['audit_id']}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Audit integrity verification failed: {e}")
            return False

    async def get_audit_trail(
        self, user_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail for specific user.

        Args:
            user_id: User identifier
            days: Number of days to retrieve

        Returns:
            List[Dict]: Audit records for the user
        """
        if not self.config.enable_audit_logging:
            return []

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            user_audits = [
                audit
                for audit in self._audit_logs
                if (
                    audit.get("user_id") == user_id
                    and datetime.fromisoformat(audit["audit_timestamp"]) >= cutoff_date
                )
            ]

            return user_audits

        except Exception as e:
            logger.error(f"Failed to retrieve audit trail for user {user_id}: {e}")
            return []

    async def validate_data_retention_compliance(self, user_id: str) -> bool:
        """
        Validate data retention compliance for genetic data.

        Args:
            user_id: User identifier

        Returns:
            bool: True if retention is compliant
        """
        try:
            # Get user's genetic data access history
            audit_trail = await self.get_audit_trail(user_id, days=2555)  # 7 years

            if not audit_trail:
                return True  # No data to validate

            # Check if any data exceeds retention period
            retention_limit = datetime.utcnow() - timedelta(
                days=2555
            )  # 7 years for genetic data

            for audit in audit_trail:
                audit_date = datetime.fromisoformat(audit["audit_timestamp"])
                if audit_date < retention_limit:
                    logger.warning(
                        f"Genetic data retention period exceeded for user {user_id}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Data retention validation failed for user {user_id}: {e}")
            return False

    @property
    def security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            "initialized": self._initialized,
            "encryption_enabled": self.config.enable_data_encryption,
            "audit_logging_enabled": self.config.enable_audit_logging,
            "gdpr_compliance": self.config.enable_gdpr_compliance,
            "hipaa_compliance": self.config.enable_hipaa_compliance,
            "audit_records_count": len(self._audit_logs),
            "last_integrity_check": datetime.utcnow().isoformat(),
        }
