"""
Body Composition Skill
======================

Analyzes body composition changes and trends.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class BodyCompositionSkill:
    """Skill for body composition analysis."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "body_composition"
        self.description = "Analyze body composition changes"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze body composition data.
        
        Args:
            request: Contains composition_data, measurements, goals
            
        Returns:
            Body composition analysis
        """
        try:
            composition_data = {
                "weight": request.get("weight_data", {}),
                "body_fat": request.get("body_fat_data", {}),
                "muscle_mass": request.get("muscle_mass_data", {}),
                "measurements": request.get("measurements", {}),
                "photos": request.get("photo_progress", {})
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_body_composition_prompt(composition_data)
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "body_composition",
                "data": {
                    "metrics_tracked": len([k for k, v in composition_data.items() if v]),
                    "focus": "health_optimization"
                },
                "metadata": {
                    "analysis_type": "body_composition",
                    "confidence": 0.89,
                    "health_focused": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in body composition analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "body_composition"
            }