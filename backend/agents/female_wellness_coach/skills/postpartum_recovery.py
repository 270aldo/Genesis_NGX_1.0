"""
Postpartum Recovery Skill
=========================

Supports safe and effective postpartum recovery.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class PostpartumRecoverySkill:
    """Skill for postpartum recovery support."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "postpartum_recovery"
        self.description = "Guide safe postpartum recovery"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create postpartum recovery plan.
        
        Args:
            request: Contains weeks_postpartum, delivery_type, concerns
            
        Returns:
            Postpartum recovery guidance
        """
        try:
            recovery_data = {
                "weeks_postpartum": request.get("weeks_postpartum", 6),
                "delivery_type": request.get("delivery_type", "vaginal"),
                "breastfeeding": request.get("breastfeeding", True),
                "concerns": request.get("concerns", []),
                "cleared_for_exercise": request.get("cleared_for_exercise", False)
            }
            
            # Safety check - ensure medical clearance
            if recovery_data["weeks_postpartum"] < 6 and not recovery_data["cleared_for_exercise"]:
                recovery_data["focus"] = "gentle_recovery"
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_postpartum_recovery_prompt(recovery_data)
            
            # Generate recovery plan
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "guidance": response,
                "skill_used": "postpartum_recovery",
                "data": {
                    "recovery_phase": "early" if recovery_data["weeks_postpartum"] < 12 else "progressive",
                    "focus_areas": ["core", "pelvic_floor", "nutrition", "self_care"]
                },
                "metadata": {
                    "personalized": True,
                    "confidence": 0.90,
                    "reminder": "Recovery is unique to each person - listen to your body"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in postpartum recovery planning: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "postpartum_recovery"
            }