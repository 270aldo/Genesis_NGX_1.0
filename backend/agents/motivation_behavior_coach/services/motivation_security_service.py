"""
Security service for SPARK Motivation Behavior Coach.
Provides data protection, audit logging, and compliance for behavioral data.
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from core.logging_config import get_logger

logger = get_logger(__name__)


class MotivationSecurityService:
    """
    Security service for protecting behavioral and motivational data.

    Implements encryption, audit logging, access control, and compliance
    features specifically for sensitive behavioral change information.
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize security service.

        Args:
            encryption_key: Encryption key for data protection (optional)
        """
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.audit_logs: List[Dict[str, Any]] = []

        logger.info("MotivationSecurityService initialized with encryption")

    def encrypt_behavioral_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive behavioral data.

        Args:
            data: Behavioral data to encrypt

        Returns:
            str: Encrypted data as string

        Raises:
            Exception: If encryption fails
        """
        try:
            json_data = json.dumps(data, default=str)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())

            self._log_security_event(
                event_type="data_encryption",
                details={"data_size": len(json_data), "success": True},
            )

            return encrypted_data.decode()

        except Exception as e:
            self._log_security_event(
                event_type="encryption_error",
                details={"error": str(e), "success": False},
            )
            raise Exception(f"Failed to encrypt behavioral data: {str(e)}")

    def decrypt_behavioral_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt behavioral data.

        Args:
            encrypted_data: Encrypted data string

        Returns:
            Dict containing decrypted data

        Raises:
            Exception: If decryption fails
        """
        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_data.encode())
            json_data = decrypted_bytes.decode()
            data = json.loads(json_data)

            self._log_security_event(
                event_type="data_decryption",
                details={"data_size": len(json_data), "success": True},
            )

            return data

        except Exception as e:
            self._log_security_event(
                event_type="decryption_error",
                details={"error": str(e), "success": False},
            )
            raise Exception(f"Failed to decrypt behavioral data: {str(e)}")

    def sanitize_user_input(self, user_input: str) -> str:
        """
        Sanitize user input to prevent injection attacks.

        Args:
            user_input: Raw user input

        Returns:
            str: Sanitized input
        """
        if not isinstance(user_input, str):
            user_input = str(user_input)

        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", "&", '"', "'", "\0", "\n", "\r", "\t"]
        sanitized = user_input

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")

        # Limit length to prevent DoS
        max_length = 10000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"User input truncated to {max_length} characters")

        self._log_security_event(
            event_type="input_sanitization",
            details={
                "original_length": len(user_input),
                "sanitized_length": len(sanitized),
                "success": True,
            },
        )

        return sanitized

    def validate_behavioral_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate behavioral data for security and integrity.

        Args:
            data: Behavioral data to validate

        Returns:
            bool: True if data is valid

        Raises:
            ValueError: If data validation fails
        """
        try:
            # Check required fields
            required_fields = ["user_id", "timestamp", "data_type"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate user_id format
            user_id = data.get("user_id")
            if not isinstance(user_id, str) or len(user_id) < 5:
                raise ValueError("Invalid user_id format")

            # Validate timestamp
            timestamp = data.get("timestamp")
            if not isinstance(timestamp, (str, int, float)):
                raise ValueError("Invalid timestamp format")

            # Validate data_type
            allowed_data_types = [
                "motivation_assessment",
                "habit_tracking",
                "goal_progress",
                "behavior_change",
                "obstacle_report",
                "coaching_session",
            ]
            data_type = data.get("data_type")
            if data_type not in allowed_data_types:
                raise ValueError(f"Invalid data_type: {data_type}")

            # Check data size limits
            data_size = len(json.dumps(data, default=str))
            max_size = 100000  # 100KB
            if data_size > max_size:
                raise ValueError(f"Data size ({data_size}) exceeds limit ({max_size})")

            self._log_security_event(
                event_type="data_validation",
                details={
                    "data_type": data_type,
                    "data_size": data_size,
                    "success": True,
                },
            )

            return True

        except Exception as e:
            self._log_security_event(
                event_type="validation_error",
                details={"error": str(e), "success": False},
            )
            raise ValueError(f"Data validation failed: {str(e)}")

    def check_access_permissions(
        self, user_id: str, operation: str, resource: str
    ) -> bool:
        """
        Check if user has permissions for specific operation.

        Args:
            user_id: User identifier
            operation: Operation type (read, write, delete, etc.)
            resource: Resource being accessed

        Returns:
            bool: True if access is allowed
        """
        try:
            # For behavioral data, users can only access their own data
            if operation in ["read", "write", "update"]:
                # Check if resource belongs to user
                if user_id in resource or resource.startswith(f"user_{user_id}"):
                    access_granted = True
                else:
                    access_granted = False
            elif operation == "delete":
                # Deletion requires additional validation
                access_granted = self._validate_deletion_request(user_id, resource)
            else:
                access_granted = False

            self._log_security_event(
                event_type="access_check",
                details={
                    "user_id": user_id,
                    "operation": operation,
                    "resource": resource,
                    "access_granted": access_granted,
                },
            )

            return access_granted

        except Exception as e:
            logger.error(f"Access permission check failed: {str(e)}")
            return False

    def _validate_deletion_request(self, user_id: str, resource: str) -> bool:
        """
        Validate deletion request for GDPR compliance.

        Args:
            user_id: User identifier
            resource: Resource to delete

        Returns:
            bool: True if deletion is allowed
        """
        # Check if user owns the resource
        if user_id not in resource:
            return False

        # Check if resource type allows deletion
        deletable_resources = [
            "motivation_data",
            "habit_data",
            "goal_data",
            "behavioral_data",
            "coaching_data",
        ]

        for resource_type in deletable_resources:
            if resource_type in resource:
                return True

        return False

    def generate_audit_hash(self, data: Dict[str, Any]) -> str:
        """
        Generate cryptographic hash for audit trail.

        Args:
            data: Data to hash

        Returns:
            str: SHA-256 hash of data
        """
        json_data = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_data.encode()).hexdigest()

    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log security event for audit trail.

        Args:
            event_type: Type of security event
            details: Event details
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "hash": None,
        }

        # Generate hash for integrity
        audit_entry["hash"] = self.generate_audit_hash(audit_entry)

        self.audit_logs.append(audit_entry)

        # Log to application logger
        logger.info(
            f"Security event: {event_type}", extra={"security_details": details}
        )

    def get_audit_logs(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs for specified time range.

        Args:
            start_time: Start of time range (optional)
            end_time: End of time range (optional)

        Returns:
            List of audit log entries
        """
        if not start_time and not end_time:
            return self.audit_logs.copy()

        filtered_logs = []
        for log_entry in self.audit_logs:
            log_time = datetime.fromisoformat(log_entry["timestamp"])

            if start_time and log_time < start_time:
                continue
            if end_time and log_time > end_time:
                continue

            filtered_logs.append(log_entry)

        return filtered_logs

    def verify_audit_integrity(self) -> bool:
        """
        Verify integrity of audit logs.

        Returns:
            bool: True if all audit logs are valid
        """
        try:
            for log_entry in self.audit_logs:
                stored_hash = log_entry.get("hash")
                if not stored_hash:
                    return False

                # Recalculate hash
                temp_entry = log_entry.copy()
                temp_entry["hash"] = None
                calculated_hash = self.generate_audit_hash(temp_entry)

                if stored_hash != calculated_hash:
                    logger.error(f"Audit log integrity violation detected")
                    return False

            return True

        except Exception as e:
            logger.error(f"Audit integrity verification failed: {str(e)}")
            return False

    def cleanup_old_logs(self, retention_days: int = 365):
        """
        Clean up old audit logs based on retention policy.

        Args:
            retention_days: Number of days to retain logs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        original_count = len(self.audit_logs)
        self.audit_logs = [
            log
            for log in self.audit_logs
            if datetime.fromisoformat(log["timestamp"]) > cutoff_date
        ]

        cleaned_count = original_count - len(self.audit_logs)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old audit log entries")
            self._log_security_event(
                event_type="log_cleanup",
                details={
                    "cleaned_entries": cleaned_count,
                    "retention_days": retention_days,
                },
            )

    def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security service status.

        Returns:
            Dict containing security status information
        """
        return {
            "encryption_enabled": True,
            "audit_logs_count": len(self.audit_logs),
            "last_audit_entry": (
                self.audit_logs[-1]["timestamp"] if self.audit_logs else None
            ),
            "audit_integrity_valid": self.verify_audit_integrity(),
            "service_status": "operational",
        }
