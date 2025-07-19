"""
Base Security Service for NGX Agents
====================================

This module provides a base class for all security services in the NGX ecosystem,
ensuring consistent security patterns and compliance across all agents.

Features:
- Data validation and sanitization
- Encryption/decryption support
- GDPR/HIPAA compliance checks
- Audit logging
- Rate limiting
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import hashlib
import json
import re

from core.logging_config import get_logger
from core.redis_pool import RedisPoolManager

logger = get_logger(__name__)


class BaseSecurityService(ABC):
    """
    Base class for all security services in NGX agents.
    
    Provides common security functionality for:
    - Data validation and sanitization
    - Privacy compliance (GDPR/HIPAA)
    - Audit logging
    - Rate limiting
    - Encryption support
    """
    
    # Common PII patterns to detect
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{4,6}",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    }
    
    def __init__(
        self,
        service_name: str,
        compliance_level: str = "standard",  # standard, hipaa, gdpr
        enable_encryption: bool = True,
        redis_manager: Optional[RedisPoolManager] = None
    ):
        """
        Initialize base security service.
        
        Args:
            service_name: Name of the security service
            compliance_level: Compliance level (standard, hipaa, gdpr)
            enable_encryption: Whether to enable data encryption
            redis_manager: Optional Redis manager for rate limiting
        """
        self.service_name = service_name
        self.compliance_level = compliance_level
        self.enable_encryption = enable_encryption
        self.redis = redis_manager or RedisPoolManager.get_instance()
        
        # Audit log storage
        self._audit_logs: List[Dict[str, Any]] = []
        
        logger.info(
            f"Initialized {service_name} with compliance level: {compliance_level}, "
            f"encryption: {enable_encryption}"
        )
    
    # ==================== Abstract Methods ====================
    
    @abstractmethod
    def get_sensitive_fields(self) -> Set[str]:
        """Get list of sensitive fields that need protection."""
        pass
    
    @abstractmethod
    def validate_business_rules(self, data: Dict[str, Any]) -> List[str]:
        """Validate business-specific rules. Returns list of validation errors."""
        pass
    
    # ==================== Common Security Methods ====================
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize data.
        
        Args:
            data: Data to validate
            
        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []
        
        try:
            # Check for required fields
            missing_fields = self._check_required_fields(data)
            if missing_fields:
                errors.extend([f"Missing required field: {field}" for field in missing_fields])
            
            # Sanitize input
            sanitized_data = self._sanitize_data(data)
            
            # Check for PII
            pii_found = self._detect_pii(sanitized_data)
            if pii_found:
                warnings.extend([f"PII detected in field '{field}': {pii_type}" 
                               for field, pii_type in pii_found.items()])
            
            # Business rule validation
            business_errors = self.validate_business_rules(sanitized_data)
            errors.extend(business_errors)
            
            # Compliance checks
            compliance_issues = self._check_compliance(sanitized_data)
            if compliance_issues:
                errors.extend(compliance_issues)
            
            # Log validation attempt
            self._audit_log("validation", {
                "data_keys": list(data.keys()),
                "errors_count": len(errors),
                "warnings_count": len(warnings),
                "compliance_level": self.compliance_level
            })
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "sanitized_data": sanitized_data if len(errors) == 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "sanitized_data": None
            }
    
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in data.
        
        Args:
            data: Data containing sensitive fields
            
        Returns:
            Data with encrypted sensitive fields
        """
        if not self.enable_encryption:
            return data
        
        encrypted_data = data.copy()
        sensitive_fields = self.get_sensitive_fields()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                # Simple encryption placeholder - in production use proper encryption
                encrypted_value = self._encrypt_field(encrypted_data[field])
                encrypted_data[field] = encrypted_value
                encrypted_data[f"{field}_encrypted"] = True
        
        self._audit_log("encryption", {
            "fields_encrypted": list(sensitive_fields & set(data.keys()))
        })
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in data.
        
        Args:
            data: Data containing encrypted fields
            
        Returns:
            Data with decrypted sensitive fields
        """
        if not self.enable_encryption:
            return data
        
        decrypted_data = data.copy()
        sensitive_fields = self.get_sensitive_fields()
        
        for field in sensitive_fields:
            if f"{field}_encrypted" in decrypted_data and decrypted_data.get(f"{field}_encrypted"):
                # Simple decryption placeholder - in production use proper decryption
                decrypted_value = self._decrypt_field(decrypted_data[field])
                decrypted_data[field] = decrypted_value
                del decrypted_data[f"{field}_encrypted"]
        
        return decrypted_data
    
    async def check_rate_limit(self, user_id: str, action: str, limit: int = 100) -> bool:
        """
        Check if user has exceeded rate limit for an action.
        
        Args:
            user_id: User identifier
            action: Action being performed
            limit: Maximum allowed actions per hour
            
        Returns:
            True if within limit, False if exceeded
        """
        if not self.redis or not await self.redis.is_connected():
            # If Redis not available, allow action
            return True
        
        try:
            key = f"rate_limit:{self.service_name}:{action}:{user_id}"
            current_hour = datetime.now().strftime("%Y%m%d%H")
            rate_key = f"{key}:{current_hour}"
            
            # Increment counter
            count = await self.redis.incr(rate_key)
            
            # Set expiry on first increment
            if count == 1:
                await self.redis.expire(rate_key, 3600)  # 1 hour expiry
            
            if count > limit:
                self._audit_log("rate_limit_exceeded", {
                    "user_id": user_id,
                    "action": action,
                    "count": count,
                    "limit": limit
                })
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # On error, allow action
            return True
    
    def audit_access(self, user_id: str, resource: str, action: str, result: str) -> None:
        """
        Log access attempt for audit purposes.
        
        Args:
            user_id: User performing the action
            resource: Resource being accessed
            action: Action performed (read, write, delete)
            result: Result of the action (success, denied, error)
        """
        self._audit_log("access", {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check data for compliance issues.
        
        Args:
            data: Data to check
            
        Returns:
            Dict with compliance check results
        """
        issues = self._check_compliance(data)
        
        return {
            "compliant": len(issues) == 0,
            "level": self.compliance_level,
            "issues": issues,
            "recommendations": self._get_compliance_recommendations(issues)
        }
    
    def get_audit_logs(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get audit logs with optional filtering.
        
        Args:
            filters: Optional filters (e.g., date range, action type)
            
        Returns:
            List of audit log entries
        """
        logs = self._audit_logs
        
        if filters:
            # Filter by date range
            if "start_date" in filters:
                logs = [log for log in logs 
                       if log.get("timestamp", "") >= filters["start_date"]]
            
            if "end_date" in filters:
                logs = [log for log in logs 
                       if log.get("timestamp", "") <= filters["end_date"]]
            
            # Filter by action
            if "action" in filters:
                logs = [log for log in logs 
                       if log.get("action") == filters["action"]]
        
        return logs
    
    # ==================== Private Methods ====================
    
    def _check_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """Check for required fields based on compliance level."""
        required_fields = set()
        
        if self.compliance_level == "hipaa":
            required_fields.update(["user_consent", "data_purpose"])
        elif self.compliance_level == "gdpr":
            required_fields.update(["user_consent", "data_retention_period"])
        
        missing = [field for field in required_fields if field not in data]
        return missing
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data to prevent injection attacks."""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potential SQL injection patterns
                sanitized_value = re.sub(r"[';\"--]", "", value)
                # Remove potential XSS patterns
                sanitized_value = re.sub(r"<[^>]*>", "", sanitized_value)
                sanitized[key] = sanitized_value.strip()
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_data(item) if isinstance(item, dict) 
                                else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _detect_pii(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Detect PII in data."""
        pii_found = {}
        
        def check_value(value: str, field_name: str):
            if not isinstance(value, str):
                return
            
            for pii_type, pattern in self.PII_PATTERNS.items():
                if re.search(pattern, value, re.IGNORECASE):
                    pii_found[field_name] = pii_type
                    break
        
        for key, value in data.items():
            if isinstance(value, str):
                check_value(value, key)
            elif isinstance(value, dict):
                nested_pii = self._detect_pii(value)
                for nested_key, pii_type in nested_pii.items():
                    pii_found[f"{key}.{nested_key}"] = pii_type
        
        return pii_found
    
    def _check_compliance(self, data: Dict[str, Any]) -> List[str]:
        """Check for compliance issues based on level."""
        issues = []
        
        if self.compliance_level == "hipaa":
            # HIPAA specific checks
            if not data.get("user_consent"):
                issues.append("HIPAA: User consent not provided")
            if not data.get("data_purpose"):
                issues.append("HIPAA: Data usage purpose not specified")
            if self._detect_pii(data) and not self.enable_encryption:
                issues.append("HIPAA: PHI detected but encryption not enabled")
        
        elif self.compliance_level == "gdpr":
            # GDPR specific checks
            if not data.get("user_consent"):
                issues.append("GDPR: User consent not provided")
            if not data.get("data_retention_period"):
                issues.append("GDPR: Data retention period not specified")
            if not data.get("opt_out_mechanism"):
                issues.append("GDPR: No opt-out mechanism provided")
        
        return issues
    
    def _get_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Get recommendations based on compliance issues."""
        recommendations = []
        
        for issue in issues:
            if "consent" in issue.lower():
                recommendations.append("Implement explicit user consent mechanism")
            if "encryption" in issue.lower():
                recommendations.append("Enable data encryption for sensitive fields")
            if "retention" in issue.lower():
                recommendations.append("Define and implement data retention policies")
            if "opt-out" in issue.lower():
                recommendations.append("Provide clear opt-out mechanisms for users")
        
        return list(set(recommendations))
    
    def _encrypt_field(self, value: str) -> str:
        """Simple encryption placeholder - replace with real encryption."""
        # In production, use proper encryption (e.g., AES-256)
        return hashlib.sha256(f"{value}{self.service_name}".encode()).hexdigest()
    
    def _decrypt_field(self, encrypted_value: str) -> str:
        """Simple decryption placeholder - replace with real decryption."""
        # In production, use proper decryption
        # This is just a placeholder that returns a masked value
        return "***ENCRYPTED***"
    
    def _audit_log(self, action: str, details: Dict[str, Any]) -> None:
        """Add entry to audit log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "action": action,
            "details": details
        }
        
        self._audit_logs.append(entry)
        
        # Keep only last 1000 entries in memory
        if len(self._audit_logs) > 1000:
            self._audit_logs = self._audit_logs[-1000:]
        
        logger.info(f"Security audit: {json.dumps(entry)}")