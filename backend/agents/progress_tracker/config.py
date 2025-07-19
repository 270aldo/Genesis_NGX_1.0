"""
STELLA Agent Configuration
==========================

Configuration settings for STELLA Progress Tracker agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StellaConfig(BaseModel):
    """Configuration for STELLA agent."""
    
    # Agent identification
    agent_id: str = "progress_tracker"
    agent_name: str = "STELLA"
    agent_type: str = "progress_analyst"
    
    # Model configuration
    model_id: str = "gemini-1.5-pro"
    temperature: float = 0.6
    
    # Personality settings
    personality_type: str = "prime"
    
    # Feature flags
    enable_fitness_tracking: bool = True
    enable_nutrition_monitoring: bool = True
    enable_body_composition: bool = True
    enable_goal_management: bool = True
    enable_streak_tracking: bool = True
    enable_milestone_celebration: bool = True
    
    # Tracking settings
    measurement_frequency: str = "weekly"  # daily, weekly, biweekly, monthly
    progress_visualization: bool = True
    comparison_period: int = 30  # days
    
    # Integration settings
    wearable_sync_enabled: bool = True
    photo_progress_enabled: bool = True
    measurement_reminders: bool = True
    
    # Analytics settings
    trend_analysis_depth: int = 90  # days
    prediction_confidence_threshold: float = 0.75
    anomaly_detection_enabled: bool = True
    
    # Cache settings
    enable_response_cache: bool = True
    cache_ttl: int = 1800  # 30 minutes
    
    # Capabilities
    capabilities: List[str] = Field(
        default_factory=lambda: [
            "fitness_progress_tracking",
            "nutrition_compliance_monitoring",
            "body_composition_analysis",
            "goal_achievement_tracking",
            "streak_and_consistency_monitoring",
            "milestone_recognition",
            "progress_visualization",
            "trend_prediction",
            "comparative_analysis",
            "motivational_insights"
        ]
    )