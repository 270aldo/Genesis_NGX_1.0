"""
Biomarker Analysis Skill
========================

Analyzes biomarkers and provides health insights.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class BiomarkerAnalysisSkill:
    """Skill for analyzing biomarkers."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze biomarkers and provide insights.
        
        Args:
            request: Contains biomarker data
            
        Returns:
            Biomarker analysis
        """
        try:
            biomarkers = request.get("biomarkers", {})
            
            # Use agent's prompt system
            prompt = self.agent.prompts.get_biomarker_analysis_prompt(biomarkers)
            
            # Generate analysis using agent's LLM
            analysis = await self.agent.generate_response(prompt)
            
            # Check for critical values
            critical_markers = self._check_critical_values(biomarkers)
            if critical_markers:
                analysis = f"⚠️ CRITICAL VALUES DETECTED: {', '.join(critical_markers)}\n\nPlease consult a healthcare provider immediately.\n\n" + analysis
            
            return {
                "success": True,
                "analysis": analysis,
                "critical_markers": critical_markers,
                "skill_used": "biomarker_analysis",
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Error analyzing biomarkers: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "biomarker_analysis"
            }
    
    def _check_critical_values(self, biomarkers: Dict[str, Any]) -> List[str]:
        """Check for critical biomarker values."""
        critical = []
        
        # Example critical ranges (simplified)
        critical_ranges = {
            "glucose": (70, 140),  # mg/dL
            "hba1c": (4.0, 7.0),   # %
            "blood_pressure_systolic": (90, 140),  # mmHg
            "blood_pressure_diastolic": (60, 90)   # mmHg
        }
        
        for marker, (low, high) in critical_ranges.items():
            if marker in biomarkers:
                value = biomarkers[marker]
                if isinstance(value, dict):
                    value = value.get('value', 0)
                if value < low or value > high:
                    critical.append(marker)
        
        return critical