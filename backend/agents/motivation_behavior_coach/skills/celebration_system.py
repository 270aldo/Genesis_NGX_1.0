"""
Celebration System Skill
========================

Celebrates achievements and milestones powerfully.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class CelebrationSystemSkill:
    """Skill for celebrating achievements."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "celebration_system"
        self.description = "Celebrate achievements and milestones"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Celebrate achievement powerfully.
        
        Args:
            request: Contains achievement_data, milestone_type, journey_context
            
        Returns:
            Celebration message and recognition
        """
        try:
            achievement_data = {
                "achievement": request.get("achievement", "progress made"),
                "milestone_type": request.get("milestone_type", "general"),
                "effort_level": request.get("effort_level", "significant"),
                "journey_length": request.get("journey_context", {}).get("days", 0),
                "personal_significance": request.get("significance", "meaningful")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_celebration_prompt(achievement_data)
            
            # Generate celebration
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "coaching": response,
                "skill_used": "celebration_system",
                "data": {
                    "celebration_intensity": self._determine_celebration_intensity(achievement_data),
                    "recognition_elements": ["achievement", "effort", "growth", "identity"],
                    "momentum_building": True
                },
                "metadata": {
                    "emotional_impact": "high",
                    "confidence": 0.94,
                    "memorable": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in celebration system: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "celebration_system"
            }
    
    def _determine_celebration_intensity(self, achievement_data: Dict[str, Any]) -> str:
        """Determine how intense the celebration should be."""
        milestone_type = achievement_data.get("milestone_type", "general")
        effort_level = achievement_data.get("effort_level", "significant")
        
        # Major milestones get biggest celebrations
        if milestone_type in ["goal_achieved", "breakthrough", "transformation"]:
            return "epic_celebration"
        elif effort_level == "extraordinary" or achievement_data.get("journey_length", 0) > 90:
            return "powerful_recognition"
        else:
            return "meaningful_acknowledgment"