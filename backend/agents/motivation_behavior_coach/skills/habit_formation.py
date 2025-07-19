"""
Habit Formation Skill
=====================

Guides sustainable habit formation using behavioral science.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class HabitFormationSkill:
    """Skill for habit formation guidance."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "habit_formation"
        self.description = "Guide sustainable habit formation"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Guide habit formation process.
        
        Args:
            request: Contains habit_goal, current_habits, obstacles
            
        Returns:
            Habit formation strategy
        """
        try:
            habit_data = {
                "desired_habit": request.get("habit_goal", ""),
                "current_habits": request.get("current_habits", []),
                "obstacles": request.get("obstacles", []),
                "environment": request.get("environment", {}),
                "motivation": request.get("user_profile", {}).get("motivation_type", "intrinsic")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_habit_formation_prompt(habit_data)
            
            # Generate habit formation plan
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "coaching": response,
                "skill_used": "habit_formation",
                "data": {
                    "habit_complexity": self._assess_habit_complexity(habit_data["desired_habit"]),
                    "success_likelihood": self._calculate_success_likelihood(habit_data),
                    "key_strategies": ["habit_stacking", "implementation_intentions", "environment_design"]
                },
                "metadata": {
                    "approach": "behavioral_science_based",
                    "confidence": 0.89,
                    "actionable": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in habit formation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "habit_formation"
            }
    
    def _assess_habit_complexity(self, habit: str) -> str:
        """Assess the complexity of the desired habit."""
        if not habit:
            return "undefined"
        
        # Simple heuristic based on habit description
        habit_lower = habit.lower()
        if any(word in habit_lower for word in ["daily", "simple", "5 minutes", "one"]):
            return "simple"
        elif any(word in habit_lower for word in ["complex", "multiple", "hour", "advanced"]):
            return "complex"
        else:
            return "moderate"
    
    def _calculate_success_likelihood(self, habit_data: Dict[str, Any]) -> float:
        """Calculate likelihood of habit formation success."""
        score = 0.5  # Base score
        
        # Positive factors
        if len(habit_data["current_habits"]) > 2:
            score += 0.1  # Has existing habit foundation
        if habit_data["motivation"] == "intrinsic":
            score += 0.15  # Intrinsic motivation boost
        
        # Negative factors
        obstacle_count = len(habit_data["obstacles"])
        score -= min(0.2, obstacle_count * 0.05)  # Obstacles reduce likelihood
        
        return max(0.2, min(0.95, score))