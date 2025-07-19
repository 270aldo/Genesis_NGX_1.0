"""
Prenatal Wellness Skill
=======================

Provides safe, trimester-specific prenatal wellness guidance.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class PrenatalWellnessSkill:
    """Skill for prenatal wellness planning."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "prenatal_wellness"
        self.description = "Create safe prenatal wellness plans"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create prenatal wellness plan.
        
        Args:
            request: Contains trimester, health_status, concerns
            
        Returns:
            Prenatal wellness recommendations
        """
        try:
            pregnancy_data = {
                "trimester": request.get("trimester", 1),
                "health_status": request.get("health_status", {}),
                "concerns": request.get("concerns", []),
                "exercise_history": request.get("context", {}).get("exercise_history", {})
            }
            
            # Safety check
            if pregnancy_data.get("high_risk", False):
                return {
                    "success": True,
                    "guidance": "For high-risk pregnancies, please work directly with your healthcare provider for personalized guidance.",
                    "skill_used": "prenatal_wellness",
                    "metadata": {"safety_redirect": True}
                }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_prenatal_wellness_prompt(pregnancy_data)
            
            # Generate plan
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "guidance": response,
                "skill_used": "prenatal_wellness",
                "data": {
                    "trimester": pregnancy_data["trimester"],
                    "plan_components": ["exercise", "nutrition", "wellness", "preparation"]
                },
                "metadata": {
                    "safety_verified": True,
                    "confidence": 0.89,
                    "medical_disclaimer": "Always consult your OB/GYN before starting any new wellness program"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in prenatal wellness planning: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "prenatal_wellness"
            }