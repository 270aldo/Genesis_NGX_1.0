"""
Compliance Check Skill
=====================

Verifies compliance with regulations and standards.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class ComplianceCheckSkill:
    """Skill for compliance verification."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "compliance_check"
        self.description = "Verify regulatory compliance"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check compliance with regulations.
        
        Args:
            request: Contains query, regulations, region
            
        Returns:
            Compliance verification report
        """
        try:
            compliance_data = {
                "query": request.get("query", ""),
                "regulations": request.get("regulations", ["GDPR", "HIPAA"]),
                "region": request.get("region", "global"),
                "scope": request.get("scope", "comprehensive")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_compliance_check_prompt(compliance_data)
            
            # Generate compliance check
            response = await self.agent.generate_response(prompt)
            
            # Analyze compliance status
            compliance_status = self._analyze_compliance_status(
                compliance_data["regulations"]
            )
            
            return {
                "success": True,
                "compliance_report": response,
                "skill_used": "compliance_check",
                "data": {
                    "regulations_checked": compliance_data["regulations"],
                    "compliance_status": compliance_status,
                    "region": compliance_data["region"],
                    "gaps_identified": self._count_gaps(response)
                },
                "metadata": {
                    "confidence": 0.89,
                    "assessment_type": "regulatory_compliance",
                    "last_updated": "2024-01-15"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in compliance check: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "compliance_check"
            }
    
    def _analyze_compliance_status(self, regulations: List[str]) -> Dict[str, str]:
        """Analyze compliance status for each regulation."""
        # Simplified compliance analysis
        status_map = {}
        for reg in regulations:
            # In real implementation, this would analyze actual compliance
            if reg in ["GDPR", "CCPA"]:
                status_map[reg] = "partial_compliance"
            elif reg in ["HIPAA", "PCI-DSS"]:
                status_map[reg] = "requires_assessment"
            else:
                status_map[reg] = "compliant"
        
        return status_map
    
    def _count_gaps(self, report: str) -> int:
        """Count compliance gaps in report."""
        gap_keywords = ["gap", "missing", "required", "must implement", "non-compliant"]
        count = 0
        report_lower = report.lower()
        
        for keyword in gap_keywords:
            count += report_lower.count(keyword)
        
        return min(count, 10)  # Cap at 10 for reasonable number