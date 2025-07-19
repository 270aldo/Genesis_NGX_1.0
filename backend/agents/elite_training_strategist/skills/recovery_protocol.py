"""
Recovery Protocol Skill
=======================

Designs recovery protocols based on training load and fatigue indicators.
"""

from typing import Dict, Any, Optional
from core.logging_config import get_logger

logger = get_logger(__name__)


class RecoveryProtocolSkill:
    """Skill for designing recovery protocols and managing fatigue."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design recovery protocol based on fatigue and training load.
        
        Args:
            request: Contains fatigue data and recovery context
            
        Returns:
            Customized recovery protocol
        """
        try:
            fatigue_data = request.get("fatigue_data", {
                "training_load": "moderate",
                "sleep_quality": "average",
                "hrv_status": "normal",
                "fatigue_level": 5,
                "soreness_level": 5
            })
            
            # Use agent's prompt system
            prompt = self.agent.prompts.get_recovery_protocol_prompt(fatigue_data)
            
            # Generate recovery protocol using agent's LLM
            protocol = await self.agent.generate_response(prompt)
            
            # Add safety checks
            if fatigue_data.get("fatigue_level", 5) > 8:
                protocol += "\n\n⚠️ HIGH FATIGUE ALERT: Consider taking a complete rest day or seeking professional guidance."
            
            return {
                "success": True,
                "recovery_protocol": protocol,
                "priority": self._calculate_priority(fatigue_data),
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Error in recovery protocol design: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_priority(self, fatigue_data: Dict[str, Any]) -> str:
        """Calculate recovery priority based on fatigue indicators."""
        fatigue_level = fatigue_data.get("fatigue_level", 5)
        soreness_level = fatigue_data.get("soreness_level", 5)
        
        avg_score = (fatigue_level + soreness_level) / 2
        
        if avg_score >= 8:
            return "critical"
        elif avg_score >= 6:
            return "high"
        elif avg_score >= 4:
            return "moderate"
        else:
            return "low"