"""
Security Monitor Service for GUARDIAN Security Compliance agent.
Handles real-time security monitoring, threat detection, and incident response.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from enum import Enum
import hashlib
import re

from agents.backend.guardian.core.config import GuardianConfig
from agents.backend.guardian.core.exceptions import (
    SecurityThreatError,
    MonitoringError,
    ThreatDetectionError,
    IncidentResponseError,
)
from agents.backend.guardian.core.constants import (
    THREAT_CATEGORIES,
    SECURITY_EVENT_TYPES,
    RESPONSE_ACTIONS,
    SEVERITY_LEVELS,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class ThreatLevel(Enum):
    """Threat level enumeration."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityEvent:
    """Represents a security event."""

    event_id: str
    event_type: str
    timestamp: datetime
    source: str
    target: Optional[str]
    severity: ThreatLevel
    description: str
    metadata: Dict[str, Any]
    response_actions: List[str]


@dataclass
class ThreatIndicator:
    """Represents a threat indicator."""

    indicator_type: str  # ip, domain, hash, pattern
    value: str
    threat_level: ThreatLevel
    categories: List[str]
    first_seen: datetime
    last_seen: datetime
    occurrences: int


class SecurityMonitorService:
    """
    Comprehensive security monitoring service for threat detection and response.

    Features:
    - Real-time security event monitoring
    - Threat detection using AI and pattern matching
    - Automated incident response
    - Vulnerability tracking
    - Anomaly detection
    - Security analytics and reporting
    """

    def __init__(self, config: GuardianConfig):
        self.config = config
        self._monitoring_active = False
        self._threat_indicators: Dict[str, ThreatIndicator] = {}
        self._security_events: List[SecurityEvent] = []
        self._active_incidents: Dict[str, Dict[str, Any]] = {}
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._event_patterns: Dict[str, re.Pattern] = {}
        self._baseline_metrics: Dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the security monitoring service."""
        try:
            # Initialize threat patterns
            await self._initialize_threat_patterns()

            # Load threat intelligence
            await self._load_threat_intelligence()

            # Establish baseline metrics
            await self._establish_baseline_metrics()

            # Start monitoring if enabled
            if self.config.enable_security_monitoring:
                await self.start_monitoring()

            self._initialized = True
            logger.info("Security monitoring service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize security monitoring service: {e}")
            raise MonitoringError(
                f"Security monitoring initialization failed: {e}",
                monitor_type="initialization",
            )

    async def _initialize_threat_patterns(self) -> None:
        """Initialize regex patterns for threat detection."""
        self._event_patterns = {
            # Authentication patterns
            "failed_login": re.compile(
                r"(failed|invalid|unsuccessful)\s+(login|authentication|auth)",
                re.IGNORECASE,
            ),
            "brute_force": re.compile(
                r"(multiple|repeated|consecutive)\s+failed\s+(login|auth)",
                re.IGNORECASE,
            ),
            # SQL injection patterns
            "sql_injection": re.compile(
                r"(union\s+select|or\s+1\s*=\s*1|drop\s+table|insert\s+into)",
                re.IGNORECASE,
            ),
            # XSS patterns
            "xss_attempt": re.compile(
                r"(<script|javascript:|onerror\s*=|onload\s*=)", re.IGNORECASE
            ),
            # Command injection patterns
            "command_injection": re.compile(
                r"(;\s*rm\s+-rf|&&\s*cat\s+/etc/passwd|\|\s*nc\s+)", re.IGNORECASE
            ),
            # Path traversal patterns
            "path_traversal": re.compile(r"(\.\./|\.\.\\|%2e%2e%2f)", re.IGNORECASE),
            # Suspicious user agents
            "suspicious_agent": re.compile(
                r"(sqlmap|nikto|nmap|masscan|metasploit)", re.IGNORECASE
            ),
        }

    async def _load_threat_intelligence(self) -> None:
        """Load threat intelligence data."""
        # In production, this would load from threat feeds
        # For now, initialize with sample indicators
        sample_indicators = [
            ThreatIndicator(
                indicator_type="ip",
                value="192.168.1.100",
                threat_level=ThreatLevel.HIGH,
                categories=["malware", "c2"],
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                occurrences=1,
            ),
            ThreatIndicator(
                indicator_type="domain",
                value="malicious-site.com",
                threat_level=ThreatLevel.CRITICAL,
                categories=["phishing"],
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                occurrences=1,
            ),
        ]

        for indicator in sample_indicators:
            self._threat_indicators[indicator.value] = indicator

    async def _establish_baseline_metrics(self) -> None:
        """Establish baseline metrics for anomaly detection."""
        self._baseline_metrics = {
            "avg_requests_per_minute": 100,
            "avg_failed_logins_per_hour": 5,
            "avg_data_transfer_mb": 50,
            "normal_access_hours": (6, 22),  # 6 AM to 10 PM
            "typical_user_agents": ["Chrome", "Firefox", "Safari", "Edge"],
        }

    async def start_monitoring(self) -> None:
        """Start security monitoring."""
        if self._monitoring_active:
            logger.warning("Security monitoring is already active")
            return

        try:
            self._monitoring_active = True

            # Start monitoring tasks
            tasks = [
                self._monitor_security_events(),
                self._monitor_system_integrity(),
                self._monitor_network_traffic(),
                self._monitor_access_patterns(),
                self._threat_intelligence_update(),
            ]

            for task in tasks:
                monitoring_task = asyncio.create_task(task)
                self._monitoring_tasks.add(monitoring_task)
                monitoring_task.add_done_callback(self._monitoring_tasks.discard)

            logger.info("Security monitoring started successfully")

        except Exception as e:
            self._monitoring_active = False
            logger.error(f"Failed to start security monitoring: {e}")
            raise MonitoringError(
                f"Failed to start monitoring: {e}", monitor_type="startup"
            )

    async def stop_monitoring(self) -> None:
        """Stop security monitoring."""
        self._monitoring_active = False

        # Cancel all monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._monitoring_tasks:
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)

        self._monitoring_tasks.clear()
        logger.info("Security monitoring stopped")

    async def _monitor_security_events(self) -> None:
        """Monitor security events in real-time."""
        while self._monitoring_active:
            try:
                # Simulate event monitoring (in production, this would connect to real sources)
                await asyncio.sleep(self.config.monitoring_sample_rate)

                # Check for security events
                # This is where real event collection would happen

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in security event monitoring: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def _monitor_system_integrity(self) -> None:
        """Monitor system integrity."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Perform integrity checks
                integrity_status = await self._check_system_integrity()

                if not integrity_status["passed"]:
                    await self._handle_integrity_violation(integrity_status)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system integrity monitoring: {e}")

    async def _monitor_network_traffic(self) -> None:
        """Monitor network traffic for anomalies."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Analyze network patterns
                traffic_analysis = await self._analyze_network_traffic()

                if traffic_analysis.get("anomalies"):
                    await self._handle_network_anomalies(traffic_analysis["anomalies"])

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in network traffic monitoring: {e}")

    async def _monitor_access_patterns(self) -> None:
        """Monitor access patterns for suspicious behavior."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes

                # Analyze access patterns
                access_analysis = await self._analyze_access_patterns()

                if access_analysis.get("suspicious_patterns"):
                    await self._handle_suspicious_access(
                        access_analysis["suspicious_patterns"]
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in access pattern monitoring: {e}")

    async def _threat_intelligence_update(self) -> None:
        """Update threat intelligence data periodically."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(self.config.threat_feed_update_interval)

                # Update threat indicators
                await self._update_threat_indicators()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating threat intelligence: {e}")

    async def detect_threat(
        self, event_data: Dict[str, Any]
    ) -> Optional[SecurityEvent]:
        """
        Detect threats in event data.

        Args:
            event_data: Event data to analyze

        Returns:
            SecurityEvent if threat detected, None otherwise
        """
        try:
            # Check against threat patterns
            threat_matches = []

            event_text = json.dumps(event_data).lower()

            for pattern_name, pattern in self._event_patterns.items():
                if pattern.search(event_text):
                    threat_matches.append(pattern_name)

            # Check against threat indicators
            for indicator in self._threat_indicators.values():
                if indicator.value.lower() in event_text:
                    threat_matches.append(f"indicator_{indicator.indicator_type}")

            if threat_matches:
                # Determine threat level
                threat_level = self._calculate_threat_level(threat_matches, event_data)

                # Create security event
                security_event = SecurityEvent(
                    event_id=self._generate_event_id(),
                    event_type="threat_detected",
                    timestamp=datetime.utcnow(),
                    source=event_data.get("source", "unknown"),
                    target=event_data.get("target"),
                    severity=threat_level,
                    description=f"Threat detected: {', '.join(threat_matches)}",
                    metadata={
                        "threat_matches": threat_matches,
                        "event_data": event_data,
                    },
                    response_actions=self._determine_response_actions(threat_level),
                )

                # Record event
                self._security_events.append(security_event)

                # Trigger response if needed
                if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    await self._initiate_incident_response(security_event)

                return security_event

            return None

        except Exception as e:
            logger.error(f"Error detecting threat: {e}")
            raise ThreatDetectionError(
                f"Threat detection failed: {e}", detection_method="pattern_matching"
            )

    async def scan_for_vulnerabilities(
        self, target: str, scan_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Scan for vulnerabilities.

        Args:
            target: Target to scan (system, application, network)
            scan_type: Type of scan to perform

        Returns:
            Dict[str, Any]: Vulnerability scan results
        """
        try:
            logger.info(f"Starting {scan_type} vulnerability scan on {target}")

            scan_results = {
                "scan_id": self._generate_event_id(),
                "target": target,
                "scan_type": scan_type,
                "started_at": datetime.utcnow(),
                "vulnerabilities": [],
                "risk_score": 0,
            }

            # Simulate vulnerability scanning
            # In production, this would use real scanning tools

            # Check for common vulnerabilities
            vulnerabilities = await self._check_common_vulnerabilities(target)

            # Check for misconfigurations
            misconfigs = await self._check_misconfigurations(target)

            # Check for outdated components
            outdated = await self._check_outdated_components(target)

            # Combine results
            all_vulnerabilities = vulnerabilities + misconfigs + outdated

            # Calculate risk score
            risk_score = self._calculate_risk_score(all_vulnerabilities)

            scan_results.update(
                {
                    "completed_at": datetime.utcnow(),
                    "vulnerabilities": all_vulnerabilities,
                    "risk_score": risk_score,
                    "severity_summary": self._summarize_severities(all_vulnerabilities),
                    "recommendations": self._generate_remediation_recommendations(
                        all_vulnerabilities
                    ),
                }
            )

            # Create security event for high-risk findings
            if risk_score > 7:
                await self._create_vulnerability_event(scan_results)

            return scan_results

        except Exception as e:
            logger.error(f"Vulnerability scan failed: {e}")
            raise MonitoringError(
                f"Vulnerability scan failed: {e}",
                monitor_type="vulnerability_scan",
                target=target,
            )

    async def respond_to_incident(
        self, incident_id: str, response_actions: List[str]
    ) -> Dict[str, Any]:
        """
        Execute incident response actions.

        Args:
            incident_id: Incident identifier
            response_actions: List of response actions to take

        Returns:
            Dict[str, Any]: Response execution results
        """
        try:
            if incident_id not in self._active_incidents:
                raise IncidentResponseError(
                    f"Incident {incident_id} not found",
                    incident_id=incident_id,
                    response_phase="validation",
                )

            incident = self._active_incidents[incident_id]
            response_results = {
                "incident_id": incident_id,
                "actions_requested": response_actions,
                "actions_completed": [],
                "actions_failed": [],
                "response_time": datetime.utcnow(),
            }

            for action in response_actions:
                try:
                    if action == "BLOCK":
                        result = await self._execute_block_action(incident)
                    elif action == "ISOLATE":
                        result = await self._execute_isolate_action(incident)
                    elif action == "ALERT":
                        result = await self._execute_alert_action(incident)
                    elif action == "INVESTIGATE":
                        result = await self._execute_investigate_action(incident)
                    elif action == "REMEDIATE":
                        result = await self._execute_remediate_action(incident)
                    else:
                        result = {"status": "unsupported", "action": action}

                    if result.get("status") == "success":
                        response_results["actions_completed"].append(action)
                    else:
                        response_results["actions_failed"].append(
                            {
                                "action": action,
                                "reason": result.get("error", "Unknown error"),
                            }
                        )

                except Exception as e:
                    response_results["actions_failed"].append(
                        {"action": action, "reason": str(e)}
                    )

            # Update incident status
            incident["status"] = "responded"
            incident["response_completed_at"] = datetime.utcnow()
            incident["response_results"] = response_results

            return response_results

        except Exception as e:
            logger.error(f"Incident response failed: {e}")
            raise IncidentResponseError(
                f"Response execution failed: {e}",
                incident_id=incident_id,
                response_phase="execution",
            )

    async def generate_threat_report(
        self, time_range: timedelta, report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate threat analysis report."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_range

            # Filter events within time range
            relevant_events = [
                event
                for event in self._security_events
                if start_time <= event.timestamp <= end_time
            ]

            # Analyze threats
            threat_analysis = {
                "report_id": self._generate_event_id(),
                "report_type": report_type,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                },
                "total_events": len(relevant_events),
                "threat_summary": self._analyze_threat_trends(relevant_events),
                "top_threats": self._identify_top_threats(relevant_events),
                "affected_resources": self._identify_affected_resources(
                    relevant_events
                ),
                "incident_summary": self._summarize_incidents(start_time, end_time),
                "recommendations": self._generate_security_recommendations(
                    relevant_events
                ),
                "risk_assessment": self._assess_overall_risk(relevant_events),
            }

            return threat_analysis

        except Exception as e:
            logger.error(f"Failed to generate threat report: {e}")
            raise MonitoringError(
                f"Report generation failed: {e}", monitor_type="threat_report"
            )

    # Helper methods

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"SEC-{int(timestamp * 1000)}"

    def _calculate_threat_level(
        self, threat_matches: List[str], event_data: Dict[str, Any]
    ) -> ThreatLevel:
        """Calculate threat level based on matches and context."""
        # Critical threats
        critical_patterns = ["sql_injection", "command_injection", "indicator_ip"]
        if any(pattern in threat_matches for pattern in critical_patterns):
            return ThreatLevel.CRITICAL

        # High threats
        high_patterns = ["xss_attempt", "path_traversal", "brute_force"]
        if any(pattern in threat_matches for pattern in high_patterns):
            return ThreatLevel.HIGH

        # Medium threats
        if len(threat_matches) > 1:
            return ThreatLevel.MEDIUM

        # Low threats
        return ThreatLevel.LOW

    def _determine_response_actions(self, threat_level: ThreatLevel) -> List[str]:
        """Determine appropriate response actions based on threat level."""
        if threat_level == ThreatLevel.CRITICAL:
            return ["BLOCK", "ISOLATE", "ALERT", "INVESTIGATE"]
        elif threat_level == ThreatLevel.HIGH:
            return ["BLOCK", "ALERT", "INVESTIGATE"]
        elif threat_level == ThreatLevel.MEDIUM:
            return ["ALERT", "LOG", "INVESTIGATE"]
        else:
            return ["LOG"]

    async def _initiate_incident_response(self, security_event: SecurityEvent) -> None:
        """Initiate incident response for high-severity events."""
        incident = {
            "incident_id": f"INC-{security_event.event_id}",
            "security_event": security_event,
            "status": "active",
            "created_at": datetime.utcnow(),
            "severity": security_event.severity.value,
            "assigned_to": "auto-response",
            "timeline": [],
        }

        self._active_incidents[incident["incident_id"]] = incident

        # Execute automatic response if enabled
        if self.config.auto_containment_enabled:
            await self.respond_to_incident(
                incident["incident_id"], security_event.response_actions
            )

    async def _check_system_integrity(self) -> Dict[str, Any]:
        """Check system integrity."""
        # Simplified integrity check
        return {
            "passed": True,
            "checks": {
                "file_integrity": "passed",
                "config_integrity": "passed",
                "binary_integrity": "passed",
            },
        }

    async def _analyze_network_traffic(self) -> Dict[str, Any]:
        """Analyze network traffic patterns."""
        # Simplified traffic analysis
        return {
            "total_requests": 1000,
            "anomalies": [],
            "suspicious_ips": [],
        }

    async def _analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze access patterns."""
        # Simplified access analysis
        return {
            "total_accesses": 500,
            "failed_attempts": 5,
            "suspicious_patterns": [],
        }

    async def _update_threat_indicators(self) -> None:
        """Update threat indicators from intelligence feeds."""
        # In production, this would fetch from real threat feeds
        logger.info("Threat intelligence updated")

    async def _check_common_vulnerabilities(self, target: str) -> List[Dict[str, Any]]:
        """Check for common vulnerabilities."""
        # Simplified vulnerability check
        return []

    async def _check_misconfigurations(self, target: str) -> List[Dict[str, Any]]:
        """Check for security misconfigurations."""
        # Simplified misconfiguration check
        return []

    async def _check_outdated_components(self, target: str) -> List[Dict[str, Any]]:
        """Check for outdated components."""
        # Simplified component check
        return []

    def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score."""
        if not vulnerabilities:
            return 0.0

        # Simplified risk calculation
        severity_scores = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 1,
        }

        total_score = sum(
            severity_scores.get(vuln.get("severity", "low"), 1)
            for vuln in vulnerabilities
        )

        # Normalize to 0-10 scale
        return min(10, total_score / len(vulnerabilities))

    def _summarize_severities(
        self, vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Summarize vulnerabilities by severity."""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            if severity in summary:
                summary[severity] += 1

        return summary

    def _generate_remediation_recommendations(
        self, vulnerabilities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate remediation recommendations."""
        recommendations = []

        if any(v.get("severity") == "critical" for v in vulnerabilities):
            recommendations.append("Immediately patch critical vulnerabilities")

        if any(v.get("type") == "misconfiguration" for v in vulnerabilities):
            recommendations.append("Review and correct security configurations")

        if any(v.get("type") == "outdated" for v in vulnerabilities):
            recommendations.append("Update outdated components to latest versions")

        return recommendations

    async def _create_vulnerability_event(self, scan_results: Dict[str, Any]) -> None:
        """Create security event for vulnerability findings."""
        security_event = SecurityEvent(
            event_id=self._generate_event_id(),
            event_type="vulnerability_discovered",
            timestamp=datetime.utcnow(),
            source="vulnerability_scanner",
            target=scan_results["target"],
            severity=(
                ThreatLevel.HIGH
                if scan_results["risk_score"] > 7
                else ThreatLevel.MEDIUM
            ),
            description=f"High-risk vulnerabilities found in {scan_results['target']}",
            metadata=scan_results,
            response_actions=["ALERT", "INVESTIGATE"],
        )

        self._security_events.append(security_event)

    # Incident response execution methods

    async def _execute_block_action(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Execute block action."""
        # In production, this would implement actual blocking
        return {"status": "success", "action": "block", "details": "Access blocked"}

    async def _execute_isolate_action(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system isolation."""
        # In production, this would implement actual isolation
        return {"status": "success", "action": "isolate", "details": "System isolated"}

    async def _execute_alert_action(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Execute alert action."""
        # In production, this would send actual alerts
        return {"status": "success", "action": "alert", "details": "Alerts sent"}

    async def _execute_investigate_action(
        self, incident: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute investigation action."""
        # In production, this would initiate investigation workflow
        return {
            "status": "success",
            "action": "investigate",
            "details": "Investigation started",
        }

    async def _execute_remediate_action(
        self, incident: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute remediation action."""
        # In production, this would apply remediation
        return {
            "status": "success",
            "action": "remediate",
            "details": "Remediation applied",
        }

    # Analysis helper methods

    def _analyze_threat_trends(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Analyze threat trends from events."""
        trend_analysis = {
            "increasing_threats": [],
            "decreasing_threats": [],
            "steady_threats": [],
            "new_threats": [],
        }

        # Simplified trend analysis
        threat_counts = {}
        for event in events:
            threat_type = event.event_type
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1

        trend_analysis["top_threat_types"] = sorted(
            threat_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return trend_analysis

    def _identify_top_threats(
        self, events: List[SecurityEvent]
    ) -> List[Dict[str, Any]]:
        """Identify top threats from events."""
        threat_summary = {}

        for event in events:
            key = (event.event_type, event.severity.value)
            if key not in threat_summary:
                threat_summary[key] = {
                    "type": event.event_type,
                    "severity": event.severity.value,
                    "count": 0,
                    "sources": set(),
                }

            threat_summary[key]["count"] += 1
            if event.source:
                threat_summary[key]["sources"].add(event.source)

        # Convert sets to lists for JSON serialization
        for threat in threat_summary.values():
            threat["sources"] = list(threat["sources"])

        # Sort by count and severity
        return sorted(
            threat_summary.values(),
            key=lambda x: (x["count"], SEVERITY_LEVELS[x["severity"]]["value"]),
            reverse=True,
        )[:10]

    def _identify_affected_resources(
        self, events: List[SecurityEvent]
    ) -> Dict[str, List[str]]:
        """Identify affected resources from events."""
        affected = {}

        for event in events:
            if event.target:
                resource_type = self._classify_resource(event.target)
                if resource_type not in affected:
                    affected[resource_type] = []
                if event.target not in affected[resource_type]:
                    affected[resource_type].append(event.target)

        return affected

    def _classify_resource(self, resource: str) -> str:
        """Classify resource type."""
        if "api" in resource.lower():
            return "api_endpoints"
        elif "db" in resource.lower() or "database" in resource.lower():
            return "databases"
        elif "server" in resource.lower():
            return "servers"
        elif "user" in resource.lower():
            return "user_accounts"
        else:
            return "other_resources"

    def _summarize_incidents(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Summarize incidents within time range."""
        relevant_incidents = [
            inc
            for inc in self._active_incidents.values()
            if start_time <= inc["created_at"] <= end_time
        ]

        return {
            "total_incidents": len(relevant_incidents),
            "active_incidents": len(
                [i for i in relevant_incidents if i["status"] == "active"]
            ),
            "resolved_incidents": len(
                [i for i in relevant_incidents if i["status"] == "resolved"]
            ),
            "severity_breakdown": self._get_incident_severity_breakdown(
                relevant_incidents
            ),
        }

    def _get_incident_severity_breakdown(
        self, incidents: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Get incident severity breakdown."""
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

        for incident in incidents:
            severity = incident.get("severity", "info")
            if severity in breakdown:
                breakdown[severity] += 1

        return breakdown

    def _generate_security_recommendations(
        self, events: List[SecurityEvent]
    ) -> List[str]:
        """Generate security recommendations based on events."""
        recommendations = []

        # Check for specific patterns
        auth_failures = [e for e in events if "auth" in e.event_type.lower()]
        if len(auth_failures) > 10:
            recommendations.append("Implement stronger authentication mechanisms")

        injection_attempts = [e for e in events if "injection" in e.event_type.lower()]
        if injection_attempts:
            recommendations.append("Review and strengthen input validation")

        high_severity = [
            e for e in events if e.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        ]
        if len(high_severity) > 5:
            recommendations.append("Conduct comprehensive security assessment")

        return recommendations

    def _assess_overall_risk(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Assess overall security risk."""
        if not events:
            return {"risk_level": "low", "risk_score": 0}

        # Calculate risk based on event severity and frequency
        severity_weights = {
            ThreatLevel.CRITICAL: 10,
            ThreatLevel.HIGH: 7,
            ThreatLevel.MEDIUM: 4,
            ThreatLevel.LOW: 2,
            ThreatLevel.INFO: 1,
        }

        total_weight = sum(severity_weights.get(e.severity, 1) for e in events)
        risk_score = min(10, total_weight / len(events))

        if risk_score >= 8:
            risk_level = "critical"
        elif risk_score >= 6:
            risk_level = "high"
        elif risk_score >= 4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "factors": {
                "event_count": len(events),
                "high_severity_count": len(
                    [
                        e
                        for e in events
                        if e.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
                    ]
                ),
                "unique_threat_types": len(set(e.event_type for e in events)),
            },
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on security monitoring service."""
        return {
            "service": "SecurityMonitorService",
            "status": "healthy" if self._initialized else "unhealthy",
            "monitoring_active": self._monitoring_active,
            "active_monitors": len(self._monitoring_tasks),
            "threat_indicators": len(self._threat_indicators),
            "recent_events": len(self._security_events),
            "active_incidents": len(self._active_incidents),
        }

    async def cleanup(self) -> None:
        """Clean up monitoring resources."""
        if self._monitoring_active:
            await self.stop_monitoring()

        self._threat_indicators.clear()
        self._security_events.clear()
        self._active_incidents.clear()

        logger.info("Security monitoring service cleaned up")
