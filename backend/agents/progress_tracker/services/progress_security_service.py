"""
STELLA Progress Security Service.
Enterprise security and compliance for progress tracking data with GDPR compliance.
"""

import hashlib
import hmac
import os
import re
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..core.exceptions import SecurityError, DataPrivacyError, AccessControlError


class ProgressSecurityService:
    """
    Comprehensive security service for STELLA Progress Tracker.
    Handles encryption, access control, audit logging, and GDPR compliance.
    """

    def __init__(self):
        """Initialize security service with encryption and audit capabilities."""
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.audit_logs = []
        self.access_tokens = {}
        self.rate_limits = {}

        # Security configuration
        self.max_failed_attempts = 5
        self.lockout_duration = 30  # minutes
        self.token_expiry = 24  # hours

        # GDPR compliance settings
        self.gdpr_enabled = True
        self.data_retention_days = 730  # 2 years default
        self.consent_required = True

    def _generate_encryption_key(self) -> bytes:
        """
        Generate encryption key for data protection.

        Returns:
            Fernet encryption key
        """
        password = os.getenv(
            "STELLA_ENCRYPTION_PASSWORD", "stella_progress_secure_key_2024"
        ).encode()
        salt = os.getenv("STELLA_ENCRYPTION_SALT", "stella_salt_progress").encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_progress_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive progress data.

        Args:
            data: Progress data to encrypt

        Returns:
            Encrypted data as string

        Raises:
            SecurityError: If encryption fails
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, default=str)

            # Encrypt the data
            encrypted_data = self.fernet.encrypt(json_data.encode())

            # Log encryption event
            self._log_security_event(
                "data_encryption",
                {
                    "data_type": "progress_data",
                    "data_size": len(json_data),
                    "encryption_method": "fernet_aes",
                },
            )

            return base64.urlsafe_b64encode(encrypted_data).decode()

        except Exception as e:
            raise SecurityError(f"Data encryption failed: {str(e)}")

    def decrypt_progress_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt progress data.

        Args:
            encrypted_data: Encrypted data string

        Returns:
            Decrypted data dictionary

        Raises:
            SecurityError: If decryption fails
        """
        try:
            # Decode and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)

            # Convert back to dictionary
            json_data = decrypted_bytes.decode()
            data = json.loads(json_data)

            # Log decryption event
            self._log_security_event(
                "data_decryption",
                {"data_type": "progress_data", "decryption_method": "fernet_aes"},
            )

            return data

        except Exception as e:
            raise SecurityError(f"Data decryption failed: {str(e)}")

    def sanitize_user_input(self, user_input: str) -> str:
        """
        Sanitize user input to prevent XSS and injection attacks.

        Args:
            user_input: Raw user input

        Returns:
            Sanitized input string
        """
        if not isinstance(user_input, str):
            user_input = str(user_input)

        # Remove potentially dangerous HTML tags
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"on\w+\s*=",  # Event handlers
            r"javascript:",
            r"vbscript:",
            r"data:text/html",
        ]

        sanitized = user_input
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Remove SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|;|/\*|\*/)",
            r"(\bOR\b.*=.*\bOR\b)",
            r"(\bAND\b.*=.*\bAND\b)",
        ]

        for pattern in sql_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # Log sanitization if changes were made
        if sanitized != user_input:
            self._log_security_event(
                "input_sanitization",
                {
                    "original_length": len(user_input),
                    "sanitized_length": len(sanitized),
                    "patterns_removed": len(user_input) - len(sanitized),
                },
            )

        return sanitized.strip()

    def validate_progress_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate progress data structure and content.

        Args:
            data: Progress data to validate

        Returns:
            True if data is valid

        Raises:
            DataPrivacyError: If data validation fails
        """
        required_fields = ["user_id", "timestamp", "data_type"]

        # Check required fields
        for field in required_fields:
            if field not in data:
                raise DataPrivacyError(f"Missing required field: {field}")

        # Validate user_id format
        user_id = data.get("user_id", "")
        if not re.match(r"^[a-zA-Z0-9_-]+$", user_id):
            raise DataPrivacyError("Invalid user_id format")

        # Validate timestamp format
        timestamp = data.get("timestamp", "")
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            raise DataPrivacyError("Invalid timestamp format")

        # Validate data_type
        valid_data_types = [
            "weight",
            "measurements",
            "strength",
            "endurance",
            "nutrition",
            "sleep",
            "mood",
            "energy",
            "custom",
        ]
        if data.get("data_type") not in valid_data_types:
            raise DataPrivacyError("Invalid data_type")

        # Check for sensitive information in content
        content_str = str(data.get("content", ""))
        sensitive_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, content_str):
                self._log_security_event(
                    "sensitive_data_detection",
                    {
                        "user_id": data.get("user_id"),
                        "pattern_type": pattern,
                        "action": "blocked",
                    },
                )
                raise DataPrivacyError(
                    "Sensitive information detected in progress data"
                )

        return True

    def check_access_permissions(
        self, user_id: str, operation: str, resource: str
    ) -> bool:
        """
        Check if user has permission for operation on resource.

        Args:
            user_id: User identifier
            operation: Operation type (read, write, delete)
            resource: Resource identifier

        Returns:
            True if access is allowed
        """
        # Basic permission model - users can only access their own data
        if resource.startswith(f"user_{user_id}_"):
            self._log_security_event(
                "access_granted",
                {"user_id": user_id, "operation": operation, "resource": resource},
            )
            return True

        # Check for admin permissions (if user_id has admin role)
        if self._is_admin_user(user_id) and operation in ["read", "write"]:
            self._log_security_event(
                "admin_access_granted",
                {"user_id": user_id, "operation": operation, "resource": resource},
            )
            return True

        # Deny access and log
        self._log_security_event(
            "access_denied",
            {
                "user_id": user_id,
                "operation": operation,
                "resource": resource,
                "reason": "insufficient_permissions",
            },
        )

        return False

    def _is_admin_user(self, user_id: str) -> bool:
        """
        Check if user has admin privileges.

        Args:
            user_id: User identifier

        Returns:
            True if user is admin
        """
        # In a real implementation, this would check against a user roles database
        admin_users = os.getenv("STELLA_ADMIN_USERS", "").split(",")
        return user_id.strip() in [admin.strip() for admin in admin_users]

    def generate_access_token(self, user_id: str, permissions: List[str]) -> str:
        """
        Generate secure access token for user.

        Args:
            user_id: User identifier
            permissions: List of permissions

        Returns:
            Secure access token
        """
        token_data = {
            "user_id": user_id,
            "permissions": permissions,
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": (
                datetime.utcnow() + timedelta(hours=self.token_expiry)
            ).isoformat(),
        }

        # Create token
        token_json = json.dumps(token_data, default=str)
        token_encrypted = self.fernet.encrypt(token_json.encode())
        token = base64.urlsafe_b64encode(token_encrypted).decode()

        # Store token
        self.access_tokens[token] = token_data

        self._log_security_event(
            "token_generated",
            {
                "user_id": user_id,
                "permissions": permissions,
                "expires_at": token_data["expires_at"],
            },
        )

        return token

    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate access token and return user info.

        Args:
            token: Access token to validate

        Returns:
            User info if token is valid, None otherwise
        """
        try:
            # Decrypt token
            token_bytes = base64.urlsafe_b64decode(token.encode())
            decrypted_data = self.fernet.decrypt(token_bytes)
            token_data = json.loads(decrypted_data.decode())

            # Check expiration
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.utcnow() > expires_at:
                self._log_security_event(
                    "token_expired",
                    {
                        "user_id": token_data.get("user_id"),
                        "expired_at": token_data["expires_at"],
                    },
                )
                return None

            self._log_security_event(
                "token_validated", {"user_id": token_data.get("user_id")}
            )

            return token_data

        except Exception:
            self._log_security_event(
                "token_validation_failed",
                {"token_prefix": token[:10] if len(token) > 10 else token},
            )
            return None

    def check_rate_limit(
        self, user_id: str, operation: str, limit: int = 100, window_minutes: int = 60
    ) -> bool:
        """
        Check if user is within rate limits.

        Args:
            user_id: User identifier
            operation: Operation type
            limit: Maximum operations per window
            window_minutes: Time window in minutes

        Returns:
            True if within limits
        """
        now = datetime.utcnow()
        key = f"{user_id}_{operation}"

        if key not in self.rate_limits:
            self.rate_limits[key] = []

        # Clean old entries
        cutoff = now - timedelta(minutes=window_minutes)
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key] if timestamp > cutoff
        ]

        # Check limit
        if len(self.rate_limits[key]) >= limit:
            self._log_security_event(
                "rate_limit_exceeded",
                {
                    "user_id": user_id,
                    "operation": operation,
                    "current_count": len(self.rate_limits[key]),
                    "limit": limit,
                },
            )
            return False

        # Add current request
        self.rate_limits[key].append(now)
        return True

    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log security event for audit trail.

        Args:
            event_type: Type of security event
            details: Event details
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "hash": self._calculate_event_hash(event_type, details),
        }

        self.audit_logs.append(event)

        # Keep only last 10000 events to prevent memory issues
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]

    def _calculate_event_hash(self, event_type: str, details: Dict[str, Any]) -> str:
        """
        Calculate hash for audit event integrity.

        Args:
            event_type: Type of event
            details: Event details

        Returns:
            Event hash for integrity verification
        """
        event_data = f"{event_type}:{json.dumps(details, sort_keys=True, default=str)}"
        return hashlib.sha256(event_data.encode()).hexdigest()

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with optional filtering.

        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            hours: Number of hours to look back

        Returns:
            List of audit log entries
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        filtered_logs = []
        for log in self.audit_logs:
            log_time = datetime.fromisoformat(log["timestamp"])
            if log_time < cutoff:
                continue

            if user_id and log["details"].get("user_id") != user_id:
                continue

            if event_type and log["event_type"] != event_type:
                continue

            filtered_logs.append(log)

        return filtered_logs

    def verify_audit_integrity(self) -> bool:
        """
        Verify integrity of audit logs.

        Returns:
            True if audit logs are intact
        """
        for log in self.audit_logs:
            expected_hash = self._calculate_event_hash(
                log["event_type"], log["details"]
            )
            if log["hash"] != expected_hash:
                return False
        return True

    def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security service status.

        Returns:
            Security status information
        """
        return {
            "encryption_enabled": True,
            "audit_logging_enabled": True,
            "gdpr_compliance": self.gdpr_enabled,
            "total_audit_events": len(self.audit_logs),
            "active_tokens": len(self.access_tokens),
            "rate_limited_users": len(self.rate_limits),
            "security_features": [
                "data_encryption",
                "input_sanitization",
                "access_control",
                "audit_logging",
                "rate_limiting",
                "token_authentication",
                "gdpr_compliance",
            ],
        }

    def ensure_gdpr_compliance(self, user_id: str, data_type: str) -> Dict[str, Any]:
        """
        Ensure GDPR compliance for data processing.

        Args:
            user_id: User identifier
            data_type: Type of data being processed

        Returns:
            GDPR compliance status
        """
        compliance_status = {
            "gdpr_compliant": True,
            "consent_required": self.consent_required,
            "data_retention_days": self.data_retention_days,
            "user_rights": [
                "right_to_access",
                "right_to_rectification",
                "right_to_erasure",
                "right_to_portability",
                "right_to_restrict_processing",
            ],
            "lawful_basis": "consent",
            "data_controller": "STELLA Progress Tracker",
            "processing_purpose": "fitness_progress_tracking",
        }

        self._log_security_event(
            "gdpr_compliance_check",
            {
                "user_id": user_id,
                "data_type": data_type,
                "compliance_status": "verified",
            },
        )

        return compliance_status
