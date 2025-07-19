"""
Goal Tracking Skill
===================

Tracks progress toward user-defined goals.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class GoalTrackingSkill:
    """Skill for goal achievement tracking."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "goal_tracking"
        self.description = "Track and analyze goal achievement"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track progress toward goals.
        
        Args:
            request: Contains goals, current_values, start_values
            
        Returns:
            Goal tracking analysis
        """
        try:
            goal_data = {
                "goals": request.get("goals", []),
                "current_values": request.get("current_values", {}),
                "start_values": request.get("start_values", {}),
                "deadlines": request.get("deadlines", {})
            }
            
            # Calculate progress for each goal
            progress_data = self._calculate_goal_progress(goal_data)
            goal_data["progress"] = progress_data
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_goal_tracking_prompt(goal_data)
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "goal_tracking",
                "data": {
                    "goals_tracked": len(goal_data["goals"]),
                    "progress_summary": progress_data,
                    "on_track": self._count_on_track_goals(progress_data)
                },
                "metadata": {
                    "analysis_type": "goal_achievement",
                    "confidence": 0.91,
                    "actionable": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in goal tracking: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "goal_tracking"
            }
    
    def _calculate_goal_progress(self, goal_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate progress percentage for each goal."""
        progress = {}
        
        for goal in goal_data["goals"]:
            goal_id = goal.get("id", goal.get("name", "unknown"))
            current = goal_data["current_values"].get(goal_id, 0)
            start = goal_data["start_values"].get(goal_id, 0)
            target = goal.get("target", 0)
            
            if target != start:
                percentage = ((current - start) / (target - start)) * 100
                progress[goal_id] = round(max(0, min(100, percentage)), 1)
            else:
                progress[goal_id] = 0.0
        
        return progress
    
    def _count_on_track_goals(self, progress_data: Dict[str, float]) -> int:
        """Count how many goals are on track (>= 50% progress)."""
        return sum(1 for p in progress_data.values() if p >= 50)