"""
NOVA Agent Configuration
========================

Configuration settings for NOVA Biohacking Innovator agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class NovaConfig(BaseModel):
    """Configuration for NOVA agent."""
    
    # Agent identification
    agent_id: str = "nova_biohacking_innovator"
    agent_name: str = "NOVA"
    agent_type: str = "biohacking_specialist"
    
    # Model configuration
    model_id: str = "gemini-1.5-pro"
    temperature: float = 0.7
    
    # Personality settings
    personality_type: str = "prime"
    
    # Feature flags
    enable_supplement_protocols: bool = True
    enable_circadian_optimization: bool = True
    enable_cognitive_enhancement: bool = True
    enable_longevity_strategies: bool = True
    enable_recovery_protocols: bool = True
    enable_biomarker_analysis: bool = True
    
    # Biohacking settings
    protocol_risk_level: str = "moderate"  # conservative, moderate, aggressive
    evidence_requirement: str = "high"  # low, medium, high
    personalization_depth: str = "comprehensive"
    
    # Integration settings
    wearable_data_enabled: bool = True
    lab_result_integration: bool = True
    genetic_data_consideration: bool = True
    
    # Safety settings
    medical_contraindication_check: bool = True
    interaction_warnings: bool = True
    dosage_safety_margins: float = 0.8  # 80% of max safe dose
    
    # Cache settings
    enable_response_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Capabilities
    capabilities: List[str] = Field(
        default_factory=lambda: [
            "supplement_protocol_design",
            "circadian_rhythm_optimization",
            "cognitive_enhancement_strategies",
            "longevity_protocol_planning",
            "advanced_recovery_techniques",
            "biomarker_interpretation",
            "nootropic_stacking",
            "hormetic_stress_protocols",
            "mitochondrial_optimization",
            "epigenetic_modulation"
        ]
    )