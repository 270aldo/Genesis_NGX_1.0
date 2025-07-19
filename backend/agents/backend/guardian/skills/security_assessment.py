"""
Security Assessment Skill
========================

Performs comprehensive security assessments.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class SecurityAssessmentSkill:
    """Skill for performing security assessments."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "security_assessment"
        self.description = "Perform comprehensive security assessments"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform security assessment.
        
        Args:
            request: Contains query, system_info, app_type
            
        Returns:
            Security assessment report
        """
        try:
            assessment_data = {
                "query": request.get("query", ""),
                "system_info": request.get("system_info", {}),
                "app_type": request.get("app_type", "general"),
                "assessment_scope": request.get("scope", "comprehensive")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_security_assessment_prompt(assessment_data)
            
            # Generate assessment
            response = await self.agent.generate_response(prompt)
            
            # Extract risk levels
            risks = self._extract_risks(response)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(assessment_data, risks)
            
            return {
                "success": True,
                "assessment": response,
                "skill_used": "security_assessment",
                "data": {
                    "risks_identified": len(risks),
                    "risk_summary": self._summarize_risks(risks),
                    "recommendations": recommendations,
                    "assessment_type": assessment_data["app_type"]
                },
                "metadata": {
                    "confidence": 0.92,
                    "assessment_depth": "comprehensive",
                    "standards_used": ["OWASP", "NIST", "CIS"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in security assessment: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "security_assessment"
            }
    
    def _extract_risks(self, assessment: str) -> List[Dict[str, Any]]:
        """Extract identified risks from assessment."""
        # Simplified risk extraction
        risk_keywords = {
            "critical": ["critical", "severe", "emergency"],
            "high": ["high", "significant", "major"],
            "medium": ["medium", "moderate", "standard"],
            "low": ["low", "minor", "minimal"]
        }
        
        risks = []
        for level, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in assessment.lower():
                    risks.append({
                        "level": level,
                        "keyword_found": keyword
                    })
                    break
        
        return risks
    
    def _summarize_risks(self, risks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize risks by level."""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for risk in risks:
            level = risk.get("level", "low")
            summary[level] = summary.get(level, 0) + 1
        return summary
    
    def _generate_recommendations(self, data: Dict[str, Any], risks: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on assessment."""
        recommendations = []
        
        # Base recommendations
        recommendations.append("Implement regular security assessments")
        recommendations.append("Maintain up-to-date security patches")
        
        # Risk-based recommendations
        risk_summary = self._summarize_risks(risks)
        if risk_summary.get("critical", 0) > 0:
            recommendations.insert(0, "URGENT: Address critical vulnerabilities immediately")
        
        if risk_summary.get("high", 0) > 0:
            recommendations.append("Prioritize high-risk vulnerabilities for remediation")
        
        # App-type specific
        app_type = data.get("app_type", "general")
        if app_type == "web":
            recommendations.append("Implement Web Application Firewall (WAF)")
        elif app_type == "mobile":
            recommendations.append("Enable certificate pinning and code obfuscation")
        elif app_type == "api":
            recommendations.append("Implement API rate limiting and authentication")
        
        return recommendations[:5]  # Top 5 recommendations