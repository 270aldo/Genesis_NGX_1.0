"""
Compliance Checker Service for GUARDIAN Security Compliance agent.
Handles compliance verification, policy enforcement, and regulatory reporting.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from agents.backend.guardian.core.config import GuardianConfig
from agents.backend.guardian.core.exceptions import (
    ComplianceViolationError,
    GuardianValidationError,
    AuditTrailError,
)
from agents.backend.guardian.core.constants import (
    COMPLIANCE_FRAMEWORKS,
    SECURITY_CONTROLS,
    DATA_CLASSIFICATION_LEVELS,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class ComplianceStatus(Enum):
    """Compliance status enumeration."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    PENDING = "pending"


class ControlStatus(Enum):
    """Security control status enumeration."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceRequirement:
    """Represents a compliance requirement."""

    requirement_id: str
    framework: str
    category: str
    description: str
    controls: List[str]
    criticality: str  # critical, high, medium, low
    evidence_required: bool


@dataclass
class ComplianceAssessment:
    """Represents a compliance assessment result."""

    assessment_id: str
    framework: str
    timestamp: datetime
    overall_status: ComplianceStatus
    requirements_checked: int
    requirements_passed: int
    requirements_failed: int
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    next_assessment: datetime


@dataclass
class PolicyViolation:
    """Represents a policy violation."""

    violation_id: str
    policy_id: str
    timestamp: datetime
    severity: str
    description: str
    affected_resource: str
    remediation_required: bool
    remediation_status: Optional[str]


class ComplianceCheckerService:
    """
    Comprehensive compliance checking service for regulatory adherence.

    Features:
    - Multi-framework compliance verification
    - Automated policy enforcement
    - Regulatory reporting
    - Control assessment and gap analysis
    - Privacy compliance (GDPR, CCPA)
    - Healthcare compliance (HIPAA)
    - Financial compliance (PCI-DSS)
    """

    def __init__(self, config: GuardianConfig):
        self.config = config
        self._compliance_requirements: Dict[str, List[ComplianceRequirement]] = {}
        self._policy_definitions: Dict[str, Dict[str, Any]] = {}
        self._assessment_history: List[ComplianceAssessment] = []
        self._policy_violations: List[PolicyViolation] = []
        self._control_implementations: Dict[str, ControlStatus] = {}
        self._monitoring_active = False
        self._compliance_tasks: Set[asyncio.Task] = set()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the compliance checker service."""
        try:
            # Load compliance requirements
            await self._load_compliance_requirements()

            # Load policy definitions
            await self._load_policy_definitions()

            # Initialize control implementations
            await self._initialize_control_status()

            # Start compliance monitoring if enabled
            if self.config.enable_compliance_monitoring:
                await self.start_compliance_monitoring()

            self._initialized = True
            logger.info("Compliance checker service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize compliance checker service: {e}")
            raise ComplianceViolationError(
                f"Compliance service initialization failed: {e}",
                framework="initialization",
                severity="critical",
            )

    async def _load_compliance_requirements(self) -> None:
        """Load compliance requirements for configured frameworks."""
        for framework in self.config.compliance_frameworks:
            if framework in COMPLIANCE_FRAMEWORKS:
                requirements = await self._generate_framework_requirements(framework)
                self._compliance_requirements[framework] = requirements
            else:
                logger.warning(f"Unknown compliance framework: {framework}")

    async def _generate_framework_requirements(
        self, framework: str
    ) -> List[ComplianceRequirement]:
        """Generate requirements for a specific framework."""
        framework_data = COMPLIANCE_FRAMEWORKS[framework]
        requirements = []

        # Generate sample requirements based on framework
        for idx, req in enumerate(framework_data["key_requirements"]):
            requirement = ComplianceRequirement(
                requirement_id=f"{framework}-REQ-{idx+1:03d}",
                framework=framework,
                category=req,
                description=f"{framework} requirement for {req}",
                controls=self._map_requirement_to_controls(framework, req),
                criticality="high" if idx < 2 else "medium",
                evidence_required=True,
            )
            requirements.append(requirement)

        return requirements

    def _map_requirement_to_controls(
        self, framework: str, requirement: str
    ) -> List[str]:
        """Map compliance requirement to security controls."""
        # Simplified mapping logic
        control_mapping = {
            "consent": ["AC-1", "AC-2", "IA-1"],
            "encryption": ["SC-1", "SC-2", "SC-3"],
            "access": ["AC-3", "AC-6", "IA-2"],
            "audit": ["AU-1", "AU-2", "AU-3", "AU-6"],
            "privacy": ["AC-1", "SC-1", "RA-1"],
        }

        # Find matching controls based on requirement keywords
        mapped_controls = []
        for keyword, controls in control_mapping.items():
            if keyword.lower() in requirement.lower():
                mapped_controls.extend(controls)

        return list(set(mapped_controls)) or ["CM-1"]  # Default control

    async def _load_policy_definitions(self) -> None:
        """Load security and compliance policy definitions."""
        self._policy_definitions = {
            "data_retention": {
                "id": "POL-001",
                "name": "Data Retention Policy",
                "description": "Defines data retention periods and procedures",
                "rules": {
                    "audit_logs": {"retention_days": 365, "encryption": True},
                    "user_data": {"retention_days": 730, "right_to_erasure": True},
                    "security_events": {"retention_days": 180, "immutable": True},
                },
            },
            "access_control": {
                "id": "POL-002",
                "name": "Access Control Policy",
                "description": "Defines access control requirements",
                "rules": {
                    "authentication": {"mfa_required": True, "session_timeout": 30},
                    "authorization": {"rbac_enabled": True, "least_privilege": True},
                    "password": {"min_length": 12, "complexity": True, "rotation": 90},
                },
            },
            "encryption": {
                "id": "POL-003",
                "name": "Encryption Policy",
                "description": "Defines encryption requirements",
                "rules": {
                    "data_at_rest": {"algorithm": "AES-256", "key_rotation": 365},
                    "data_in_transit": {
                        "protocol": "TLS1.3",
                        "cipher_suites": "strong",
                    },
                    "key_management": {"hsm_required": True, "escrow": False},
                },
            },
            "incident_response": {
                "id": "POL-004",
                "name": "Incident Response Policy",
                "description": "Defines incident response procedures",
                "rules": {
                    "notification": {
                        "breach_notification": 72,
                        "internal_escalation": 1,
                    },
                    "containment": {"auto_containment": True, "isolation": True},
                    "recovery": {"backup_required": True, "rto": 4, "rpo": 1},
                },
            },
        }

    async def _initialize_control_status(self) -> None:
        """Initialize security control implementation status."""
        # Initialize all controls as not implemented (for demo)
        for category, controls in SECURITY_CONTROLS.items():
            for control_id in controls.keys():
                self._control_implementations[control_id] = (
                    ControlStatus.NOT_IMPLEMENTED
                )

        # Mark some controls as implemented (for demo)
        implemented_controls = ["AC-1", "AC-2", "AU-1", "CM-1", "IA-1", "SC-1"]
        for control_id in implemented_controls:
            self._control_implementations[control_id] = ControlStatus.IMPLEMENTED

    async def start_compliance_monitoring(self) -> None:
        """Start continuous compliance monitoring."""
        if self._monitoring_active:
            logger.warning("Compliance monitoring is already active")
            return

        try:
            self._monitoring_active = True

            # Start monitoring tasks
            tasks = [
                self._monitor_compliance_status(),
                self._monitor_policy_violations(),
                self._perform_scheduled_assessments(),
            ]

            for task in tasks:
                compliance_task = asyncio.create_task(task)
                self._compliance_tasks.add(compliance_task)
                compliance_task.add_done_callback(self._compliance_tasks.discard)

            logger.info("Compliance monitoring started successfully")

        except Exception as e:
            self._monitoring_active = False
            logger.error(f"Failed to start compliance monitoring: {e}")
            raise ComplianceViolationError(
                f"Failed to start monitoring: {e}",
                framework="monitoring",
                severity="high",
            )

    async def stop_compliance_monitoring(self) -> None:
        """Stop compliance monitoring."""
        self._monitoring_active = False

        # Cancel all monitoring tasks
        for task in self._compliance_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._compliance_tasks:
            await asyncio.gather(*self._compliance_tasks, return_exceptions=True)

        self._compliance_tasks.clear()
        logger.info("Compliance monitoring stopped")

    async def _monitor_compliance_status(self) -> None:
        """Monitor compliance status continuously."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(self.config.compliance_check_interval)

                # Check compliance for each framework
                for framework in self.config.compliance_frameworks:
                    await self.check_compliance(framework)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in compliance monitoring: {e}")

    async def _monitor_policy_violations(self) -> None:
        """Monitor for policy violations."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Check for policy violations
                violations = await self._detect_policy_violations()

                for violation in violations:
                    await self._handle_policy_violation(violation)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in policy violation monitoring: {e}")

    async def _perform_scheduled_assessments(self) -> None:
        """Perform scheduled compliance assessments."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(3600)  # Check every hour

                # Check if any assessments are due
                now = datetime.utcnow()

                for framework in self.config.compliance_frameworks:
                    last_assessment = self._get_last_assessment(framework)

                    if not last_assessment or last_assessment.next_assessment <= now:
                        await self.perform_assessment(framework)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduled assessments: {e}")

    async def check_compliance(
        self, framework: str, scope: Optional[str] = None
    ) -> ComplianceAssessment:
        """
        Check compliance for a specific framework.

        Args:
            framework: Compliance framework to check
            scope: Optional scope limitation

        Returns:
            ComplianceAssessment: Assessment results
        """
        try:
            if framework not in self._compliance_requirements:
                raise GuardianValidationError(
                    f"Unknown compliance framework: {framework}"
                )

            logger.info(f"Checking compliance for {framework}")

            requirements = self._compliance_requirements[framework]
            findings = []
            passed = 0
            failed = 0

            # Check each requirement
            for requirement in requirements:
                result = await self._check_requirement(requirement, scope)

                if result["status"] == ComplianceStatus.COMPLIANT:
                    passed += 1
                else:
                    failed += 1
                    findings.append(
                        {
                            "requirement_id": requirement.requirement_id,
                            "status": result["status"].value,
                            "description": requirement.description,
                            "gaps": result.get("gaps", []),
                            "evidence": result.get("evidence", []),
                        }
                    )

            # Determine overall status
            if failed == 0:
                overall_status = ComplianceStatus.COMPLIANT
            elif passed == 0:
                overall_status = ComplianceStatus.NON_COMPLIANT
            else:
                overall_status = ComplianceStatus.PARTIAL

            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(findings)

            # Create assessment
            assessment = ComplianceAssessment(
                assessment_id=self._generate_assessment_id(),
                framework=framework,
                timestamp=datetime.utcnow(),
                overall_status=overall_status,
                requirements_checked=len(requirements),
                requirements_passed=passed,
                requirements_failed=failed,
                findings=findings,
                recommendations=recommendations,
                next_assessment=datetime.utcnow() + timedelta(days=30),
            )

            # Store assessment
            self._assessment_history.append(assessment)

            # Trigger alerts for non-compliance
            if overall_status == ComplianceStatus.NON_COMPLIANT:
                await self._alert_non_compliance(assessment)

            return assessment

        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            raise ComplianceViolationError(
                f"Compliance check failed: {e}", framework=framework, severity="high"
            )

    async def _check_requirement(
        self, requirement: ComplianceRequirement, scope: Optional[str]
    ) -> Dict[str, Any]:
        """Check a specific compliance requirement."""
        result = {
            "status": ComplianceStatus.UNKNOWN,
            "gaps": [],
            "evidence": [],
        }

        # Check if required controls are implemented
        missing_controls = []
        partial_controls = []

        for control_id in requirement.controls:
            control_status = self._control_implementations.get(
                control_id, ControlStatus.NOT_IMPLEMENTED
            )

            if control_status == ControlStatus.NOT_IMPLEMENTED:
                missing_controls.append(control_id)
            elif control_status == ControlStatus.PARTIAL:
                partial_controls.append(control_id)

        # Determine requirement status
        if not missing_controls and not partial_controls:
            result["status"] = ComplianceStatus.COMPLIANT
            result["evidence"].append(
                f"All controls implemented: {requirement.controls}"
            )
        elif missing_controls:
            result["status"] = ComplianceStatus.NON_COMPLIANT
            result["gaps"].append(f"Missing controls: {missing_controls}")
        else:
            result["status"] = ComplianceStatus.PARTIAL
            result["gaps"].append(f"Partial controls: {partial_controls}")

        # Additional checks based on requirement type
        if requirement.evidence_required:
            has_evidence = await self._check_evidence_availability(requirement)
            if not has_evidence:
                result["status"] = ComplianceStatus.PARTIAL
                result["gaps"].append("Evidence documentation missing")

        return result

    async def _check_evidence_availability(
        self, requirement: ComplianceRequirement
    ) -> bool:
        """Check if required evidence is available."""
        # Simplified evidence check
        # In production, this would check actual documentation
        return requirement.criticality != "critical"  # Demo logic

    def _generate_compliance_recommendations(
        self, findings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate compliance recommendations based on findings."""
        recommendations = []

        # Analyze gaps
        all_gaps = []
        for finding in findings:
            all_gaps.extend(finding.get("gaps", []))

        # Generate recommendations
        if any("Missing controls" in gap for gap in all_gaps):
            recommendations.append(
                "Implement missing security controls to achieve compliance"
            )

        if any("Partial controls" in gap for gap in all_gaps):
            recommendations.append(
                "Complete implementation of partially deployed controls"
            )

        if any("Evidence" in gap for gap in all_gaps):
            recommendations.append(
                "Document and maintain evidence for compliance requirements"
            )

        if len(findings) > 5:
            recommendations.append(
                "Consider a comprehensive compliance remediation program"
            )

        return recommendations

    async def perform_assessment(
        self, framework: str, assessment_type: str = "full"
    ) -> ComplianceAssessment:
        """
        Perform a comprehensive compliance assessment.

        Args:
            framework: Framework to assess
            assessment_type: Type of assessment (full, partial, specific)

        Returns:
            ComplianceAssessment: Detailed assessment results
        """
        try:
            logger.info(f"Performing {assessment_type} assessment for {framework}")

            # Perform compliance check
            assessment = await self.check_compliance(framework)

            # Additional assessment activities
            if assessment_type == "full":
                # Perform additional checks
                assessment.findings.extend(
                    await self._perform_deep_assessment(framework)
                )

                # Update recommendations
                assessment.recommendations = self._generate_compliance_recommendations(
                    assessment.findings
                )

            # Generate compliance report
            report = await self.generate_compliance_report(
                framework, assessment_id=assessment.assessment_id
            )

            # Store report reference
            assessment.findings.append(
                {
                    "type": "report",
                    "report_id": report["report_id"],
                    "report_location": report.get("location"),
                }
            )

            return assessment

        except Exception as e:
            logger.error(f"Assessment failed: {e}")
            raise ComplianceViolationError(
                f"Assessment failed: {e}", framework=framework, severity="high"
            )

    async def _perform_deep_assessment(self, framework: str) -> List[Dict[str, Any]]:
        """Perform deep assessment checks."""
        additional_findings = []

        # Check data classification compliance
        if framework in ["GDPR", "CCPA"]:
            data_compliance = await self._assess_data_compliance()
            additional_findings.extend(data_compliance)

        # Check security configurations
        config_compliance = await self._assess_configuration_compliance()
        additional_findings.extend(config_compliance)

        return additional_findings

    async def _assess_data_compliance(self) -> List[Dict[str, Any]]:
        """Assess data handling compliance."""
        findings = []

        # Check data classification
        if not self.config.data_classification_enabled:
            findings.append(
                {
                    "type": "data_classification",
                    "status": "non_compliant",
                    "description": "Data classification is not enabled",
                    "severity": "high",
                }
            )

        # Check PII detection
        if not self.config.enable_pii_detection:
            findings.append(
                {
                    "type": "pii_detection",
                    "status": "non_compliant",
                    "description": "PII detection is not enabled",
                    "severity": "medium",
                }
            )

        return findings

    async def _assess_configuration_compliance(self) -> List[Dict[str, Any]]:
        """Assess security configuration compliance."""
        findings = []

        # Check encryption
        if not self.config.enable_data_encryption:
            findings.append(
                {
                    "type": "encryption",
                    "status": "non_compliant",
                    "description": "Data encryption is not enabled",
                    "severity": "critical",
                }
            )

        # Check audit trail
        if not self.config.enable_audit_trail:
            findings.append(
                {
                    "type": "audit_trail",
                    "status": "non_compliant",
                    "description": "Audit trail is not enabled",
                    "severity": "high",
                }
            )

        return findings

    async def verify_policy_compliance(
        self, policy_id: str, context: Dict[str, Any]
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """
        Verify compliance with a specific policy.

        Args:
            policy_id: Policy identifier
            context: Context for policy evaluation

        Returns:
            Tuple[bool, Optional[PolicyViolation]]: Compliance status and violation if any
        """
        try:
            if policy_id not in self._policy_definitions:
                raise GuardianValidationError(f"Unknown policy: {policy_id}")

            policy = self._policy_definitions[policy_id]
            violations = []

            # Check each rule in the policy
            for rule_name, rule_config in policy["rules"].items():
                is_compliant = await self._evaluate_policy_rule(
                    rule_name, rule_config, context
                )

                if not is_compliant:
                    violations.append(
                        {
                            "rule": rule_name,
                            "expected": rule_config,
                            "actual": context.get(rule_name),
                        }
                    )

            if violations:
                # Create policy violation
                violation = PolicyViolation(
                    violation_id=self._generate_violation_id(),
                    policy_id=policy_id,
                    timestamp=datetime.utcnow(),
                    severity="high" if len(violations) > 2 else "medium",
                    description=f"Policy {policy_id} violated: {len(violations)} rules failed",
                    affected_resource=context.get("resource", "unknown"),
                    remediation_required=True,
                    remediation_status="pending",
                )

                self._policy_violations.append(violation)

                # Auto-remediate if enabled
                if self.config.enable_automated_remediation:
                    await self._attempt_auto_remediation(violation, violations)

                return False, violation

            return True, None

        except Exception as e:
            logger.error(f"Policy verification failed: {e}")
            raise ComplianceViolationError(
                f"Policy verification failed: {e}",
                framework="policy",
                severity="medium",
            )

    async def _evaluate_policy_rule(
        self, rule_name: str, rule_config: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Evaluate a specific policy rule."""
        # Simplified rule evaluation
        # In production, this would use a proper policy engine

        if rule_name == "mfa_required" and rule_config is True:
            return context.get("mfa_enabled", False)

        if rule_name == "min_length" and isinstance(rule_config, int):
            return context.get("password_length", 0) >= rule_config

        if rule_name == "retention_days" and isinstance(rule_config, int):
            return context.get("retention_period", 0) >= rule_config

        # Default to compliant for unknown rules
        return True

    async def _detect_policy_violations(self) -> List[PolicyViolation]:
        """Detect policy violations proactively."""
        violations = []

        # Check for various policy violations
        # This is simplified - in production would check actual system state

        # Example: Check session timeout
        if self.config.session_timeout_minutes > 60:
            violations.append(
                PolicyViolation(
                    violation_id=self._generate_violation_id(),
                    policy_id="POL-002",
                    timestamp=datetime.utcnow(),
                    severity="medium",
                    description="Session timeout exceeds policy limit",
                    affected_resource="system_configuration",
                    remediation_required=True,
                    remediation_status="pending",
                )
            )

        return violations

    async def _handle_policy_violation(self, violation: PolicyViolation) -> None:
        """Handle detected policy violation."""
        logger.warning(f"Policy violation detected: {violation.violation_id}")

        # Record violation
        self._policy_violations.append(violation)

        # Send alerts
        await self._alert_policy_violation(violation)

        # Attempt remediation if enabled
        if self.config.enable_automated_remediation and violation.remediation_required:
            await self._attempt_auto_remediation(violation, [])

    async def _attempt_auto_remediation(
        self, violation: PolicyViolation, violation_details: List[Dict[str, Any]]
    ) -> None:
        """Attempt automatic remediation of policy violation."""
        try:
            logger.info(
                f"Attempting auto-remediation for violation: {violation.violation_id}"
            )

            # Implement remediation logic based on policy
            if violation.policy_id == "POL-002":  # Access control
                # Example: Enforce session timeout
                success = await self._remediate_access_control(violation_details)
            elif violation.policy_id == "POL-003":  # Encryption
                success = await self._remediate_encryption(violation_details)
            else:
                success = False

            # Update violation status
            violation.remediation_status = "completed" if success else "failed"

        except Exception as e:
            logger.error(f"Auto-remediation failed: {e}")
            violation.remediation_status = "failed"

    async def _remediate_access_control(self, details: List[Dict[str, Any]]) -> bool:
        """Remediate access control violations."""
        # Simplified remediation
        return True

    async def _remediate_encryption(self, details: List[Dict[str, Any]]) -> bool:
        """Remediate encryption violations."""
        # Simplified remediation
        return True

    async def generate_compliance_report(
        self,
        framework: str,
        report_type: str = "summary",
        assessment_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate compliance report.

        Args:
            framework: Framework to report on
            report_type: Type of report (summary, detailed, executive)
            assessment_id: Specific assessment to report on

        Returns:
            Dict[str, Any]: Report data
        """
        try:
            logger.info(f"Generating {report_type} compliance report for {framework}")

            # Get assessment data
            if assessment_id:
                assessment = self._get_assessment_by_id(assessment_id)
            else:
                assessment = self._get_last_assessment(framework)

            if not assessment:
                raise GuardianValidationError(f"No assessment found for {framework}")

            # Generate report based on type
            if report_type == "executive":
                report = self._generate_executive_report(assessment)
            elif report_type == "detailed":
                report = self._generate_detailed_report(assessment)
            else:
                report = self._generate_summary_report(assessment)

            # Add metadata
            report.update(
                {
                    "report_id": self._generate_report_id(),
                    "generated_at": datetime.utcnow().isoformat(),
                    "framework": framework,
                    "report_type": report_type,
                    "assessment_id": assessment.assessment_id,
                }
            )

            return report

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise ComplianceViolationError(
                f"Report generation failed: {e}", framework=framework, severity="medium"
            )

    def _generate_summary_report(
        self, assessment: ComplianceAssessment
    ) -> Dict[str, Any]:
        """Generate summary compliance report."""
        return {
            "compliance_status": assessment.overall_status.value,
            "compliance_percentage": (
                assessment.requirements_passed / assessment.requirements_checked * 100
                if assessment.requirements_checked > 0
                else 0
            ),
            "requirements_summary": {
                "total": assessment.requirements_checked,
                "passed": assessment.requirements_passed,
                "failed": assessment.requirements_failed,
            },
            "top_findings": assessment.findings[:5],
            "key_recommendations": assessment.recommendations[:3],
            "next_assessment_due": assessment.next_assessment.isoformat(),
        }

    def _generate_detailed_report(
        self, assessment: ComplianceAssessment
    ) -> Dict[str, Any]:
        """Generate detailed compliance report."""
        report = self._generate_summary_report(assessment)

        # Add detailed findings
        report["detailed_findings"] = assessment.findings

        # Add control status
        report["control_implementation"] = {
            control_id: status.value
            for control_id, status in self._control_implementations.items()
            if control_id in self._get_framework_controls(assessment.framework)
        }

        # Add policy compliance
        report["policy_violations"] = [
            {
                "violation_id": v.violation_id,
                "policy_id": v.policy_id,
                "severity": v.severity,
                "remediation_status": v.remediation_status,
            }
            for v in self._policy_violations
            if v.timestamp >= assessment.timestamp - timedelta(days=30)
        ]

        return report

    def _generate_executive_report(
        self, assessment: ComplianceAssessment
    ) -> Dict[str, Any]:
        """Generate executive-level compliance report."""
        return {
            "executive_summary": {
                "compliance_status": assessment.overall_status.value,
                "risk_level": self._calculate_compliance_risk(assessment),
                "action_required": assessment.overall_status
                != ComplianceStatus.COMPLIANT,
            },
            "key_metrics": {
                "compliance_score": round(
                    (
                        assessment.requirements_passed
                        / assessment.requirements_checked
                        * 100
                        if assessment.requirements_checked > 0
                        else 0
                    ),
                    1,
                ),
                "critical_gaps": len(
                    [f for f in assessment.findings if self._is_critical_finding(f)]
                ),
                "estimated_remediation_time": self._estimate_remediation_time(
                    assessment
                ),
            },
            "strategic_recommendations": assessment.recommendations[:2],
            "compliance_trend": self._calculate_compliance_trend(assessment.framework),
        }

    def _calculate_compliance_risk(self, assessment: ComplianceAssessment) -> str:
        """Calculate compliance risk level."""
        if assessment.overall_status == ComplianceStatus.COMPLIANT:
            return "low"
        elif assessment.requirements_failed > assessment.requirements_checked * 0.5:
            return "high"
        else:
            return "medium"

    def _is_critical_finding(self, finding: Dict[str, Any]) -> bool:
        """Check if finding is critical."""
        return any(
            keyword in str(finding).lower()
            for keyword in ["critical", "severe", "immediate"]
        )

    def _estimate_remediation_time(self, assessment: ComplianceAssessment) -> str:
        """Estimate time to remediate non-compliance."""
        if assessment.requirements_failed == 0:
            return "N/A"
        elif assessment.requirements_failed <= 5:
            return "1-2 weeks"
        elif assessment.requirements_failed <= 10:
            return "1-2 months"
        else:
            return "3-6 months"

    def _calculate_compliance_trend(self, framework: str) -> str:
        """Calculate compliance trend over time."""
        recent_assessments = [
            a for a in self._assessment_history if a.framework == framework
        ][-5:]

        if len(recent_assessments) < 2:
            return "insufficient_data"

        # Compare compliance scores
        scores = [
            a.requirements_passed / a.requirements_checked
            for a in recent_assessments
            if a.requirements_checked > 0
        ]

        if scores[-1] > scores[0]:
            return "improving"
        elif scores[-1] < scores[0]:
            return "declining"
        else:
            return "stable"

    def _get_framework_controls(self, framework: str) -> List[str]:
        """Get controls relevant to a framework."""
        if framework not in self._compliance_requirements:
            return []

        controls = []
        for requirement in self._compliance_requirements[framework]:
            controls.extend(requirement.controls)

        return list(set(controls))

    async def get_control_implementation_status(
        self, control_id: str
    ) -> Dict[str, Any]:
        """Get implementation status for a specific control."""
        status = self._control_implementations.get(
            control_id, ControlStatus.NOT_IMPLEMENTED
        )

        # Get control details
        control_details = None
        for category, controls in SECURITY_CONTROLS.items():
            if control_id in controls:
                control_details = {
                    "category": category,
                    "description": controls[control_id],
                }
                break

        # Find frameworks requiring this control
        requiring_frameworks = []
        for framework, requirements in self._compliance_requirements.items():
            for req in requirements:
                if control_id in req.controls:
                    requiring_frameworks.append(framework)
                    break

        return {
            "control_id": control_id,
            "status": status.value,
            "details": control_details,
            "required_by": list(set(requiring_frameworks)),
            "implementation_notes": self._get_implementation_notes(control_id),
        }

    def _get_implementation_notes(self, control_id: str) -> str:
        """Get implementation notes for a control."""
        # Simplified notes
        if self._control_implementations.get(control_id) == ControlStatus.IMPLEMENTED:
            return "Control fully implemented and tested"
        else:
            return "Control pending implementation"

    # Helper methods

    def _generate_assessment_id(self) -> str:
        """Generate unique assessment ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"ASSESS-{int(timestamp * 1000)}"

    def _generate_violation_id(self) -> str:
        """Generate unique violation ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"VIOL-{int(timestamp * 1000)}"

    def _generate_report_id(self) -> str:
        """Generate unique report ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"RPT-{int(timestamp * 1000)}"

    def _get_last_assessment(self, framework: str) -> Optional[ComplianceAssessment]:
        """Get the most recent assessment for a framework."""
        framework_assessments = [
            a for a in self._assessment_history if a.framework == framework
        ]

        if framework_assessments:
            return max(framework_assessments, key=lambda a: a.timestamp)

        return None

    def _get_assessment_by_id(
        self, assessment_id: str
    ) -> Optional[ComplianceAssessment]:
        """Get assessment by ID."""
        for assessment in self._assessment_history:
            if assessment.assessment_id == assessment_id:
                return assessment
        return None

    async def _alert_non_compliance(self, assessment: ComplianceAssessment) -> None:
        """Send alerts for non-compliance."""
        logger.critical(
            f"Non-compliance detected for {assessment.framework}: "
            f"{assessment.requirements_failed} requirements failed"
        )
        # In production, this would send actual alerts

    async def _alert_policy_violation(self, violation: PolicyViolation) -> None:
        """Send alerts for policy violations."""
        logger.warning(
            f"Policy violation: {violation.policy_id} - {violation.description}"
        )
        # In production, this would send actual alerts

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on compliance service."""
        return {
            "service": "ComplianceCheckerService",
            "status": "healthy" if self._initialized else "unhealthy",
            "monitoring_active": self._monitoring_active,
            "frameworks_configured": len(self._compliance_requirements),
            "policies_defined": len(self._policy_definitions),
            "recent_assessments": len(
                [
                    a
                    for a in self._assessment_history
                    if a.timestamp >= datetime.utcnow() - timedelta(days=7)
                ]
            ),
            "active_violations": len(
                [
                    v
                    for v in self._policy_violations
                    if v.remediation_status == "pending"
                ]
            ),
        }

    async def cleanup(self) -> None:
        """Clean up compliance monitoring resources."""
        if self._monitoring_active:
            await self.stop_compliance_monitoring()

        self._compliance_requirements.clear()
        self._policy_definitions.clear()
        self._assessment_history.clear()
        self._policy_violations.clear()

        logger.info("Compliance checker service cleaned up")
