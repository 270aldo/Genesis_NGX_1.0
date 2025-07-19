"""
Risk Assessment Skill
=====================

Genetic risk assessment and prevention strategies.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class RiskAssessmentSkill:
    """Skill for genetic risk assessment."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "risk_assessment"
        self.description = "Assess genetic health risks and prevention"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform genetic risk assessment.
        
        Args:
            request: Contains genetic_data, family_history, health_data
            
        Returns:
            Risk assessment and prevention strategies
        """
        try:
            health_data = {
                "genetic_data": request.get("genetic_data", {}),
                "family_history": request.get("family_history", {}),
                "current_health": request.get("health_data", {})
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_risk_assessment_prompt(health_data)
            
            # Generate risk assessment
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "risk_assessment",
                "metadata": {
                    "assessment_type": "preventive",
                    "confidence": 0.91
                }
            }
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "risk_assessment"
            }