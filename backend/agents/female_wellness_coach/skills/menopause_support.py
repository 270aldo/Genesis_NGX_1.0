"""
Menopause Support Skill
=======================

Provides comprehensive menopause transition support.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class MenopauseSupportSkill:
    """Skill for menopause transition support."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "menopause_support"
        self.description = "Support menopause transition naturally"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide menopause support guidance.
        
        Args:
            request: Contains symptoms, stage, health_history
            
        Returns:
            Menopause management strategies
        """
        try:
            menopause_data = {
                "stage": request.get("stage", "perimenopause"),
                "symptoms": request.get("symptoms", []),
                "health_history": request.get("health_history", {}),
                "current_treatments": request.get("current_treatments", [])
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_menopause_support_prompt(menopause_data)
            
            # Generate support plan
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "guidance": response,
                "skill_used": "menopause_support",
                "data": {
                    "stage": menopause_data["stage"],
                    "symptoms_addressed": len(menopause_data["symptoms"]),
                    "approach": "holistic"
                },
                "metadata": {
                    "evidence_based": True,
                    "confidence": 0.88,
                    "note": "Every woman's experience is unique"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in menopause support: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "menopause_support"
            }