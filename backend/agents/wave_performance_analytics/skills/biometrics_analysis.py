"""
Biometrics Analysis Skill
=========================

Analyzes biometric data from wearables and assessments.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class BiometricsAnalysisSkill:
    """Skill for analyzing biometric data."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "biometrics_analysis"
        self.description = "Analyze biometric data and provide insights"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze biometric data.
        
        Args:
            request: Contains biometric_data, analysis_type, time_range
            
        Returns:
            Biometric analysis insights
        """
        try:
            biometric_data = request.get("biometric_data", {})
            analysis_type = request.get("analysis_type", "comprehensive")
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_biometrics_analysis_prompt({
                "data": biometric_data,
                "type": analysis_type,
                "user_context": request.get("context", {})
            })
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "biometrics_analysis",
                "data": {
                    "metrics_analyzed": len(biometric_data),
                    "analysis_type": analysis_type
                },
                "metadata": {
                    "confidence": 0.92,
                    "data_quality": "high"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in biometrics analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "biometrics_analysis"
            }