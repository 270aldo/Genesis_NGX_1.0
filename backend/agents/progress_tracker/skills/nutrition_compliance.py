"""
Nutrition Compliance Skill
==========================

Tracks nutrition plan adherence and compliance.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class NutritionComplianceSkill:
    """Skill for nutrition compliance tracking."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "nutrition_compliance"
        self.description = "Track nutrition plan compliance"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze nutrition compliance data.
        
        Args:
            request: Contains nutrition_data, targets, preferences
            
        Returns:
            Nutrition compliance analysis
        """
        try:
            nutrition_data = {
                "daily_logs": request.get("nutrition_logs", []),
                "targets": request.get("nutrition_targets", {}),
                "compliance_days": request.get("compliance_days", 0),
                "total_days": request.get("total_days", 30)
            }
            
            # Calculate compliance metrics
            compliance_rate = (nutrition_data["compliance_days"] / 
                             max(1, nutrition_data["total_days"])) * 100
            
            nutrition_data["compliance_rate"] = round(compliance_rate, 1)
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_nutrition_compliance_prompt(nutrition_data)
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "nutrition_compliance",
                "data": {
                    "compliance_percentage": compliance_rate,
                    "days_tracked": nutrition_data["total_days"],
                    "consistency_level": self._get_consistency_level(compliance_rate)
                },
                "metadata": {
                    "analysis_type": "nutrition_adherence",
                    "confidence": 0.90,
                    "supportive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in nutrition compliance tracking: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "nutrition_compliance"
            }
    
    def _get_consistency_level(self, compliance_rate: float) -> str:
        """Determine consistency level based on compliance rate."""
        if compliance_rate >= 90:
            return "excellent"
        elif compliance_rate >= 75:
            return "good"
        elif compliance_rate >= 60:
            return "moderate"
        else:
            return "needs_improvement"