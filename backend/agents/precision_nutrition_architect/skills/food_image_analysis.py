"""
Food Image Analysis Skill
=========================

Analyzes food images to estimate nutritional content.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class FoodImageAnalysisSkill:
    """Skill for analyzing food images."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze food image for nutritional content.
        
        Args:
            request: Contains image data
            
        Returns:
            Food analysis results
        """
        try:
            image_data = request.get("image_data")
            
            if not image_data:
                return {
                    "success": False,
                    "error": "No image data provided",
                    "skill_used": "food_image_analysis"
                }
            
            # Use agent's vision capabilities
            if hasattr(self.agent, 'analyze_image'):
                # Analyze the image
                vision_result = await self.agent.analyze_image(image_data, analysis_type="full")
                
                # Get nutritional analysis prompt
                prompt = self.agent.prompts.get_food_image_analysis_prompt()
                prompt += f"\n\nImage analysis results: {vision_result}"
                
                # Generate nutritional analysis
                food_analysis = await self.agent.generate_response(prompt)
            else:
                # Fallback if vision not available
                food_analysis = "Food image analysis requires vision capabilities. Please describe the food instead."
            
            return {
                "success": True,
                "food_analysis": food_analysis,
                "skill_used": "food_image_analysis",
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error analyzing food image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "food_image_analysis"
            }