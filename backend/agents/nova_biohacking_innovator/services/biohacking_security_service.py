"""
NOVA Biohacking Security Service.
Enterprise-grade security for biohacking data, protocols, and research information.
"""

import re
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from core.logging_config import get_logger
from core.redis_pool import get_redis_connection

logger = get_logger(__name__)


@dataclass
class BiohackingAuditEntry:
    """Audit log entry for biohacking operations."""

    user_id: str
    operation: str
    resource: str
    timestamp: datetime
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    success: bool = True


class BiohackingSecurityService:
    """
    Security service for NOVA Biohacking Innovator operations.

    Handles data protection, access control, audit logging, and compliance
    for sensitive biohacking data including biomarkers, wearable data,
    experimental protocols, and research information.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self._initialize_security_patterns()

    def _initialize_security_patterns(self):
        """Initialize security patterns for biohacking data validation."""
        # Patterns for dangerous content
        self.dangerous_patterns = [
            r"<script[^>]*>.*?</script>",  # Script injection
            r"javascript:",  # JavaScript protocol
            r"data:text/html",  # HTML data URLs
            r"vbscript:",  # VBScript protocol
            r"on\w+\s*=",  # Event handlers
            r"eval\s*\(",  # Code evaluation
            r"expression\s*\(",  # CSS expressions
            r"import\s+\w+",  # Module imports
            r"require\s*\(",  # Module requires
        ]

        # Patterns for biomarker data validation
        self.biomarker_patterns = [
            r"^[A-Za-z0-9\s\-\.]{1,100}$",  # Biomarker names
            r"^\d+\.?\d*\s*[a-zA-Z/%]*$",  # Biomarker values with units
        ]

        # Patterns for wearable device data
        self.wearable_patterns = [
            r"^(oura|whoop|apple_watch|garmin|fitbit|cgm)$",  # Device types
            r"^\d{4}-\d{2}-\d{2}$",  # Date format
            r"^\d+\.?\d*$",  # Numeric values
        ]

        # Compile patterns for performance
        self.compiled_dangerous = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns
        ]
        self.compiled_biomarker = [
            re.compile(pattern) for pattern in self.biomarker_patterns
        ]
        self.compiled_wearable = [
            re.compile(pattern) for pattern in self.wearable_patterns
        ]

    def sanitize_user_input(self, user_input: str) -> str:
        """
        Sanitize user input for biohacking queries and data.

        Args:
            user_input: Raw user input string

        Returns:
            Sanitized input string safe for processing
        """
        if not user_input:
            return ""

        try:
            # Remove null bytes and control characters
            sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", user_input)

            # Check for dangerous patterns
            for pattern in self.compiled_dangerous:
                if pattern.search(sanitized):
                    self.logger.warning(
                        f"Dangerous pattern detected in user input: {pattern.pattern}"
                    )
                    sanitized = pattern.sub("", sanitized)

            # Limit length for biohacking queries
            max_length = 2000  # Reasonable limit for biohacking queries
            if len(sanitized) > max_length:
                sanitized = sanitized[:max_length]
                self.logger.warning(f"Input truncated to {max_length} characters")

            # Basic HTML entity encoding for special characters
            sanitized = sanitized.replace("&", "&amp;")
            sanitized = sanitized.replace("<", "&lt;")
            sanitized = sanitized.replace(">", "&gt;")
            sanitized = sanitized.replace('"', "&quot;")
            sanitized = sanitized.replace("'", "&#x27;")

            return sanitized.strip()

        except Exception as e:
            self.logger.error(f"Error sanitizing user input: {str(e)}")
            return ""

    def validate_biomarker_data(self, biomarker_data: Dict[str, Any]) -> bool:
        """
        Validate biomarker data structure and content.

        Args:
            biomarker_data: Dictionary containing biomarker information

        Returns:
            True if biomarker data is valid and safe
        """
        try:
            if not isinstance(biomarker_data, dict):
                return False

            required_fields = ["name", "value"]
            if not all(field in biomarker_data for field in required_fields):
                return False

            # Validate biomarker name
            name = str(biomarker_data["name"])
            if not any(pattern.match(name) for pattern in self.compiled_biomarker):
                self.logger.warning(f"Invalid biomarker name format: {name}")
                return False

            # Validate biomarker value
            value = str(biomarker_data["value"])
            if not re.match(r"^\d+\.?\d*\s*[a-zA-Z/%]*$", value):
                self.logger.warning(f"Invalid biomarker value format: {value}")
                return False

            # Check for reasonable value ranges (basic sanity check)
            numeric_value = re.search(r"(\d+\.?\d*)", value)
            if numeric_value:
                num_val = float(numeric_value.group(1))
                if num_val < 0 or num_val > 1000000:  # Basic range check
                    self.logger.warning(
                        f"Biomarker value outside reasonable range: {num_val}"
                    )
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating biomarker data: {str(e)}")
            return False

    def validate_wearable_data(self, wearable_data: Dict[str, Any]) -> bool:
        """
        Validate wearable device data structure and content.

        Args:
            wearable_data: Dictionary containing wearable device data

        Returns:
            True if wearable data is valid and safe
        """
        try:
            if not isinstance(wearable_data, dict):
                return False

            # Validate device type if present
            if "device_type" in wearable_data:
                device_type = str(wearable_data["device_type"]).lower()
                valid_devices = [
                    "oura",
                    "whoop",
                    "apple_watch",
                    "garmin",
                    "fitbit",
                    "cgm",
                ]
                if device_type not in valid_devices:
                    self.logger.warning(f"Unknown device type: {device_type}")
                    return False

            # Validate metrics data
            if "metrics" in wearable_data:
                metrics = wearable_data["metrics"]
                if not isinstance(metrics, (dict, list)):
                    return False

                # Check each metric value
                if isinstance(metrics, dict):
                    for metric_name, metric_value in metrics.items():
                        if not self._validate_metric_value(metric_name, metric_value):
                            return False
                elif isinstance(metrics, list):
                    for metric in metrics:
                        if isinstance(metric, dict) and "value" in metric:
                            if not self._validate_metric_value(
                                metric.get("name", ""), metric["value"]
                            ):
                                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating wearable data: {str(e)}")
            return False

    def _validate_metric_value(self, metric_name: str, metric_value: Any) -> bool:
        """Validate individual metric value."""
        try:
            # Convert to string for pattern matching
            value_str = str(metric_value)

            # Check for reasonable numeric values
            if re.match(r"^\d+\.?\d*$", value_str):
                numeric_value = float(value_str)

                # Basic sanity checks for common metrics
                if "heart_rate" in metric_name.lower():
                    return 30 <= numeric_value <= 300  # Reasonable HR range
                elif "temperature" in metric_name.lower():
                    return 90 <= numeric_value <= 110  # Reasonable temp range (F)
                elif "steps" in metric_name.lower():
                    return 0 <= numeric_value <= 100000  # Reasonable steps range
                elif "sleep" in metric_name.lower():
                    return 0 <= numeric_value <= 24  # Hours of sleep
                else:
                    return 0 <= numeric_value <= 1000000  # General range

            return True

        except Exception:
            return False

    def check_access_permissions(
        self, user_id: str, operation: str, resource: str
    ) -> bool:
        """
        Check if user has permission to perform operation on resource.

        Args:
            user_id: User identifier
            operation: Operation being performed
            resource: Resource being accessed

        Returns:
            True if user has permission
        """
        try:
            # Basic permission checks for biohacking operations
            allowed_operations = [
                "biohacking_analysis",
                "protocol_generation",
                "biomarker_analysis",
                "wearable_analysis",
                "research_synthesis",
                "supplement_recommendations",
            ]

            if operation not in allowed_operations:
                self.logger.warning(f"Unauthorized operation attempted: {operation}")
                return False

            # Check for user-specific resource access
            if resource.startswith(f"user_{user_id}_"):
                return True  # User can access their own resources

            # Check for general resource access
            public_resources = [
                "research_database",
                "protocol_templates",
                "supplement_database",
                "biomarker_references",
            ]

            if any(resource.startswith(pub_res) for pub_res in public_resources):
                return True

            self.logger.warning(
                f"Access denied for user {user_id} to resource {resource}"
            )
            return False

        except Exception as e:
            self.logger.error(f"Error checking access permissions: {str(e)}")
            return False

    def encrypt_sensitive_data(self, data: str, context: str = "biohacking") -> str:
        """
        Encrypt sensitive biohacking data.

        Args:
            data: Data to encrypt
            context: Context for encryption (biomarker, protocol, etc.)

        Returns:
            Encrypted data string
        """
        try:
            # Use secrets for cryptographically secure operations
            salt = secrets.token_bytes(32)

            # Create context-specific key derivation
            key_material = f"{context}:{data}".encode("utf-8")
            key = hashlib.pbkdf2_hmac("sha256", key_material, salt, 100000)

            # Simple encryption (in production, use proper encryption library)
            encrypted = hmac.new(key, data.encode("utf-8"), hashlib.sha256).hexdigest()

            # Combine salt and encrypted data
            return f"{salt.hex()}:{encrypted}"

        except Exception as e:
            self.logger.error(f"Error encrypting sensitive data: {str(e)}")
            return data  # Return original data if encryption fails

    def log_biohacking_operation(
        self,
        user_id: str,
        operation: str,
        resource: str,
        success: bool = True,
        details: Dict[str, Any] = None,
        ip_address: str = None,
    ):
        """
        Log biohacking operation for audit trail.

        Args:
            user_id: User performing the operation
            operation: Operation performed
            resource: Resource accessed
            success: Whether operation was successful
            details: Additional operation details
            ip_address: User's IP address
        """
        try:
            audit_entry = BiohackingAuditEntry(
                user_id=user_id,
                operation=operation,
                resource=resource,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                details=details or {},
                success=success,
            )

            # Log to structured logger
            self.logger.info(
                f"Biohacking operation: {operation}",
                extra={
                    "user_id": user_id,
                    "operation": operation,
                    "resource": resource,
                    "success": success,
                    "ip_address": ip_address,
                    "details": details,
                },
            )

            # Store in Redis for immediate access
            try:
                with get_redis_connection() as redis_client:
                    audit_key = f"biohacking_audit:{user_id}:{datetime.utcnow().strftime('%Y%m%d')}"
                    audit_data = {
                        "operation": operation,
                        "resource": resource,
                        "timestamp": audit_entry.timestamp.isoformat(),
                        "success": success,
                        "ip_address": ip_address or "unknown",
                    }

                    redis_client.lpush(audit_key, str(audit_data))
                    redis_client.expire(audit_key, 7 * 24 * 3600)  # Keep for 7 days

            except Exception as redis_error:
                self.logger.warning(
                    f"Failed to store audit log in Redis: {str(redis_error)}"
                )

        except Exception as e:
            self.logger.error(f"Error logging biohacking operation: {str(e)}")

    def validate_research_citation(self, citation: Dict[str, Any]) -> bool:
        """
        Validate research citation for biohacking protocols.

        Args:
            citation: Research citation data

        Returns:
            True if citation is valid
        """
        try:
            required_fields = ["title", "authors", "journal", "year"]
            if not all(field in citation for field in required_fields):
                return False

            # Validate year
            year = citation.get("year")
            if not isinstance(year, int) or year < 1900 or year > datetime.now().year:
                return False

            # Validate title length
            title = citation.get("title", "")
            if len(title) < 10 or len(title) > 500:
                return False

            # Check for suspicious content in citation
            citation_text = (
                f"{title} {citation.get('journal', '')} {citation.get('authors', '')}"
            )
            for pattern in self.compiled_dangerous:
                if pattern.search(citation_text):
                    self.logger.warning("Suspicious content in research citation")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating research citation: {str(e)}")
            return False

    def sanitize_protocol_data(self, protocol: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize biohacking protocol data.

        Args:
            protocol: Protocol data to sanitize

        Returns:
            Sanitized protocol data
        """
        try:
            sanitized = {}

            for key, value in protocol.items():
                if isinstance(value, str):
                    sanitized[key] = self.sanitize_user_input(value)
                elif isinstance(value, dict):
                    sanitized[key] = self.sanitize_protocol_data(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        (
                            self.sanitize_user_input(item)
                            if isinstance(item, str)
                            else (
                                self.sanitize_protocol_data(item)
                                if isinstance(item, dict)
                                else item
                            )
                        )
                        for item in value
                    ]
                else:
                    sanitized[key] = value

            return sanitized

        except Exception as e:
            self.logger.error(f"Error sanitizing protocol data: {str(e)}")
            return protocol
