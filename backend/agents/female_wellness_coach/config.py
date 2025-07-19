"""
LUNA Agent Configuration
========================

Configuration settings for LUNA Female Wellness Coach agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LunaConfig(BaseModel):
    """Configuration for LUNA agent."""
    
    # Agent identification
    agent_id: str = "female_wellness_coach"
    agent_name: str = "LUNA"
    agent_type: str = "wellness_specialist"
    
    # Model configuration
    model_id: str = "gemini-1.5-pro"
    temperature: float = 0.8
    
    # Personality settings
    personality_type: str = "prime"
    
    # Feature flags
    enable_hormonal_health: bool = True
    enable_prenatal_support: bool = True
    enable_postpartum_recovery: bool = True
    enable_menopause_guidance: bool = True
    enable_stress_management: bool = True
    enable_nutrition_planning: bool = True
    
    # Health settings
    cycle_tracking_enabled: bool = True
    hormonal_analysis_depth: str = "comprehensive"
    wellness_assessment_interval: int = 7  # days
    
    # Safety settings
    medical_disclaimer_required: bool = True
    pregnancy_safety_checks: bool = True
    medication_interaction_warnings: bool = True
    
    # Cache settings
    enable_response_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Capabilities
    capabilities: List[str] = Field(
        default_factory=lambda: [
            "hormonal_health_optimization",
            "prenatal_wellness_planning",
            "postpartum_recovery_support",
            "menopause_transition_guidance",
            "stress_hormone_management",
            "female_specific_nutrition",
            "pelvic_floor_health",
            "bone_density_optimization",
            "fertility_awareness",
            "emotional_wellness_support"
        ]
    )