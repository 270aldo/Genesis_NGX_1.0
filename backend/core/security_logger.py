"""
Security logging and monitoring for GENESIS API.

This module provides comprehensive security event logging for:
- Authentication attempts (success/failure)
- Authorization violations
- Rate limit violations
- Suspicious activities
- Data access patterns
- API misuse attempts
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import hashlib

from fastapi import Request
from pydantic import BaseModel
import redis.asyncio as redis

from core.settings_lazy import settings
from core.logging_config import get_logger

# Create dedicated security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Create file handler for security events
security_handler = logging.FileHandler("logs/security.log")
security_handler.setLevel(logging.INFO)

# Create formatter with structured logging
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": %(message)s}'
)
security_handler.setFormatter(formatter)
security_logger.addHandler(security_handler)


class SecurityEventType(str, Enum):
    """Types of security events to track."""
    
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    
    # Authorization events
    ACCESS_DENIED = "access_denied"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNAUTHORIZED_RESOURCE = "unauthorized_resource"
    
    # Rate limiting events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    IP_BLOCKED = "ip_blocked"
    USER_BLOCKED = "user_blocked"
    
    # Suspicious activity
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    PATH_TRAVERSAL_ATTEMPT = "path_traversal_attempt"
    UNUSUAL_REQUEST_PATTERN = "unusual_request_pattern"
    
    # Data access
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    BULK_DATA_EXPORT = "bulk_data_export"
    DATA_MODIFICATION = "data_modification"
    
    # API misuse
    INVALID_API_KEY = "invalid_api_key"
    DEPRECATED_ENDPOINT = "deprecated_endpoint"
    MALFORMED_REQUEST = "malformed_request"


class SecurityEvent(BaseModel):
    """Model for security events."""
    
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}
    risk_score: int = 0  # 0-100 risk assessment


class SecurityLogger:
    """Advanced security logging with pattern detection and alerting."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.logger = security_logger
        self.suspicious_patterns = [
            r"(?i)(union.*select|select.*from|insert.*into|delete.*from)",  # SQL injection
            r"(?i)(<script|javascript:|onerror=|onload=)",  # XSS
            r"(?i)(\.\.\/|\.\.\\)",  # Path traversal
            r"(?i)(eval\(|exec\(|system\()",  # Code injection
        ]
    
    def _hash_ip(self, ip: str) -> str:
        """Hash IP address for privacy (GDPR compliance)."""
        if settings.env == "production":
            return hashlib.sha256(f"{ip}{settings.jwt_secret}".encode()).hexdigest()[:16]
        return ip
    
    async def log_event(self, event: SecurityEvent):
        """Log a security event with risk assessment."""
        # Calculate risk score if not provided
        if event.risk_score == 0:
            event.risk_score = self._calculate_risk_score(event)
        
        # Anonymize IP if needed
        if event.ip_address:
            event.metadata["original_ip_hash"] = self._hash_ip(event.ip_address)
        
        # Log to file
        log_data = event.dict()
        log_data["timestamp"] = log_data["timestamp"].isoformat()
        self.logger.info(json.dumps(log_data))
        
        # Store in Redis for real-time analysis
        if self.redis_client:
            await self._store_event_redis(event)
        
        # Check for alerts
        if event.risk_score >= 70:
            await self._trigger_alert(event)
    
    def _calculate_risk_score(self, event: SecurityEvent) -> int:
        """Calculate risk score based on event type and patterns."""
        base_scores = {
            SecurityEventType.LOGIN_SUCCESS: 0,
            SecurityEventType.LOGIN_FAILURE: 20,
            SecurityEventType.ACCESS_DENIED: 30,
            SecurityEventType.RATE_LIMIT_EXCEEDED: 40,
            SecurityEventType.SQL_INJECTION_ATTEMPT: 80,
            SecurityEventType.XSS_ATTEMPT: 80,
            SecurityEventType.PATH_TRAVERSAL_ATTEMPT: 80,
            SecurityEventType.PRIVILEGE_ESCALATION: 90,
            SecurityEventType.SENSITIVE_DATA_ACCESS: 50,
            SecurityEventType.BULK_DATA_EXPORT: 60,
        }
        
        score = base_scores.get(event.event_type, 50)
        
        # Increase score for repeated violations
        if event.metadata.get("violation_count", 0) > 3:
            score += 20
        
        # Increase score for suspicious user agents
        if event.user_agent and any(bot in event.user_agent.lower() 
                                   for bot in ["bot", "scanner", "crawler"]):
            score += 10
        
        return min(score, 100)
    
    async def _store_event_redis(self, event: SecurityEvent):
        """Store event in Redis for pattern analysis."""
        if not self.redis_client:
            return
        
        key = f"security_event:{event.event_type}:{datetime.now().strftime('%Y%m%d')}"
        
        # Store event
        await self.redis_client.lpush(key, event.json())
        await self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days
        
        # Update counters
        if event.user_id:
            user_key = f"security_events:user:{event.user_id}"
            await self.redis_client.hincrby(user_key, event.event_type, 1)
            await self.redis_client.expire(user_key, 86400)
        
        if event.ip_address:
            ip_key = f"security_events:ip:{self._hash_ip(event.ip_address)}"
            await self.redis_client.hincrby(ip_key, event.event_type, 1)
            await self.redis_client.expire(ip_key, 86400)
    
    async def _trigger_alert(self, event: SecurityEvent):
        """Trigger alert for high-risk events."""
        alert_message = f"""
        HIGH RISK SECURITY EVENT DETECTED
        
        Event Type: {event.event_type}
        Risk Score: {event.risk_score}
        User ID: {event.user_id or 'Anonymous'}
        IP Hash: {event.metadata.get('original_ip_hash', 'Unknown')}
        Path: {event.request_path}
        Time: {event.timestamp}
        
        Metadata: {json.dumps(event.metadata, indent=2)}
        """
        
        # Log critical alert
        self.logger.critical(alert_message)
        
        # TODO: Integrate with alerting service (PagerDuty, email, Slack, etc.)
    
    async def analyze_patterns(self, user_id: Optional[str] = None, 
                             ip_hash: Optional[str] = None) -> Dict[str, Any]:
        """Analyze security patterns for a user or IP."""
        if not self.redis_client:
            return {}
        
        pattern_data = {
            "risk_level": "low",
            "event_counts": {},
            "recommendations": []
        }
        
        # Get event counts
        if user_id:
            key = f"security_events:user:{user_id}"
        elif ip_hash:
            key = f"security_events:ip:{ip_hash}"
        else:
            return pattern_data
        
        events = await self.redis_client.hgetall(key)
        if not events:
            return pattern_data
        
        # Convert and analyze
        event_counts = {k.decode(): int(v) for k, v in events.items()}
        pattern_data["event_counts"] = event_counts
        
        # Assess risk level
        total_failures = event_counts.get(SecurityEventType.LOGIN_FAILURE, 0)
        total_rate_limits = event_counts.get(SecurityEventType.RATE_LIMIT_EXCEEDED, 0)
        total_suspicious = sum(event_counts.get(e, 0) for e in [
            SecurityEventType.SQL_INJECTION_ATTEMPT,
            SecurityEventType.XSS_ATTEMPT,
            SecurityEventType.PATH_TRAVERSAL_ATTEMPT
        ])
        
        if total_suspicious > 0 or total_failures > 10:
            pattern_data["risk_level"] = "high"
            pattern_data["recommendations"].append("Consider blocking this entity")
        elif total_rate_limits > 5 or total_failures > 5:
            pattern_data["risk_level"] = "medium"
            pattern_data["recommendations"].append("Monitor closely for suspicious activity")
        
        return pattern_data


# Global security logger instance
sec_logger = SecurityLogger()


# Convenience functions
async def log_login_attempt(request: Request, user_id: Optional[str], 
                          success: bool, error: Optional[str] = None):
    """Log login attempt."""
    event = SecurityEvent(
        event_type=SecurityEventType.LOGIN_SUCCESS if success else SecurityEventType.LOGIN_FAILURE,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path=str(request.url.path),
        request_method=request.method,
        error_message=error,
        metadata={"attempt_username": user_id} if not success else {}
    )
    await sec_logger.log_event(event)


async def log_access_denied(request: Request, user_id: Optional[str], 
                          resource: str, reason: str):
    """Log access denied event."""
    event = SecurityEvent(
        event_type=SecurityEventType.ACCESS_DENIED,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path=str(request.url.path),
        request_method=request.method,
        metadata={
            "resource": resource,
            "reason": reason
        }
    )
    await sec_logger.log_event(event)


async def log_suspicious_request(request: Request, pattern_type: str, 
                               details: Dict[str, Any]):
    """Log suspicious request patterns."""
    event_type_map = {
        "sql_injection": SecurityEventType.SQL_INJECTION_ATTEMPT,
        "xss": SecurityEventType.XSS_ATTEMPT,
        "path_traversal": SecurityEventType.PATH_TRAVERSAL_ATTEMPT,
    }
    
    event = SecurityEvent(
        event_type=event_type_map.get(pattern_type, SecurityEventType.UNUSUAL_REQUEST_PATTERN),
        timestamp=datetime.utcnow(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path=str(request.url.path),
        request_method=request.method,
        metadata=details,
        risk_score=80  # High risk for suspicious patterns
    )
    await sec_logger.log_event(event)


async def log_data_access(request: Request, user_id: str, 
                        resource_type: str, action: str, 
                        record_count: int = 1):
    """Log data access events."""
    is_bulk = record_count > 100
    is_sensitive = resource_type in ["users", "payments", "health_data"]
    
    event_type = SecurityEventType.BULK_DATA_EXPORT if is_bulk else (
        SecurityEventType.SENSITIVE_DATA_ACCESS if is_sensitive else 
        SecurityEventType.DATA_MODIFICATION
    )
    
    event = SecurityEvent(
        event_type=event_type,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path=str(request.url.path),
        request_method=request.method,
        metadata={
            "resource_type": resource_type,
            "action": action,
            "record_count": record_count
        }
    )
    await sec_logger.log_event(event)