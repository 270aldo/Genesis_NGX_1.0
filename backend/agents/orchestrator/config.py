"""
Orchestrator Agent Configuration
================================

Central configuration for the NEXUS orchestrator agent.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# Use lazy-initialized settings to prevent hanging
try:
    from core.settings_lazy import settings
except ImportError:
    from core.settings import Settings
    settings = Settings()


class OrchestratorConfig(BaseModel):
    """Configuration for NEXUS Orchestrator Agent."""
    
    model_config = {
        "protected_namespaces": (),
        "use_enum_values": True,
        "validate_assignment": True
    }
    
    # Agent identity
    agent_id: str = Field(default="ngx_nexus_orchestrator")
    agent_name: str = Field(default="NGX Nexus Orchestrator")
    agent_type: str = Field(default="orchestrator")
    version: str = Field(default="1.0.0")
    
    # Model configuration
    model_id: str = Field(default_factory=lambda: settings.ORCHESTRATOR_DEFAULT_MODEL_ID)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)
    
    # A2A Configuration
    a2a_server_url: Optional[str] = Field(
        default_factory=lambda: f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"
    )
    a2a_timeout: int = Field(default=30)
    
    # Capabilities
    capabilities: List[str] = Field(default_factory=lambda: [
        "analyze_user_intent",
        "route_to_specialized_agents",
        "synthesize_agent_responses",
        "manage_conversation_flow",
        "context_management",
        "multi_agent_coordination",
        "streaming_responses",
        "function_calling"
    ])
    
    # Intent to agent mapping
    intent_to_agent_map: Dict[str, List[str]] = Field(default_factory=lambda: {
        # Training - BLAZE
        "plan_entrenamiento": ["elite_training_strategist"],
        "elite_training_strategist": ["elite_training_strategist"],
        "generar_plan_entrenamiento": ["elite_training_strategist"],
        "training_ai": ["elite_training_strategist"],
        "consultar_ejercicio": ["elite_training_strategist"],
        "ejercicio": ["elite_training_strategist"],
        "workout": ["elite_training_strategist"],
        
        # Nutrition - SAGE
        "analizar_nutricion": ["precision_nutrition_architect"],
        "recomendar_receta": ["precision_nutrition_architect"],
        "nutrition_ai": ["precision_nutrition_architect"],
        "dieta": ["precision_nutrition_architect"],
        "comida": ["precision_nutrition_architect"],
        "meal_plan": ["precision_nutrition_architect"],
        
        # Progress - STELLA
        "registrar_actividad": ["progress_tracker"],
        "track_progress": ["progress_tracker"],
        "progress_analysis": ["progress_tracker"],
        "progress_ai": ["progress_tracker"],
        "metricas": ["progress_tracker"],
        "estadisticas": ["progress_tracker"],
        
        # Motivation - SPARK
        "motivation": ["motivation_behavior_coach"],
        "behavior_change": ["motivation_behavior_coach"],
        "habitos": ["motivation_behavior_coach"],
        "mindset": ["motivation_behavior_coach"],
        
        # Female Wellness - LUNA
        "female_health_query": ["female_wellness_coach"],
        "menstrual_cycle_query": ["female_wellness_coach"],
        "hormonal_support": ["female_wellness_coach"],
        "menopause_support": ["female_wellness_coach"],
        "salud_femenina": ["female_wellness_coach"],
        "ciclo_menstrual": ["female_wellness_coach"],
        
        # Biohacking - NOVA
        "biohacking": ["nova_biohacking_innovator"],
        "optimization": ["nova_biohacking_innovator"],
        "suplementos": ["nova_biohacking_innovator"],
        "nootropicos": ["nova_biohacking_innovator"],
        
        # Analytics - WAVE
        "analytics": ["wave_performance_analytics"],
        "performance_metrics": ["wave_performance_analytics"],
        "data_analysis": ["wave_performance_analytics"],
        
        # Genetics - CODE
        "genetic_analysis": ["code_genetic_specialist"],
        "genetic_profile": ["code_genetic_specialist"],
        "adn": ["code_genetic_specialist"],
        "genes": ["code_genetic_specialist"],
        
        # Multi-agent intents
        "transformation_plan": ["elite_training_strategist", "precision_nutrition_architect", "motivation_behavior_coach"],
        "health_check": ["progress_tracker", "wave_performance_analytics"],
        "recovery_plan": ["elite_training_strategist", "nova_biohacking_innovator"],
        "hormonal_optimization": ["female_wellness_coach", "nova_biohacking_innovator"],
        
        # General
        "general": ["motivation_behavior_coach"],
        "help": ["motivation_behavior_coach"],
        "start": ["motivation_behavior_coach", "progress_tracker"]
    })
    
    # Performance settings
    enable_caching: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)
    max_concurrent_agents: int = Field(default=5)
    circuit_breaker_threshold: int = Field(default=3)
    
    # Response settings
    enable_streaming: bool = Field(default=True)
    synthesis_strategy: str = Field(default="intelligent")  # "simple", "intelligent", "consensus"
    response_format: str = Field(default="structured")  # "text", "structured", "markdown"
    
    # Context management
    max_context_length: int = Field(default=4096)
    context_window_messages: int = Field(default=10)
    
    # Logging and monitoring
    enable_detailed_logging: bool = Field(default=True)
    metrics_enabled: bool = Field(default=True)


# Default orchestrator configuration
DEFAULT_ORCHESTRATOR_CONFIG = OrchestratorConfig()


# Agent metadata for discovery
ORCHESTRATOR_METADATA = {
    "id": DEFAULT_ORCHESTRATOR_CONFIG.agent_id,
    "name": DEFAULT_ORCHESTRATOR_CONFIG.agent_name,
    "description": "Central orchestrator that analyzes intents, routes to specialized agents, and synthesizes responses",
    "version": DEFAULT_ORCHESTRATOR_CONFIG.version,
    "capabilities": DEFAULT_ORCHESTRATOR_CONFIG.capabilities,
    "supported_languages": ["en", "es"],
    "requires_auth": True,
    "max_concurrent_requests": 100,
    "protocols": ["a2a", "adk", "http", "websocket"],
    "health_check": "/health",
    "status_endpoint": "/status"
}