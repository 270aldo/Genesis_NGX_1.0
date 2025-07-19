"""
Streak Tracking Skill
=====================

Monitors consistency streaks and habit formation.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from core.logging_config import get_logger

logger = get_logger(__name__)


class StreakTrackingSkill:
    """Skill for streak and consistency tracking."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "streak_tracking"
        self.description = "Track consistency streaks"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze streak and consistency data.
        
        Args:
            request: Contains streak_data, habits, check_ins
            
        Returns:
            Streak analysis and motivation
        """
        try:
            streak_data = {
                "current_streaks": request.get("current_streaks", {}),
                "longest_streaks": request.get("longest_streaks", {}),
                "habits_tracked": request.get("habits", []),
                "recent_check_ins": request.get("check_ins", [])
            }
            
            # Calculate streak statistics
            active_streaks = len([s for s in streak_data["current_streaks"].values() if s > 0])
            total_streak_days = sum(streak_data["current_streaks"].values())
            
            streak_data["active_count"] = active_streaks
            streak_data["total_days"] = total_streak_days
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_streak_tracking_prompt(streak_data)
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "streak_tracking",
                "data": {
                    "active_streaks": active_streaks,
                    "total_streak_days": total_streak_days,
                    "consistency_score": self._calculate_consistency_score(streak_data)
                },
                "metadata": {
                    "analysis_type": "consistency_tracking",
                    "confidence": 0.93,
                    "celebratory": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in streak tracking: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "streak_tracking"
            }
    
    def _calculate_consistency_score(self, streak_data: Dict[str, Any]) -> float:
        """Calculate overall consistency score."""
        if not streak_data["habits_tracked"]:
            return 0.0
        
        # Simple consistency score based on active streaks and check-ins
        habit_count = len(streak_data["habits_tracked"])
        active_ratio = streak_data["active_count"] / max(1, habit_count)
        
        # Recent check-in bonus
        recent_bonus = 0.1 if len(streak_data["recent_check_ins"]) >= 7 else 0
        
        score = (active_ratio * 0.8 + recent_bonus) * 100
        return round(min(100, score), 1)