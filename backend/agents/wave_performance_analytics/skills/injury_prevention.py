"""
Injury Prevention Skill
=======================

Analyzes injury risk and provides prevention strategies.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class InjuryPreventionSkill:
    """Skill for injury prevention analysis."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "injury_prevention"
        self.description = "Analyze injury risk and prevention strategies"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze injury risk and provide prevention strategies.
        
        Args:
            request: Contains movement_data, training_load, risk_factors
            
        Returns:
            Injury prevention recommendations
        """
        try:
            risk_data = {
                "movement_patterns": request.get("movement_data", {}),
                "training_load": request.get("training_load", {}),
                "risk_factors": request.get("risk_factors", []),
                "injury_history": request.get("injury_history", [])
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_injury_prevention_prompt(risk_data)
            
            # Generate prevention strategies
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "injury_prevention",
                "data": {
                    "risk_factors_identified": len(risk_data["risk_factors"]),
                    "prevention_focus": "proactive"
                },
                "metadata": {
                    "assessment_type": "comprehensive",
                    "confidence": 0.88
                }
            }
            
        except Exception as e:
            logger.error(f"Error in injury prevention analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "injury_prevention"
            }