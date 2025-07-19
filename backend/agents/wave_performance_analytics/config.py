"""
WAVE Agent Configuration
========================

Configuration settings for WAVE Performance Analytics agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class WaveConfig(BaseModel):
    """Configuration for WAVE agent."""
    
    # Agent identification
    agent_id: str = "wave_performance_analytics"
    agent_name: str = "WAVE"
    agent_type: str = "performance_analytics"
    
    # Model configuration
    model_id: str = "gemini-1.5-pro"
    temperature: float = 0.7
    
    # Personality settings
    personality_type: str = "prime"
    
    # Feature flags
    enable_biometrics_analysis: bool = True
    enable_recovery_protocols: bool = True
    enable_performance_tracking: bool = True
    enable_injury_prevention: bool = True
    enable_sleep_analysis: bool = True
    
    # Analytics settings
    hrv_analysis_window: int = 7  # days
    performance_trend_window: int = 30  # days
    recovery_score_algorithm: str = "advanced"
    
    # Integration settings
    wearable_sync_interval: int = 300  # seconds
    supported_wearables: List[str] = Field(
        default_factory=lambda: [
            "fitbit", "garmin", "whoop", 
            "oura", "apple_watch", "polar"
        ]
    )
    
    # Cache settings
    enable_response_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Analytics thresholds
    hrv_alert_threshold: float = 0.7  # 70% of baseline
    fatigue_alert_threshold: float = 0.8
    overtraining_threshold: float = 0.85
    
    # Capabilities
    capabilities: List[str] = Field(
        default_factory=lambda: [
            "biometrics_analysis",
            "recovery_optimization",
            "performance_tracking",
            "injury_prevention",
            "sleep_quality_analysis",
            "hrv_protocols",
            "fatigue_management",
            "training_load_analysis",
            "readiness_scoring",
            "trend_analysis"
        ]
    )