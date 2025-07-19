"""
Incident Response Skill
======================

Coordinates security incident response.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger
import time

logger = get_logger(__name__)


class IncidentResponseSkill:
    """Skill for incident response coordination."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "incident_response"
        self.description = "Coordinate security incident response"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate incident response.
        
        Args:
            request: Contains incident_type, severity, context
            
        Returns:
            Incident response plan
        """
        try:
            incident_data = {
                "incident_type": request.get("incident_type", "unknown"),
                "severity": request.get("severity", "medium"),
                "context": request.get("context", {}),
                "affected_systems": request.get("affected_systems", []),
                "timestamp": request.get("timestamp", time.time())
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_incident_response_prompt(incident_data)
            
            # Generate response plan
            response = await self.agent.generate_response(prompt)
            
            # Generate incident ID
            incident_id = f"INC-{int(time.time())}"
            
            # Determine response priority
            priority = self._determine_priority(incident_data)
            
            return {
                "success": True,
                "response_plan": response,
                "skill_used": "incident_response",
                "data": {
                    "incident_id": incident_id,
                    "priority": priority,
                    "estimated_impact": self._estimate_impact(incident_data),
                    "response_phases": self._get_response_phases(),
                    "escalation_required": priority in ["critical", "high"]
                },
                "metadata": {
                    "confidence": 0.88,
                    "framework": "NIST_IR",
                    "sla_minutes": self._get_sla(priority)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in incident response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "incident_response"
            }
    
    def _determine_priority(self, incident_data: Dict[str, Any]) -> str:
        """Determine incident priority."""
        severity = incident_data.get("severity", "medium")
        incident_type = incident_data.get("incident_type", "").lower()
        
        # Critical incidents
        critical_types = ["data_breach", "ransomware", "system_compromise", "active_attack"]
        if severity == "critical" or any(crit in incident_type for crit in critical_types):
            return "critical"
        
        # High priority
        high_types = ["unauthorized_access", "malware", "dos_attack"]
        if severity == "high" or any(high in incident_type for high in high_types):
            return "high"
        
        # Medium priority
        if severity == "medium":
            return "medium"
        
        return "low"
    
    def _estimate_impact(self, incident_data: Dict[str, Any]) -> Dict[str, str]:
        """Estimate incident impact."""
        severity = incident_data.get("severity", "medium")
        affected_systems = incident_data.get("affected_systems", [])
        
        impact = {
            "business_impact": "low",
            "data_impact": "low",
            "operational_impact": "low",
            "reputational_impact": "low"
        }
        
        if severity == "critical":
            impact = {k: "high" for k in impact}
        elif severity == "high":
            impact["business_impact"] = "high"
            impact["operational_impact"] = "medium"
        elif len(affected_systems) > 5:
            impact["operational_impact"] = "high"
        
        return impact
    
    def _get_response_phases(self) -> List[Dict[str, str]]:
        """Get standard incident response phases."""
        return [
            {"phase": "detection", "status": "completed"},
            {"phase": "analysis", "status": "in_progress"},
            {"phase": "containment", "status": "pending"},
            {"phase": "eradication", "status": "pending"},
            {"phase": "recovery", "status": "pending"},
            {"phase": "lessons_learned", "status": "pending"}
        ]
    
    def _get_sla(self, priority: str) -> int:
        """Get SLA in minutes based on priority."""
        sla_map = {
            "critical": 15,
            "high": 60,
            "medium": 240,
            "low": 480
        }
        return sla_map.get(priority, 480)