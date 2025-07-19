"""
Esquemas Pydantic para el agente HELIX - Genetic Performance Specialist
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Esquemas de entrada y salida para las skills genéticas


class AnalyzeGeneticProfileInput(BaseModel):
    """Input para análisis de perfil genético"""

    user_id: str = Field(..., description="ID del usuario")
    genetic_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos genéticos del usuario (SNPs, variantes, etc.)"
    )
    analysis_type: str = Field(
        default="comprehensive",
        description="Tipo de análisis: comprehensive, fitness, nutrition, health_risks",
    )
    program_type: Optional[str] = Field(
        None, description="Tipo de programa NGX: PRIME o LONGEVITY"
    )


class AnalyzeGeneticProfileOutput(BaseModel):
    """Output del análisis genético"""

    genetic_summary: str = Field(..., description="Resumen del análisis genético")
    key_findings: List[Dict[str, Any]] = Field(
        ..., description="Hallazgos clave del análisis"
    )
    strengths: List[str] = Field(..., description="Fortalezas genéticas identificadas")
    considerations: List[str] = Field(..., description="Consideraciones genéticas")
    personalized_recommendations: Dict[str, Any] = Field(
        ..., description="Recomendaciones personalizadas basadas en genética"
    )


class GeneticRiskAssessmentInput(BaseModel):
    """Input para evaluación de riesgos genéticos"""

    user_id: str = Field(..., description="ID del usuario")
    genetic_markers: Dict[str, Any] = Field(
        ..., description="Marcadores genéticos relevantes"
    )
    family_history: Optional[Dict[str, Any]] = Field(
        None, description="Historial familiar de condiciones de salud"
    )
    focus_areas: Optional[List[str]] = Field(
        None, description="Áreas de enfoque: cardiovascular, metabolic, cognitive, etc."
    )


class GeneticRiskAssessmentOutput(BaseModel):
    """Output de evaluación de riesgos"""

    risk_profile: Dict[str, float] = Field(
        ..., description="Perfil de riesgo por condición (0-1 escala)"
    )
    preventive_strategies: List[Dict[str, Any]] = Field(
        ..., description="Estrategias preventivas personalizadas"
    )
    monitoring_recommendations: List[str] = Field(
        ..., description="Recomendaciones de monitoreo"
    )
    lifestyle_modifications: Dict[str, List[str]] = Field(
        ..., description="Modificaciones de estilo de vida recomendadas"
    )


class PersonalizeByGeneticsInput(BaseModel):
    """Input para personalización basada en genética"""

    user_id: str = Field(..., description="ID del usuario")
    genetic_profile: Dict[str, Any] = Field(
        ..., description="Perfil genético del usuario"
    )
    personalization_domain: str = Field(
        ..., description="Dominio: training, nutrition, recovery, supplementation"
    )
    current_plan: Optional[Dict[str, Any]] = Field(
        None, description="Plan actual del usuario"
    )


class PersonalizeByGeneticsOutput(BaseModel):
    """Output de personalización genética"""

    personalized_plan: Dict[str, Any] = Field(
        ..., description="Plan personalizado basado en genética"
    )
    genetic_optimizations: List[Dict[str, str]] = Field(
        ..., description="Optimizaciones específicas basadas en genes"
    )
    expected_outcomes: Dict[str, str] = Field(
        ..., description="Resultados esperados con base genética"
    )
    contraindications: Optional[List[str]] = Field(
        None, description="Contraindicaciones basadas en genética"
    )


class EpigeneticOptimizationInput(BaseModel):
    """Input para optimización epigenética"""

    user_id: str = Field(..., description="ID del usuario")
    current_lifestyle: Dict[str, Any] = Field(
        ..., description="Estilo de vida actual: dieta, ejercicio, sueño, estrés"
    )
    genetic_markers: Dict[str, Any] = Field(
        ..., description="Marcadores genéticos relevantes"
    )
    optimization_goals: List[str] = Field(
        ..., description="Objetivos de optimización epigenética"
    )


class EpigeneticOptimizationOutput(BaseModel):
    """Output de optimización epigenética"""

    epigenetic_plan: Dict[str, Any] = Field(
        ..., description="Plan de optimización epigenética"
    )
    lifestyle_interventions: Dict[str, List[str]] = Field(
        ..., description="Intervenciones de estilo de vida"
    )
    timeline: str = Field(..., description="Timeline esperado para cambios")
    monitoring_protocol: Dict[str, Any] = Field(
        ..., description="Protocolo de monitoreo de cambios epigenéticos"
    )


class NutrigenomicsInput(BaseModel):
    """Input para análisis nutrigenómico"""

    user_id: str = Field(..., description="ID del usuario")
    genetic_variants: Dict[str, Any] = Field(
        ..., description="Variantes genéticas relacionadas con nutrición"
    )
    dietary_preferences: Optional[List[str]] = Field(
        None, description="Preferencias dietéticas del usuario"
    )
    health_goals: List[str] = Field(..., description="Objetivos de salud del usuario")


class NutrigenomicsOutput(BaseModel):
    """Output de análisis nutrigenómico"""

    nutritional_profile: Dict[str, Any] = Field(
        ..., description="Perfil nutricional personalizado"
    )
    macro_recommendations: Dict[str, float] = Field(
        ..., description="Recomendaciones de macronutrientes (%)"
    )
    micro_recommendations: Dict[str, str] = Field(
        ..., description="Recomendaciones de micronutrientes"
    )
    food_sensitivities: List[str] = Field(
        ..., description="Sensibilidades alimentarias potenciales"
    )
    optimal_foods: List[str] = Field(
        ..., description="Alimentos óptimos según genética"
    )


class SportGeneticsInput(BaseModel):
    """Input para genética deportiva"""

    user_id: str = Field(..., description="ID del usuario")
    athletic_genes: Dict[str, Any] = Field(
        ..., description="Genes relacionados con rendimiento atlético"
    )
    sport_type: Optional[str] = Field(
        None, description="Tipo de deporte o actividad física"
    )
    performance_goals: List[str] = Field(..., description="Objetivos de rendimiento")


class SportGeneticsOutput(BaseModel):
    """Output de genética deportiva"""

    athletic_profile: Dict[str, Any] = Field(
        ..., description="Perfil atlético genético"
    )
    strength_predisposition: str = Field(
        ..., description="Predisposición: power, endurance, mixed"
    )
    optimal_training_type: List[str] = Field(
        ..., description="Tipos de entrenamiento óptimos"
    )
    recovery_profile: Dict[str, Any] = Field(
        ..., description="Perfil de recuperación genética"
    )
    injury_susceptibility: Dict[str, float] = Field(
        ..., description="Susceptibilidad a lesiones por tipo"
    )


# Artifacts para almacenar análisis genéticos
class GeneticAnalysisArtifact(BaseModel):
    """Artifact para almacenar análisis genético completo"""

    analysis_id: str = Field(..., description="ID único del análisis")
    user_id: str = Field(..., description="ID del usuario")
    analysis_date: datetime = Field(..., description="Fecha del análisis")
    genetic_profile: Dict[str, Any] = Field(..., description="Perfil genético completo")
    key_insights: List[Dict[str, Any]] = Field(
        ..., description="Insights clave del análisis"
    )
    recommendations: Dict[str, List[str]] = Field(
        ..., description="Recomendaciones por categoría"
    )
    program_adaptations: Dict[str, Any] = Field(
        ..., description="Adaptaciones específicas para NGX PRIME/LONGEVITY"
    )
    confidence_scores: Dict[str, float] = Field(
        ..., description="Scores de confianza por análisis"
    )
    next_review_date: datetime = Field(
        ..., description="Fecha recomendada para próxima revisión"
    )


# Esquemas conversacionales para CODE - Genetic Performance Specialist


class GeneticAnalysisConversationInput(BaseModel):
    """Input para conversación sobre análisis genético"""

    message: str = Field(..., description="Mensaje del usuario sobre análisis genético")
    user_id: str = Field(..., description="ID del usuario")
    genetic_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos genéticos disponibles del usuario"
    )
    context: Optional[str] = Field(
        None, description="Contexto adicional de la conversación"
    )
    analysis_focus: Optional[str] = Field(
        None, description="Enfoque específico: profile, risks, optimization"
    )


class GeneticAnalysisConversationOutput(BaseModel):
    """Output de conversación sobre análisis genético"""

    response: str = Field(..., description="Respuesta del especialista genético")
    scientific_insights: List[str] = Field(
        ..., description="Insights científicos clave"
    )
    genetic_implications: Dict[str, Any] = Field(
        ..., description="Implicaciones genéticas identificadas"
    )
    follow_up_suggestions: List[str] = Field(
        ..., description="Sugerencias de seguimiento"
    )
    confidence_level: str = Field(
        ..., description="Nivel de confianza: high, moderate, preliminary"
    )


class NutrigenomicsConversationInput(BaseModel):
    """Input para conversación sobre nutrigenómica"""

    message: str = Field(
        ..., description="Mensaje del usuario sobre nutrición genética"
    )
    user_id: str = Field(..., description="ID del usuario")
    dietary_context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto dietético actual del usuario"
    )
    nutrition_goals: Optional[List[str]] = Field(
        None, description="Objetivos nutricionales específicos"
    )
    genetic_variants: Optional[Dict[str, Any]] = Field(
        None, description="Variantes genéticas nutricionales conocidas"
    )


class NutrigenomicsConversationOutput(BaseModel):
    """Output de conversación sobre nutrigenómica"""

    response: str = Field(..., description="Respuesta especializada en nutrigenómica")
    nutritional_insights: List[str] = Field(..., description="Insights nutricionales")
    genetic_food_recommendations: List[str] = Field(
        ..., description="Recomendaciones alimentarias basadas en genética"
    )
    metabolic_considerations: Dict[str, str] = Field(
        ..., description="Consideraciones metabólicas específicas"
    )
    implementation_tips: List[str] = Field(
        ..., description="Consejos prácticos de implementación"
    )


class EpigeneticsConversationInput(BaseModel):
    """Input para conversación sobre epigenética"""

    message: str = Field(..., description="Mensaje del usuario sobre epigenética")
    user_id: str = Field(..., description="ID del usuario")
    lifestyle_factors: Optional[Dict[str, Any]] = Field(
        None, description="Factores de estilo de vida actuales"
    )
    epigenetic_goals: Optional[List[str]] = Field(
        None, description="Objetivos de modificación epigenética"
    )
    environmental_context: Optional[str] = Field(
        None, description="Contexto ambiental del usuario"
    )


class EpigeneticsConversationOutput(BaseModel):
    """Output de conversación sobre epigenética"""

    response: str = Field(..., description="Respuesta especializada en epigenética")
    epigenetic_mechanisms: List[str] = Field(
        ..., description="Mecanismos epigenéticos relevantes"
    )
    lifestyle_interventions: Dict[str, List[str]] = Field(
        ..., description="Intervenciones de estilo de vida recomendadas"
    )
    gene_expression_insights: List[str] = Field(
        ..., description="Insights sobre expresión génica"
    )
    timeline_expectations: str = Field(
        ..., description="Expectativas de cronología para cambios"
    )


class SportGeneticsConversationInput(BaseModel):
    """Input para conversación sobre genética deportiva"""

    message: str = Field(
        ..., description="Mensaje del usuario sobre genética deportiva"
    )
    user_id: str = Field(..., description="ID del usuario")
    athletic_background: Optional[Dict[str, Any]] = Field(
        None, description="Antecedentes atléticos del usuario"
    )
    performance_goals: Optional[List[str]] = Field(
        None, description="Objetivos de rendimiento deportivo"
    )
    sport_type: Optional[str] = Field(
        None, description="Tipo de deporte o actividad física"
    )


class SportGeneticsConversationOutput(BaseModel):
    """Output de conversación sobre genética deportiva"""

    response: str = Field(
        ..., description="Respuesta especializada en genética deportiva"
    )
    athletic_potential: Dict[str, Any] = Field(
        ..., description="Análisis del potencial atlético genético"
    )
    training_recommendations: List[str] = Field(
        ..., description="Recomendaciones de entrenamiento específicas"
    )
    genetic_advantages: List[str] = Field(
        ..., description="Ventajas genéticas identificadas"
    )
    injury_prevention_focus: List[str] = Field(
        ..., description="Áreas de enfoque para prevención de lesiones"
    )


class PersonalizedOptimizationConversationInput(BaseModel):
    """Input para conversación sobre optimización personalizada"""

    message: str = Field(..., description="Mensaje del usuario sobre optimización")
    user_id: str = Field(..., description="ID del usuario")
    optimization_domain: Optional[str] = Field(
        None, description="Dominio: performance, health, longevity, cognitive"
    )
    current_status: Optional[Dict[str, Any]] = Field(
        None, description="Estado actual en el dominio de optimización"
    )
    genetic_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil genético disponible"
    )


class PersonalizedOptimizationConversationOutput(BaseModel):
    """Output de conversación sobre optimización personalizada"""

    response: str = Field(..., description="Respuesta de optimización personalizada")
    optimization_strategy: Dict[str, Any] = Field(
        ..., description="Estrategia de optimización específica"
    )
    genetic_basis: List[str] = Field(
        ..., description="Base genética de las recomendaciones"
    )
    implementation_roadmap: Dict[str, str] = Field(
        ..., description="Hoja de ruta de implementación"
    )
    success_metrics: List[str] = Field(
        ..., description="Métricas de éxito para seguimiento"
    )
