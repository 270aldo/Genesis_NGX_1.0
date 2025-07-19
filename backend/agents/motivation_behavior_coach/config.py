"""
SPARK Agent Configuration
=========================

Configuration settings for SPARK Motivation & Behavior Coach agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SparkConfig(BaseModel):
    """Configuration for SPARK agent."""
    
    # Agent identification
    agent_id: str = "motivation_behavior_coach"
    agent_name: str = "SPARK"
    agent_type: str = "behavioral_specialist"
    
    # Model configuration
    model_id: str = "gemini-1.5-pro"
    temperature: float = 0.8
    
    # Personality settings
    personality_type: str = "prime"
    
    # Feature flags
    enable_motivation_boost: bool = True
    enable_habit_formation: bool = True
    enable_mindset_coaching: bool = True
    enable_accountability_check: bool = True
    enable_behavioral_analysis: bool = True
    enable_celebration_system: bool = True
    
    # Coaching settings
    motivation_style: str = "empowering"  # empowering, tough_love, gentle, adaptive
    check_in_frequency: str = "daily"
    celebration_threshold: float = 0.8  # 80% achievement triggers celebration
    
    # Behavioral settings
    habit_tracking_enabled: bool = True
    behavioral_nudge_frequency: int = 3  # times per day
    mindset_assessment_interval: int = 7  # days
    
    # Communication settings
    use_motivational_quotes: bool = True
    personalized_messaging: bool = True
    adaptive_tone: bool = True
    
    # Cache settings
    enable_response_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Capabilities
    capabilities: List[str] = Field(
        default_factory=lambda: [
            "motivational_coaching",
            "habit_formation_guidance",
            "mindset_transformation",
            "accountability_partnership",
            "behavioral_change_strategies",
            "celebration_and_recognition",
            "obstacle_problem_solving",
            "confidence_building",
            "resilience_training",
            "peak_performance_mindset"
        ]
    )