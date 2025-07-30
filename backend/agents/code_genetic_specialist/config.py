"""
CODE Agent Configuration
========================

Centralized configuration for the CODE Genetic Specialist agent.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from core.settings_lazy import settings


class CodeConfig(BaseModel):
    """Configuration for CODE agent."""
    
    model_config = {
        "protected_namespaces": (),
        "use_enum_values": True,
        "validate_assignment": True
    }
    
    # Agent identity
    agent_id: str = Field(default="code_genetic_specialist")
    agent_name: str = Field(default="CODE Genetic Specialist")
    agent_type: str = Field(default="genetic_specialist")
    
    # Model configuration
    model_id: str = Field(default="gemini-1.5-pro")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048)
    
    # A2A configuration
    a2a_server_url: str = Field(
        default_factory=lambda: f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"
    )
    
    # Personality settings
    personality_type: str = Field(default="analytical")  # analytical, supportive
    communication_style: str = Field(default="scientific")  # scientific, accessible, balanced
    
    # Feature flags
    enable_genetic_analysis: bool = Field(default=True)
    enable_epigenetics: bool = Field(default=True)
    enable_nutrigenomics: bool = Field(default=True)
    enable_sport_genetics: bool = Field(default=True)
    enable_risk_assessment: bool = Field(default=True)
    
    # Privacy and compliance
    enforce_consent: bool = Field(default=True)
    enable_data_encryption: bool = Field(default=True)
    gdpr_compliant: bool = Field(default=True)
    hipaa_compliant: bool = Field(default=True)
    
    # Cache settings
    cache_ttl: int = Field(default=3600)  # 1 hour
    enable_response_cache: bool = Field(default=True)
    
    # Genetic analysis settings
    max_variants_per_analysis: int = Field(default=1000)
    min_confidence_threshold: float = Field(default=0.85)
    
    # Capabilities
    capabilities: list[str] = Field(
        default=[
            "genetic_analysis",
            "epigenetic_optimization",
            "nutrigenomics_personalization",
            "sport_genetics_analysis",
            "risk_assessment",
            "personalized_medicine"
        ]
    )