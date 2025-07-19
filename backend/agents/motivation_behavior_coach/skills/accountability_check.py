"""
Accountability Check Skill
==========================

Provides supportive accountability and progress check-ins.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class AccountabilityCheckSkill:
    """Skill for accountability check-ins."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "accountability_check"
        self.description = "Provide accountability and progress check-ins"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct accountability check-in.
        
        Args:
            request: Contains progress_data, commitments, obstacles
            
        Returns:
            Accountability guidance and support
        """
        try:
            progress_data = {
                "commitments": request.get("commitments", []),
                "progress_made": request.get("recent_activity", {}),
                "obstacles_faced": request.get("obstacles", []),
                "days_since_last_check": request.get("days_since_check", 1),
                "overall_adherence": request.get("adherence_rate", 0.0)
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_accountability_check_prompt(progress_data)
            
            # Generate accountability response
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "coaching": response,
                "skill_used": "accountability_check",
                "data": {
                    "check_in_type": self._determine_check_in_type(progress_data),
                    "support_level": self._calculate_support_level(progress_data),
                    "next_check_in": self._suggest_next_check_in(progress_data)
                },
                "metadata": {
                    "tone": "supportive_yet_honest",
                    "confidence": 0.90,
                    "constructive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in accountability check: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "accountability_check"
            }
    
    def _determine_check_in_type(self, progress_data: Dict[str, Any]) -> str:
        """Determine the type of check-in needed."""
        adherence = progress_data.get("overall_adherence", 0)
        
        if adherence >= 0.8:
            return "celebration_and_growth"
        elif adherence >= 0.5:
            return "encouragement_and_adjustment"
        else:
            return "reset_and_support"
    
    def _calculate_support_level(self, progress_data: Dict[str, Any]) -> str:
        """Calculate the level of support needed."""
        obstacles = len(progress_data.get("obstacles_faced", []))
        adherence = progress_data.get("overall_adherence", 0)
        
        if obstacles > 3 or adherence < 0.4:
            return "high_support"
        elif obstacles > 1 or adherence < 0.7:
            return "moderate_support"
        else:
            return "maintenance_support"
    
    def _suggest_next_check_in(self, progress_data: Dict[str, Any]) -> str:
        """Suggest timing for next check-in."""
        support_level = self._calculate_support_level(progress_data)
        
        if support_level == "high_support":
            return "tomorrow"
        elif support_level == "moderate_support":
            return "in_2_days"
        else:
            return "weekly"