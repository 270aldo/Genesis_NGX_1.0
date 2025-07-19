"""
Recovery Protocol Skill
=======================

Generates personalized recovery protocols based on fatigue and training data.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class RecoveryProtocolSkill:
    """Skill for generating recovery protocols."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "recovery_protocol"
        self.description = "Generate personalized recovery protocols"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recovery protocol.
        
        Args:
            request: Contains fatigue_level, recent_training, recovery_time
            
        Returns:
            Recovery protocol recommendations
        """
        try:
            recovery_data = {
                "fatigue_level": request.get("fatigue_level", "moderate"),
                "recent_training": request.get("recent_training", {}),
                "recovery_time": request.get("recovery_time", "24h"),
                "user_profile": request.get("user_profile", {})
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_recovery_protocol_prompt(recovery_data)
            
            # Generate protocol
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "recovery_protocol",
                "data": {
                    "protocol_duration": recovery_data["recovery_time"],
                    "fatigue_addressed": recovery_data["fatigue_level"]
                },
                "metadata": {
                    "protocol_type": "comprehensive",
                    "confidence": 0.89
                }
            }
            
        except Exception as e:
            logger.error(f"Error in recovery protocol generation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "recovery_protocol"
            }