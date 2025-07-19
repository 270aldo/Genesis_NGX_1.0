"""
Meal Plan Generation Skill
==========================

Generates personalized meal plans based on user profile and goals.
"""

from typing import Dict, Any, Optional
from core.logging_config import get_logger

logger = get_logger(__name__)


class MealPlanGenerationSkill:
    """Skill for generating personalized meal plans."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized meal plan.
        
        Args:
            request: Contains user profile and preferences
            
        Returns:
            Generated meal plan
        """
        try:
            user_profile = request.get("user_profile", {})
            
            # Use agent's prompt system
            prompt = self.agent.prompts.get_meal_plan_prompt(user_profile)
            
            # Generate meal plan using agent's LLM
            meal_plan = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "meal_plan": meal_plan,
                "skill_used": "meal_plan_generation",
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Error generating meal plan: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "meal_plan_generation"
            }