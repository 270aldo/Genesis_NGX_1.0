"""
Chrononutrition Skill
=====================

Plans meal timing based on circadian rhythms.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class ChrononutritionSkill:
    """Skill for chrononutrition planning."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create chrononutrition plan based on schedule and circadian type.
        
        Args:
            request: Contains schedule and circadian preferences
            
        Returns:
            Chrononutrition plan
        """
        try:
            meal_times = request.get("meal_times", {
                "wake_time": "7:00 AM",
                "sleep_time": "11:00 PM"
            })
            circadian_type = request.get("circadian_type", "balanced")
            
            # Use agent's prompt system
            prompt = self.agent.prompts.get_chrononutrition_prompt(meal_times, circadian_type)
            
            # Generate plan using agent's LLM
            chrono_plan = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "chrono_plan": chrono_plan,
                "skill_used": "chrononutrition",
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error creating chrononutrition plan: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "chrononutrition"
            }