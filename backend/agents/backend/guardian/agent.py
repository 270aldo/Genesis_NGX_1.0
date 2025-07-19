"""
Guardian Security and Compliance Agent
=====================================

Security and compliance specialist with cybersecurity expertise.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

# Core imports
from agents.base.base_ngx_agent import BaseNGXAgent
from agents.base.adk_agent import ADKAgent
from adk import Skill
from infrastructure.adapters.a2a_adapter import a2a_adapter
from core.logging_config import get_logger

# Guardian-specific imports
from .config import GuardianConfig
from .prompts import GuardianPrompts
from .skills import (
    SecurityAssessmentSkill,
    ComplianceCheckSkill,
    VulnerabilityScanSkill,
    DataProtectionSkill,
    IncidentResponseSkill,
    ThreatIntelligenceSkill,
    PrivacyAuditSkill,
    SecurityEducationSkill
)

# Services
from .services.audit_trail_service import AuditTrailService
from .services.compliance_checker_service import ComplianceCheckerService
from .services.security_monitor_service import SecurityMonitorService

logger = get_logger(__name__)


class SecurityComplianceGuardian(BaseNGXAgent, ADKAgent):
    """
    Guardian agent specializing in security and compliance.
    
    Inherits from both BaseNGXAgent and ADKAgent for full compatibility
    with the NGX ecosystem and Google ADK framework.
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        """Initialize Guardian agent with configuration."""
        # Load configuration
        self.config = GuardianConfig()
        
        # Generate ID if not provided
        if not agent_id:
            agent_id = f"guardian_{uuid.uuid4().hex[:8]}"
        
        # Initialize base classes
        BaseNGXAgent.__init__(
            self,
            agent_id=agent_id,
            name=self.config.name,
            specialization=self.config.specialization,
            system_prompt=GuardianPrompts.get_base_instructions()
        )
        
        # Initialize ADKAgent
        ADKAgent.__init__(self, agent_id=agent_id)
        
        # Initialize prompts manager
        self.prompts = GuardianPrompts()
        
        # Initialize services
        self._init_services()
        
        # Initialize skills
        self._init_skills()
        
        # Register ADK skills
        self.adk_skills = self._create_adk_skills()
        
        logger.info(f"Guardian agent initialized: {self.name}")
    
    def _init_services(self):
        """Initialize Guardian services."""
        self.audit_service = AuditTrailService()
        self.compliance_service = ComplianceCheckerService()
        self.security_monitor = SecurityMonitorService()
    
    def _init_skills(self):
        """Initialize Guardian skills."""
        self.security_assessment_skill = SecurityAssessmentSkill(self)
        self.compliance_check_skill = ComplianceCheckSkill(self)
        self.vulnerability_scan_skill = VulnerabilityScanSkill(self)
        self.data_protection_skill = DataProtectionSkill(self)
        self.incident_response_skill = IncidentResponseSkill(self)
        self.threat_intelligence_skill = ThreatIntelligenceSkill(self)
        self.privacy_audit_skill = PrivacyAuditSkill(self)
        self.security_education_skill = SecurityEducationSkill(self)
    
    def _create_adk_skills(self) -> List[Skill]:
        """Create ADK skill definitions."""
        return [
            Skill(
                name="security_assessment",
                description="Perform comprehensive security assessments",
                handler=self._handle_security_assessment
            ),
            Skill(
                name="compliance_check",
                description="Verify regulatory compliance",
                handler=self._handle_compliance_check
            ),
            Skill(
                name="vulnerability_scan",
                description="Scan and analyze vulnerabilities",
                handler=self._handle_vulnerability_scan
            ),
            Skill(
                name="data_protection",
                description="Design data protection strategies",
                handler=self._handle_data_protection
            ),
            Skill(
                name="incident_response",
                description="Coordinate security incident response",
                handler=self._handle_incident_response
            ),
            Skill(
                name="threat_intelligence",
                description="Analyze threat intelligence",
                handler=self._handle_threat_intelligence
            ),
            Skill(
                name="privacy_audit",
                description="Conduct privacy audits",
                handler=self._handle_privacy_audit
            ),
            Skill(
                name="security_education",
                description="Provide security education",
                handler=self._handle_security_education
            )
        ]
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming request and route to appropriate skill.
        
        Args:
            request: Request containing user input and context
            
        Returns:
            Response from skill execution
        """
        try:
            # Log audit trail
            await self.audit_service.log_request(
                agent_id=self.agent_id,
                request=request
            )
            
            # Analyze request type
            skill_type = self._analyze_request_type(request)
            
            # Route to appropriate skill
            response = await self._route_to_skill(skill_type, request)
            
            # Log response
            await self.audit_service.log_response(
                agent_id=self.agent_id,
                response=response
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _analyze_request_type(self, request: Dict[str, Any]) -> str:
        """Analyze request to determine skill type."""
        query = request.get("message", "").lower()
        
        # Keyword-based routing
        if any(word in query for word in ["assess", "evaluation", "security check"]):
            return "security_assessment"
        elif any(word in query for word in ["compliance", "regulation", "gdpr", "hipaa"]):
            return "compliance_check"
        elif any(word in query for word in ["vulnerability", "scan", "cve"]):
            return "vulnerability_scan"
        elif any(word in query for word in ["protect", "encryption", "privacy"]):
            return "data_protection"
        elif any(word in query for word in ["incident", "breach", "attack"]):
            return "incident_response"
        elif any(word in query for word in ["threat", "intelligence", "ioc"]):
            return "threat_intelligence"
        elif any(word in query for word in ["audit", "privacy audit"]):
            return "privacy_audit"
        elif any(word in query for word in ["learn", "education", "training"]):
            return "security_education"
        else:
            return "security_assessment"  # Default
    
    async def _route_to_skill(self, skill_type: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate skill."""
        skill_map = {
            "security_assessment": self.security_assessment_skill,
            "compliance_check": self.compliance_check_skill,
            "vulnerability_scan": self.vulnerability_scan_skill,
            "data_protection": self.data_protection_skill,
            "incident_response": self.incident_response_skill,
            "threat_intelligence": self.threat_intelligence_skill,
            "privacy_audit": self.privacy_audit_skill,
            "security_education": self.security_education_skill
        }
        
        skill = skill_map.get(skill_type)
        if skill:
            return await skill.execute(request)
        else:
            return await self.security_assessment_skill.execute(request)
    
    # ADK Handler Methods
    async def _handle_security_assessment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for security assessment."""
        return await self.security_assessment_skill.execute(request)
    
    async def _handle_compliance_check(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for compliance check."""
        return await self.compliance_check_skill.execute(request)
    
    async def _handle_vulnerability_scan(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for vulnerability scan."""
        return await self.vulnerability_scan_skill.execute(request)
    
    async def _handle_data_protection(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for data protection."""
        return await self.data_protection_skill.execute(request)
    
    async def _handle_incident_response(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for incident response."""
        return await self.incident_response_skill.execute(request)
    
    async def _handle_threat_intelligence(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for threat intelligence."""
        return await self.threat_intelligence_skill.execute(request)
    
    async def _handle_privacy_audit(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for privacy audit."""
        return await self.privacy_audit_skill.execute(request)
    
    async def _handle_security_education(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for security education."""
        return await self.security_education_skill.execute(request)
    
    # A2A Integration
    async def handle_a2a_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A protocol requests."""
        try:
            # Validate request
            if not self._validate_a2a_request(request):
                return {
                    "success": False,
                    "error": "Invalid A2A request format"
                }
            
            # Process through standard flow
            return await self.process_request(request)
            
        except Exception as e:
            logger.error(f"A2A request error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _validate_a2a_request(self, request: Dict[str, Any]) -> bool:
        """Validate A2A request format."""
        required_fields = ["user_id", "session_id", "message"]
        return all(field in request for field in required_fields)
    
    # Compliance tracking
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get current compliance status."""
        return await self.compliance_service.get_overall_status()
    
    # Security metrics
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and KPIs."""
        return await self.security_monitor.get_metrics()
    
    # Audit trail
    async def get_audit_trail(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get audit trail with optional filters."""
        return await self.audit_service.get_audit_trail(filters)


# Alias for backward compatibility
GUARDIAN = SecurityComplianceGuardian