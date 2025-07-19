"""
Stress Management Skill
=======================

Female-specific stress and emotional wellness management.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class StressManagementSkill:
    """Skill for female-specific stress management."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "stress_management"
        self.description = "Manage stress with female-specific strategies"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create stress management plan.
        
        Args:
            request: Contains stress_levels, triggers, life_stage
            
        Returns:
            Stress management strategies
        """
        try:
            stress_data = {
                "stress_level": request.get("stress_level", "moderate"),
                "triggers": request.get("triggers", []),
                "life_stage": request.get("context", {}).get("life_stage", ""),
                "cycle_phase": request.get("cycle_phase", ""),
                "current_coping": request.get("current_coping", [])
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_stress_management_prompt(stress_data)
            
            # Generate strategies
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "guidance": response,
                "skill_used": "stress_management",
                "data": {
                    "triggers_addressed": len(stress_data["triggers"]),
                    "techniques": ["mindfulness", "movement", "nutrition", "social"]
                },
                "metadata": {
                    "holistic_approach": True,
                    "confidence": 0.89,
                    "reminder": "Self-care is not selfish"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in stress management planning: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "stress_management"
            }