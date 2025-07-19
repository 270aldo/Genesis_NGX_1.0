"""
Esquemas para el agente BiohackingInnovator (NOVA).

Este módulo define los modelos Pydantic para las entradas y salidas
de las skills conversacionales del agente NOVA BiohackingInnovator.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# ===== ESQUEMAS CONVERSACIONALES PARA NOVA (ENTP - The Innovator) =====


class LongevityOptimizationConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre optimización de longevidad."""

    user_text: str = Field(..., description="Texto del usuario sobre longevidad")
    current_age: Optional[int] = Field(None, description="Edad actual del usuario")
    longevity_goals: Optional[List[str]] = Field(
        None, description="Objetivos específicos de longevidad"
    )
    current_biomarkers: Optional[Dict[str, Any]] = Field(
        None, description="Biomarcadores actuales conocidos"
    )
    research_interests: Optional[List[str]] = Field(
        None, description="Intereses en investigación de longevidad"
    )
    conversation_context: Optional[str] = Field(
        None, description="Contexto de la conversación"
    )
    experiment_openness: Optional[str] = Field(
        None, description="Apertura a experimentos (low, medium, high)"
    )


class LongevityOptimizationConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre optimización de longevidad."""

    exploration_response: str = Field(
        ..., description="Respuesta explorativa e innovadora sobre longevidad"
    )
    conversation_id: str = Field(..., description="ID único de la conversación")
    cutting_edge_insights: List[str] = Field(
        ..., description="Insights de investigación más reciente"
    )
    experimental_protocols: List[str] = Field(
        ..., description="Protocolos experimentales sugeridos"
    )
    scientific_curiosities: List[str] = Field(
        ..., description="Aspectos científicos fascinantes para explorar"
    )
    innovation_opportunities: List[str] = Field(
        ..., description="Oportunidades de innovación personal"
    )


class CognitiveEnhancementConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre mejora cognitiva."""

    user_text: str = Field(..., description="Texto del usuario sobre mejora cognitiva")
    cognitive_areas: Optional[List[str]] = Field(
        None,
        description="Áreas cognitivas de interés (memoria, atención, creatividad, etc.)",
    )
    current_performance: Optional[str] = Field(
        None, description="Rendimiento cognitivo actual percibido"
    )
    enhancement_methods: Optional[List[str]] = Field(
        None, description="Métodos de mejora ya intentados"
    )
    work_demands: Optional[str] = Field(
        None, description="Demandas cognitivas del trabajo/estudio"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class CognitiveEnhancementConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre mejora cognitiva."""

    cognitive_exploration: str = Field(
        ..., description="Respuesta explorativa sobre mejora cognitiva"
    )
    neuroplasticity_insights: List[str] = Field(
        ..., description="Insights sobre neuroplastilidad y optimización cerebral"
    )
    experimental_approaches: List[str] = Field(
        ..., description="Enfoques experimentales innovadores"
    )
    measurement_protocols: List[str] = Field(
        ..., description="Protocolos para medir mejoras cognitivas"
    )
    personalized_experiments: List[str] = Field(
        ..., description="Experimentos personalizados sugeridos"
    )


class HormonalOptimizationConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre optimización hormonal."""

    user_text: str = Field(..., description="Texto del usuario sobre hormonas")
    gender: Optional[str] = Field(None, description="Género del usuario")
    age_range: Optional[str] = Field(
        None, description="Rango de edad (20s, 30s, 40s, etc.)"
    )
    hormonal_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones hormonales específicas"
    )
    current_symptoms: Optional[List[str]] = Field(
        None, description="Síntomas actuales relacionados con hormonas"
    )
    lifestyle_factors: Optional[List[str]] = Field(
        None, description="Factores de estilo de vida relevantes"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class HormonalOptimizationConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre optimización hormonal."""

    hormonal_innovation_response: str = Field(
        ..., description="Respuesta innovadora sobre optimización hormonal"
    )
    systems_thinking_approach: str = Field(
        ..., description="Enfoque de pensamiento sistémico para hormonas"
    )
    cutting_edge_interventions: List[str] = Field(
        ..., description="Intervenciones de vanguardia en optimización hormonal"
    )
    biomarker_tracking: List[str] = Field(
        ..., description="Biomarcadores clave para rastrear"
    )
    experimental_protocols: List[str] = Field(
        ..., description="Protocolos experimentales para optimización"
    )
    interconnection_insights: List[str] = Field(
        ..., description="Insights sobre interconexiones hormonales"
    )


class TechnologyIntegrationConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre integración tecnológica."""

    user_text: str = Field(
        ..., description="Texto del usuario sobre tecnología en biohacking"
    )
    current_devices: Optional[List[str]] = Field(
        None, description="Dispositivos tecnológicos actuales"
    )
    tech_comfort_level: Optional[str] = Field(
        None,
        description="Nivel de comodidad con tecnología (beginner, intermediate, advanced)",
    )
    integration_goals: Optional[List[str]] = Field(
        None, description="Objetivos de integración tecnológica"
    )
    data_interests: Optional[List[str]] = Field(
        None, description="Tipos de datos de interés para rastrear"
    )
    budget_considerations: Optional[str] = Field(
        None, description="Consideraciones de presupuesto"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class TechnologyIntegrationConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre integración tecnológica."""

    tech_innovation_response: str = Field(
        ..., description="Respuesta innovadora sobre integración tecnológica"
    )
    emerging_technologies: List[str] = Field(
        ..., description="Tecnologías emergentes relevantes"
    )
    integration_strategies: List[str] = Field(
        ..., description="Estrategias para integrar tecnología efectivamente"
    )
    data_optimization: List[str] = Field(
        ..., description="Formas de optimizar el uso de datos"
    )
    future_tech_trends: List[str] = Field(
        ..., description="Tendencias tecnológicas futuras en biohacking"
    )
    experimental_setups: List[str] = Field(
        ..., description="Configuraciones experimentales con tecnología"
    )


class ExperimentalProtocolsConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre protocolos experimentales."""

    user_text: str = Field(..., description="Texto del usuario sobre experimentación")
    experimentation_experience: Optional[str] = Field(
        None,
        description="Experiencia previa con experimentación (none, some, extensive)",
    )
    areas_of_interest: Optional[List[str]] = Field(
        None, description="Áreas de interés para experimentar"
    )
    risk_tolerance: Optional[str] = Field(
        None, description="Tolerancia al riesgo (low, medium, high)"
    )
    time_availability: Optional[str] = Field(
        None, description="Disponibilidad de tiempo para experimentos"
    )
    measurement_preferences: Optional[List[str]] = Field(
        None, description="Preferencias de medición y seguimiento"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class ExperimentalProtocolsConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre protocolos experimentales."""

    experimental_enthusiasm_response: str = Field(
        ..., description="Respuesta entusiasta sobre experimentación científica"
    )
    innovative_protocols: List[str] = Field(
        ..., description="Protocolos innovadores para experimentar"
    )
    scientific_methodology: List[str] = Field(
        ..., description="Metodología científica aplicada al auto-hacking"
    )
    measurement_frameworks: List[str] = Field(
        ..., description="Marcos de medición para experimentos"
    )
    exploration_opportunities: List[str] = Field(
        ..., description="Oportunidades emocionantes de exploración"
    )
    curiosity_driven_approaches: List[str] = Field(
        ..., description="Enfoques impulsados por la curiosidad científica"
    )
