"""
Motivation Boost Skill
======================

Delivers powerful, personalized motivation.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class MotivationBoostSkill:
    """Skill for delivering motivational boosts."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "motivation_boost"
        self.description = "Deliver powerful personalized motivation"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide motivational boost.
        
        Args:
            request: Contains situation, emotional_state, user_profile
            
        Returns:
            Motivational message and guidance
        """
        try:
            context_data = {
                "situation": request.get("situation", "general"),
                "emotional_state": request.get("emotional_state", "neutral"),
                "recent_activity": request.get("recent_activity", {}),
                "goals": request.get("user_profile", {}).get("goals", []),
                "query": request.get("query", "")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_motivation_boost_prompt(context_data)
            
            # Generate motivational response
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "coaching": response,
                "skill_used": "motivation_boost",
                "data": {
                    "motivation_type": self._determine_motivation_type(context_data),
                    "intensity": self._calculate_intensity(context_data["emotional_state"])
                },
                "metadata": {
                    "coaching_style": self.agent.config.motivation_style,
                    "confidence": 0.92,
                    "empowering": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in motivation boost: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "motivation_boost"
            }
    
    def _determine_motivation_type(self, context: Dict[str, Any]) -> str:
        """Determine the type of motivation needed."""
        emotional_state = context.get("emotional_state", "neutral")
        
        if emotional_state == "low":
            return "supportive_encouragement"
        elif emotional_state == "high":
            return "challenge_and_growth"
        else:
            return "balanced_inspiration"
    
    def _calculate_intensity(self, emotional_state: str) -> str:
        """Calculate motivation intensity based on emotional state."""
        intensity_map = {
            "low": "gentle_but_powerful",
            "neutral": "energizing",
            "high": "amplifying"
        }
        return intensity_map.get(emotional_state, "energizing")