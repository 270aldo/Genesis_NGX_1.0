"""
Circadian Optimization Skill
============================

Optimizes circadian rhythm for better sleep and performance.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class CircadianOptimizationSkill:
    """Skill for circadian rhythm optimization."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "circadian_optimization"
        self.description = "Optimize circadian rhythm and sleep"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize circadian rhythm.
        
        Args:
            request: Contains sleep_data, schedule, environment, goals
            
        Returns:
            Circadian optimization protocol
        """
        try:
            circadian_data = {
                "current_sleep": request.get("sleep_data", {}),
                "daily_schedule": request.get("schedule", {}),
                "environment": request.get("environment", {}),
                "goals": request.get("goals", ["better_sleep"]),
                "chronotype": request.get("user_profile", {}).get("chronotype", "unknown")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_circadian_optimization_prompt(circadian_data)
            
            # Generate optimization plan
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "protocol": response,
                "skill_used": "circadian_optimization",
                "data": {
                    "intervention_count": self._count_interventions(circadian_data),
                    "difficulty_level": self._assess_difficulty(circadian_data),
                    "expected_timeline": "2-4 weeks"
                },
                "metadata": {
                    "approach": "chronobiology_based",
                    "confidence": 0.91,
                    "evidence_strong": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in circadian optimization: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "circadian_optimization"
            }
    
    def _count_interventions(self, circadian_data: Dict[str, Any]) -> int:
        """Count number of interventions needed."""
        count = 3  # Base interventions (light, timing, temperature)
        
        if circadian_data.get("current_sleep", {}).get("quality", "poor") == "poor":
            count += 2  # Additional interventions for poor sleepers
            
        if circadian_data.get("chronotype") == "unknown":
            count += 1  # Chronotype assessment
            
        return count
    
    def _assess_difficulty(self, circadian_data: Dict[str, Any]) -> str:
        """Assess implementation difficulty."""
        schedule = circadian_data.get("daily_schedule", {})
        
        if schedule.get("shift_work") or schedule.get("irregular_hours"):
            return "challenging"
        elif schedule.get("travel_frequency", "low") == "high":
            return "moderate"
        else:
            return "manageable"