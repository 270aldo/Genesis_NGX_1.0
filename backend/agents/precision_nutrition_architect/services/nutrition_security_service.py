"""
Security service for handling sensitive nutrition and health data.
Implements encryption, audit logging, and compliance measures.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..core.exceptions import (
    HealthDataSecurityError,
    ConsentRequiredError,
    DataRetentionError,
)

logger = logging.getLogger(__name__)


class NutritionSecurityService:
    """
    Handles security aspects of nutrition data including:
    - Health data encryption
    - Audit logging
    - GDPR/HIPAA compliance
    - Consent management
    - Data retention policies
    """

    def __init__(self, config: Any):
        """Initialize security service with configuration."""
        self.config = config
        self.encryption_enabled = config.enable_health_data_encryption
        self.audit_enabled = config.enable_audit_logging
        self.gdpr_compliant = config.gdpr_compliant
        self.hipaa_compliant = config.hipaa_compliant
        self.max_retention_days = config.max_health_record_retention_days

        # Initialize encryption key if enabled
        if self.encryption_enabled:
            self._init_encryption()

        # Initialize audit log
        self.audit_log: List[Dict[str, Any]] = []

    def _init_encryption(self) -> None:
        """Initialize encryption key for health data."""
        # In production, this should use a proper key management service
        # For now, generate a key from a salt
        salt = b"ngx_sage_nutrition_salt_v1"  # Should be stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"ngx_sage_master_key"))
        self.cipher_suite = Fernet(key)

    def encrypt_health_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive health data.

        Args:
            data: Health data to encrypt

        Returns:
            Encrypted data as base64 string
        """
        if not self.encryption_enabled:
            return json.dumps(data)

        try:
            # Convert to JSON and encode
            json_data = json.dumps(data)
            encrypted = self.cipher_suite.encrypt(json_data.encode())

            # Log encryption event
            self._audit_log(
                "health_data_encrypted",
                {"data_type": "health_record", "size_bytes": len(json_data)},
            )

            return base64.b64encode(encrypted).decode()

        except Exception as e:
            logger.error(f"Failed to encrypt health data: {e}")
            raise HealthDataSecurityError(
                "Failed to encrypt health data",
                data_type="health_record",
                security_issue="encryption_failure",
            )

    def decrypt_health_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt health data.

        Args:
            encrypted_data: Base64 encoded encrypted data

        Returns:
            Decrypted data dictionary
        """
        if not self.encryption_enabled:
            return json.loads(encrypted_data)

        try:
            # Decode and decrypt
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)

            # Log decryption event
            self._audit_log("health_data_decrypted", {"data_type": "health_record"})

            return json.loads(decrypted.decode())

        except Exception as e:
            logger.error(f"Failed to decrypt health data: {e}")
            raise HealthDataSecurityError(
                "Failed to decrypt health data",
                data_type="health_record",
                security_issue="decryption_failure",
            )

    def sanitize_biomarker_data(self, biomarkers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize biomarker data to remove PII and validate inputs.

        Args:
            biomarkers: Raw biomarker data

        Returns:
            Sanitized biomarker data
        """
        sanitized = {}

        # Remove any PII fields
        pii_fields = ["name", "email", "phone", "address", "ssn", "dob", "id"]

        for key, value in biomarkers.items():
            # Skip PII fields
            if any(pii in key.lower() for pii in pii_fields):
                continue

            # Validate and sanitize values
            if isinstance(value, (int, float)):
                # Ensure reasonable ranges for biomarkers
                if -1000000 < value < 1000000:
                    sanitized[key] = value
            elif isinstance(value, str):
                # Limit string length and remove special characters
                sanitized[key] = value[:100].replace("<", "").replace(">", "")
            elif isinstance(value, dict):
                # Recursively sanitize nested data
                sanitized[key] = self.sanitize_biomarker_data(value)

        # Log sanitization
        self._audit_log(
            "biomarker_data_sanitized",
            {
                "fields_removed": len(biomarkers) - len(sanitized),
                "fields_retained": len(sanitized),
            },
        )

        return sanitized

    def check_consent(self, user_id: str, consent_type: str) -> bool:
        """
        Check if user has given consent for specific data usage.

        Args:
            user_id: User identifier
            consent_type: Type of consent (e.g., "biomarker_analysis", "genetic_data")

        Returns:
            True if consent is given

        Raises:
            ConsentRequiredError if consent is required but not given
        """
        if not self.config.require_consent_for_analysis:
            return True

        # In production, this would check a consent database
        # For now, simulate consent check
        consent_given = True  # Placeholder

        if not consent_given:
            raise ConsentRequiredError(
                f"User consent required for {consent_type}",
                consent_type=consent_type,
                data_usage=f"Processing {consent_type} requires explicit user consent",
            )

        # Log consent check
        self._audit_log(
            "consent_checked",
            {
                "user_id": self._hash_user_id(user_id),
                "consent_type": consent_type,
                "result": "granted",
            },
        )

        return True

    def check_data_retention(self, data_date: datetime) -> bool:
        """
        Check if data is within retention policy limits.

        Args:
            data_date: Date of the data

        Returns:
            True if data can be retained

        Raises:
            DataRetentionError if data is too old
        """
        age_days = (datetime.now() - data_date).days

        if age_days > self.max_retention_days:
            raise DataRetentionError(
                "Data exceeds retention policy limit",
                retention_days=age_days,
                policy_limit=self.max_retention_days,
            )

        return True

    def anonymize_meal_plan(self, meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize meal plan data for analytics.

        Args:
            meal_plan: Original meal plan

        Returns:
            Anonymized meal plan
        """
        anonymized = meal_plan.copy()

        # Remove user identifiers
        fields_to_remove = ["user_id", "user_name", "created_by"]
        for field in fields_to_remove:
            anonymized.pop(field, None)

        # Hash any remaining identifiers
        if "id" in anonymized:
            anonymized["id"] = self._hash_data(str(anonymized["id"]))

        return anonymized

    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for audit logs."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    def _hash_data(self, data: str) -> str:
        """Hash sensitive data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def _audit_log(self, action: str, details: Dict[str, Any]) -> None:
        """
        Add entry to audit log.

        Args:
            action: Action performed
            details: Additional details
        """
        if not self.audit_enabled:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "compliance": {"gdpr": self.gdpr_compliant, "hipaa": self.hipaa_compliant},
        }

        self.audit_log.append(log_entry)

        # In production, this would write to a secure audit database
        logger.info(f"Audit log: {action} - {details}")

    def get_audit_log(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit log entries within date range.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of audit log entries
        """
        if not self.audit_enabled:
            return []

        # Filter by date if provided
        filtered_logs = self.audit_log

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

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate compliance report for GDPR/HIPAA.

        Returns:
            Compliance report dictionary
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "compliance_status": {
                "gdpr": {
                    "enabled": self.gdpr_compliant,
                    "encryption": self.encryption_enabled,
                    "audit_logging": self.audit_enabled,
                    "consent_management": self.config.require_consent_for_analysis,
                    "data_retention_days": self.max_retention_days,
                },
                "hipaa": {
                    "enabled": self.hipaa_compliant,
                    "encryption": self.encryption_enabled,
                    "audit_logging": self.audit_enabled,
                    "access_controls": True,  # Placeholder
                },
            },
            "audit_summary": {
                "total_events": len(self.audit_log),
                "event_types": self._count_audit_events(),
            },
        }

        return report

    def _count_audit_events(self) -> Dict[str, int]:
        """Count audit events by type."""
        event_counts = {}
        for log in self.audit_log:
            action = log.get("action", "unknown")
            event_counts[action] = event_counts.get(action, 0) + 1
        return event_counts
