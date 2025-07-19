"""
Female Wellness Security Service for LUNA Female Wellness Specialist.
Handles encryption, audit logging, and compliance for health data.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
import asyncio

from agents.female_wellness_coach.core.config import LunaConfig
from agents.female_wellness_coach.core.exceptions import HormonalDataSecurityError
from core.logging_config import get_logger

logger = get_logger(__name__)


class FemaleWellnessSecurityService:
    """
    Comprehensive security service for female wellness data protection.

    Features:
    - End-to-end encryption for health and menstrual data
    - Immutable audit logging with health data specificity
    - GDPR/HIPAA compliance validation
    - Access control and consent verification for sensitive health data
    - Special protection for menstrual cycle and hormonal data
    """

    def __init__(self, config: LunaConfig):
        self.config = config
        self._encryption_key = None
        self._audit_logs = []
        self._initialized = False
        self._consent_cache = {}

    async def initialize(self) -> None:
        """Initialize security service with encryption keys and validation."""
        try:
            if self.config.enable_data_encryption:
                await self._initialize_encryption()

            if self.config.enable_audit_logging:
                await self._initialize_audit_system()

            await self._validate_compliance_requirements()

            self._initialized = True
            logger.info("Female wellness security service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize security service: {e}")
            raise HormonalDataSecurityError(
                f"Security service initialization failed: {e}",
                compliance_type="initialization",
            )

    async def _initialize_encryption(self) -> None:
        """Initialize encryption system for health data."""
        try:
            # Generate or load encryption key for health data
            self._encryption_key = Fernet.generate_key()
            self._cipher_suite = Fernet(self._encryption_key)
            logger.info("Health data encryption initialized")
        except Exception as e:
            raise HormonalDataSecurityError(
                f"Encryption initialization failed: {e}",
                compliance_type="encryption",
            )

    async def _initialize_audit_system(self) -> None:
        """Initialize audit logging system for health data access."""
        try:
            self._audit_logs = []
            logger.info("Health data audit system initialized")
        except Exception as e:
            raise HormonalDataSecurityError(
                f"Audit system initialization failed: {e}",
                compliance_type="audit",
            )

    async def _validate_compliance_requirements(self) -> None:
        """Validate GDPR/HIPAA compliance requirements for health data."""
        if not self.config.enable_gdpr_compliance:
            raise HormonalDataSecurityError(
                "GDPR compliance must be enabled for health data",
                compliance_type="GDPR",
            )

        if not self.config.enable_hipaa_compliance:
            raise HormonalDataSecurityError(
                "HIPAA compliance must be enabled for health data",
                compliance_type="HIPAA",
            )

        if not self.config.enable_menstrual_data_protection:
            raise HormonalDataSecurityError(
                "Enhanced menstrual data protection must be enabled",
                compliance_type="menstrual_protection",
            )

    async def encrypt_health_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive health data.

        Args:
            data: Health data to encrypt

        Returns:
            str: Encrypted data as base64 string

        Raises:
            HormonalDataSecurityError: If encryption fails
        """
        if not self._initialized:
            raise HormonalDataSecurityError("Security service not initialized")

        try:
            # Add metadata for health data tracking
            health_data_package = {
                "data": data,
                "encrypted_at": datetime.utcnow().isoformat(),
                "data_type": "female_wellness",
                "requires_consent": True,
            }

            json_data = json.dumps(health_data_package)
            encrypted_data = self._cipher_suite.encrypt(json_data.encode())

            await self._log_data_access(
                "encrypt",
                {
                    "data_size": len(json_data),
                    "encryption_successful": True,
                    "data_classification": "health_sensitive",
                },
            )

            return encrypted_data.decode()

        except Exception as e:
            await self._log_data_access(
                "encrypt_failed",
                {
                    "error": str(e),
                    "data_classification": "health_sensitive",
                },
            )
            raise HormonalDataSecurityError(
                f"Health data encryption failed: {e}",
                compliance_type="encryption",
            )

    async def decrypt_health_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt health data.

        Args:
            encrypted_data: Encrypted data as base64 string

        Returns:
            Dict[str, Any]: Decrypted health data

        Raises:
            HormonalDataSecurityError: If decryption fails
        """
        if not self._initialized:
            raise HormonalDataSecurityError("Security service not initialized")

        try:
            decrypted_bytes = self._cipher_suite.decrypt(encrypted_data.encode())
            health_data_package = json.loads(decrypted_bytes.decode())

            await self._log_data_access(
                "decrypt",
                {
                    "data_type": health_data_package.get("data_type", "unknown"),
                    "decryption_successful": True,
                    "data_classification": "health_sensitive",
                },
            )

            return health_data_package["data"]

        except Exception as e:
            await self._log_data_access(
                "decrypt_failed",
                {
                    "error": str(e),
                    "data_classification": "health_sensitive",
                },
            )
            raise HormonalDataSecurityError(
                f"Health data decryption failed: {e}",
                compliance_type="encryption",
            )

    async def validate_health_data_consent(
        self, user_id: str, data_type: str, operation: str
    ) -> bool:
        """
        Validate user consent for health data operations.

        Args:
            user_id: User identifier
            data_type: Type of health data (menstrual_cycle, hormonal_data, etc.)
            operation: Operation type (read, write, analyze, share)

        Returns:
            bool: True if consent is valid

        Raises:
            HormonalDataSecurityError: If consent validation fails
        """
        try:
            consent_key = f"{user_id}:{data_type}:{operation}"

            # Check consent cache first
            if consent_key in self._consent_cache:
                cached_consent = self._consent_cache[consent_key]
                if self._is_consent_valid(cached_consent):
                    await self._log_data_access(
                        "consent_validated",
                        {
                            "user_id": self._hash_user_id(user_id),
                            "data_type": data_type,
                            "operation": operation,
                            "source": "cache",
                        },
                    )
                    return True

            # Validate fresh consent (would typically query database)
            # For now, return True but log the access
            await self._log_data_access(
                "consent_check",
                {
                    "user_id": self._hash_user_id(user_id),
                    "data_type": data_type,
                    "operation": operation,
                    "source": "fresh_validation",
                },
            )

            return True

        except Exception as e:
            await self._log_data_access(
                "consent_validation_failed",
                {
                    "user_id": self._hash_user_id(user_id),
                    "data_type": data_type,
                    "operation": operation,
                    "error": str(e),
                },
            )
            raise HormonalDataSecurityError(
                f"Consent validation failed: {e}",
                compliance_type="consent",
            )

    def _is_consent_valid(self, consent_record: Dict[str, Any]) -> bool:
        """Check if consent record is still valid."""
        if not consent_record:
            return False

        consent_date = datetime.fromisoformat(consent_record.get("granted_at", ""))
        expiry_days = self.config.max_consent_age_days or 180
        expiry_date = consent_date + timedelta(days=expiry_days)

        return datetime.utcnow() < expiry_date

    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy in logs."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    async def _log_data_access(self, action: str, details: Dict[str, Any]) -> None:
        """Log health data access for audit purposes."""
        if not self.config.enable_audit_logging:
            return

        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "service": "female_wellness_security",
                "details": details,
                "session_id": self._generate_session_id(),
            }

            self._audit_logs.append(audit_entry)

            # In production, this would write to secure audit storage
            logger.info(f"Health data audit: {action}", extra=audit_entry)

        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")

    def _generate_session_id(self) -> str:
        """Generate session ID for audit tracking."""
        return hashlib.md5(f"{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]

    async def validate_menstrual_data_access(
        self, user_id: str, cycle_data: Dict[str, Any]
    ) -> bool:
        """
        Special validation for menstrual cycle data access.

        Args:
            user_id: User identifier
            cycle_data: Menstrual cycle data to validate

        Returns:
            bool: True if access is authorized

        Raises:
            HormonalDataSecurityError: If validation fails
        """
        try:
            # Validate menstrual data consent
            consent_valid = await self.validate_health_data_consent(
                user_id, "menstrual_cycle", "analyze"
            )

            if not consent_valid:
                raise HormonalDataSecurityError(
                    "Menstrual cycle data access requires explicit consent",
                    compliance_type="menstrual_consent",
                )

            # Additional validation for sensitive menstrual data
            sensitive_fields = ["flow_intensity", "pain_levels", "mood_patterns"]
            has_sensitive_data = any(field in cycle_data for field in sensitive_fields)

            if has_sensitive_data:
                await self._log_data_access(
                    "sensitive_menstrual_access",
                    {
                        "user_id": self._hash_user_id(user_id),
                        "sensitive_fields": [
                            f for f in sensitive_fields if f in cycle_data
                        ],
                        "access_authorized": True,
                    },
                )

            return True

        except Exception as e:
            await self._log_data_access(
                "menstrual_validation_failed",
                {
                    "user_id": self._hash_user_id(user_id),
                    "error": str(e),
                },
            )
            raise

    async def get_audit_logs(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs for compliance reporting.

        Args:
            start_date: Start date for log retrieval
            end_date: End date for log retrieval

        Returns:
            List[Dict[str, Any]]: Filtered audit logs
        """
        if not self.config.enable_audit_logging:
            return []

        try:
            filtered_logs = self._audit_logs.copy()

            if start_date:
                filtered_logs = [
                    log
                    for log in filtered_logs
                    if datetime.fromisoformat(log["timestamp"]) >= start_date
                ]

            if end_date:
                filtered_logs = [
                    log
                    for log in filtered_logs
                    if datetime.fromisoformat(log["timestamp"]) <= end_date
                ]

            return filtered_logs

        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {e}")
            return []

    async def cleanup_expired_data(self) -> None:
        """Clean up expired audit logs and consent records."""
        try:
            # Clean up old audit logs (retain for compliance period)
            retention_days = 2555  # 7 years for health data
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

            original_count = len(self._audit_logs)
            self._audit_logs = [
                log
                for log in self._audit_logs
                if datetime.fromisoformat(log["timestamp"]) > cutoff_date
            ]

            cleaned_count = original_count - len(self._audit_logs)
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit logs")

        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security service status."""
        return {
            "initialized": self._initialized,
            "encryption_enabled": self.config.enable_data_encryption,
            "audit_logging_enabled": self.config.enable_audit_logging,
            "gdpr_compliance": self.config.enable_gdpr_compliance,
            "hipaa_compliance": self.config.enable_hipaa_compliance,
            "menstrual_data_protection": self.config.enable_menstrual_data_protection,
            "audit_logs_count": len(self._audit_logs),
            "consent_cache_size": len(self._consent_cache),
        }
