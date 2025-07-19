"""
Esquemas para el agente WAVE Performance Analytics.

Combines schemas from Recovery Corrective (WAVE) and Biometrics Insight Engine (VOLT)
plus new hybrid schemas for the consolidated agent.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


# ===============================
# RECOVERY SKILLS SCHEMAS (From WAVE)
# ===============================


class InjuryPreventionInput(BaseModel):
    """Esquema de entrada para prevención de lesiones."""

    query: str = Field(
        ..., description="Consulta del usuario sobre prevención de lesiones"
    )
    activity_type: Optional[str] = Field(None, description="Tipo de actividad física")
    injury_history: Optional[List[str]] = Field(
        None, description="Historial de lesiones previas"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class InjuryPreventionOutput(BaseModel):
    """Esquema de salida para prevención de lesiones."""

    response: str = Field(
        ..., description="Respuesta detallada sobre prevención de lesiones"
    )
    prevention_plan: Dict[str, Any] = Field(
        ..., description="Plan de prevención estructurado"
    )
    exercises: Optional[List[Dict[str, Any]]] = Field(
        None, description="Ejercicios recomendados"
    )


class RehabilitationInput(BaseModel):
    """Esquema de entrada para rehabilitación."""

    query: str = Field(..., description="Consulta del usuario sobre rehabilitación")
    injury_type: Optional[str] = Field(None, description="Tipo de lesión")
    injury_phase: Optional[str] = Field(
        None, description="Fase de la lesión (aguda, subaguda, crónica)"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class RehabilitationOutput(BaseModel):
    """Esquema de salida para rehabilitación."""

    response: str = Field(..., description="Respuesta detallada sobre rehabilitación")
    rehab_protocol: Dict[str, Any] = Field(
        ..., description="Protocolo de rehabilitación estructurado"
    )
    exercises: Optional[List[Dict[str, Any]]] = Field(
        None, description="Ejercicios recomendados"
    )


class MobilityAssessmentInput(BaseModel):
    """Esquema de entrada para evaluación de movilidad."""

    query: str = Field(..., description="Consulta del usuario sobre movilidad")
    target_areas: Optional[List[str]] = Field(
        None, description="Áreas objetivo para mejorar movilidad"
    )
    movement_goals: Optional[List[str]] = Field(
        None, description="Objetivos de movimiento"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class MobilityAssessmentOutput(BaseModel):
    """Esquema de salida para evaluación de movilidad."""

    response: str = Field(..., description="Respuesta detallada sobre movilidad")
    mobility_assessment: Dict[str, Any] = Field(
        ..., description="Evaluación de movilidad estructurada"
    )
    exercises: Optional[List[Dict[str, Any]]] = Field(
        None, description="Ejercicios recomendados"
    )


class SleepOptimizationInput(BaseModel):
    """Esquema de entrada para optimización del sueño."""

    query: str = Field(
        ..., description="Consulta del usuario sobre optimización del sueño"
    )
    sleep_issues: Optional[List[str]] = Field(
        None, description="Problemas de sueño reportados"
    )
    sleep_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos de sueño del usuario"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class SleepOptimizationOutput(BaseModel):
    """Esquema de salida para optimización del sueño."""

    response: str = Field(
        ..., description="Respuesta detallada sobre optimización del sueño"
    )
    sleep_plan: Dict[str, Any] = Field(
        ..., description="Plan de optimización del sueño estructurado"
    )
    recommendations: Optional[List[str]] = Field(
        None, description="Recomendaciones específicas"
    )


class HRVProtocolInput(BaseModel):
    """Esquema de entrada para protocolos HRV."""

    query: str = Field(..., description="Consulta del usuario sobre protocolos HRV")
    hrv_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos de HRV del usuario"
    )
    training_context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto de entrenamiento"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class HRVProtocolOutput(BaseModel):
    """Esquema de salida para protocolos HRV."""

    response: str = Field(..., description="Respuesta detallada sobre protocolos HRV")
    hrv_protocol: Dict[str, Any] = Field(..., description="Protocolo HRV estructurado")
    recommendations: Optional[List[str]] = Field(
        None, description="Recomendaciones específicas"
    )


class ChronicPainInput(BaseModel):
    """Esquema de entrada para dolor crónico."""

    query: str = Field(..., description="Consulta del usuario sobre dolor crónico")
    pain_location: Optional[str] = Field(None, description="Ubicación del dolor")
    pain_intensity: Optional[int] = Field(
        None, description="Intensidad del dolor (1-10)"
    )
    pain_duration: Optional[str] = Field(None, description="Duración del dolor")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class ChronicPainOutput(BaseModel):
    """Esquema de salida para dolor crónico."""

    response: str = Field(
        ..., description="Respuesta detallada sobre manejo del dolor crónico"
    )
    pain_assessment: Dict[str, Any] = Field(
        ..., description="Evaluación del dolor estructurada"
    )
    management_plan: Dict[str, Any] = Field(
        ..., description="Plan de manejo del dolor estructurado"
    )
    recommendations: Optional[List[str]] = Field(
        None, description="Recomendaciones específicas"
    )


class GeneralRecoveryInput(BaseModel):
    """Esquema de entrada para recuperación general."""

    query: str = Field(
        ..., description="Consulta general del usuario sobre recuperación"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class GeneralRecoveryOutput(BaseModel):
    """Esquema de salida para recuperación general."""

    response: str = Field(..., description="Respuesta detallada a la consulta general")
    recovery_protocol: Optional[Dict[str, Any]] = Field(
        None, description="Protocolo de recuperación si es aplicable"
    )


# ===============================
# ANALYTICS SKILLS SCHEMAS (From VOLT)
# ===============================


class BiometricAnalysisInput(BaseModel):
    """Esquema de entrada para análisis biométrico."""

    biometric_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos biométricos del usuario a analizar"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )


class BiometricAnalysisOutput(BaseModel):
    """Esquema de salida para análisis biométrico."""

    analysis: str = Field(..., description="Análisis completo de los datos biométricos")
    artifacts: List["BiometricAnalysisArtifact"] = Field(
        ..., description="Artefactos generados durante el análisis"
    )
    metadata: Dict[str, Any] = Field(..., description="Metadatos del análisis")


class PatternRecognitionInput(BaseModel):
    """Esquema de entrada para reconocimiento de patrones."""

    user_input: str = Field(..., description="Texto de entrada del usuario")
    biometric_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos biométricos del usuario a analizar"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )


class PatternRecognitionOutput(BaseModel):
    """Esquema de salida para reconocimiento de patrones."""

    identified_patterns: List[Dict[str, Any]] = Field(
        ..., description="Patrones identificados en los datos biométricos"
    )
    correlations: List[Dict[str, Any]] = Field(
        ..., description="Correlaciones entre diferentes métricas"
    )
    causality_analysis: Optional[Dict[str, Any]] = Field(
        None, description="Análisis de posibles relaciones causales"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones basadas en los patrones identificados"
    )


class TrendIdentificationInput(BaseModel):
    """Esquema de entrada para identificación de tendencias."""

    user_input: str = Field(..., description="Texto de entrada del usuario")
    biometric_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos biométricos del usuario a analizar"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )


class TrendIdentificationOutput(BaseModel):
    """Esquema de salida para identificación de tendencias."""

    trends: List[str] = Field(
        ..., description="Tendencias identificadas en los datos biométricos"
    )
    significant_changes: List[str] = Field(
        ..., description="Cambios significativos detectados"
    )
    progress: str = Field(..., description="Evaluación del progreso en el tiempo")
    projections: List[str] = Field(
        ..., description="Proyecciones futuras basadas en tendencias actuales"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones basadas en las tendencias identificadas"
    )


class DataVisualizationInput(BaseModel):
    """Esquema de entrada para visualización de datos."""

    user_input: str = Field(..., description="Texto de entrada del usuario")
    biometric_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos biométricos del usuario a visualizar"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )
    visualization_type: Optional[str] = Field(
        "line", description="Tipo de visualización (line, bar, scatter, etc.)"
    )
    metrics: Optional[List[str]] = Field(
        None, description="Métricas específicas a visualizar"
    )


class DataVisualizationOutput(BaseModel):
    """Esquema de salida para visualización de datos."""

    chart_type: str = Field(..., description="Tipo de gráfico generado")
    metrics: List[str] = Field(
        ..., description="Métricas incluidas en la visualización"
    )
    axes: Dict[str, str] = Field(..., description="Configuración de ejes")
    highlighted_patterns: List[str] = Field(
        ..., description="Patrones destacados en la visualización"
    )
    interpretation: str = Field(..., description="Interpretación de la visualización")
    artifact: "BiometricVisualizationArtifact" = Field(
        ..., description="Artefacto de visualización generado"
    )


class BiometricImageAnalysisInput(BaseModel):
    """Esquema de entrada para análisis de imágenes biométricas."""

    image_data: Union[str, Dict[str, Any]] = Field(
        ..., description="Datos de la imagen (base64, URL o ruta de archivo)"
    )
    analysis_type: Optional[str] = Field(
        "full",
        description="Tipo de análisis a realizar (full, body, face, posture, etc.)",
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )


class BiometricImageAnalysisOutput(BaseModel):
    """Esquema de salida para análisis de imágenes biométricas."""

    analysis_summary: str = Field(
        ..., description="Resumen del análisis de la imagen biométrica"
    )
    detected_metrics: Dict[str, Any] = Field(
        ..., description="Métricas biométricas detectadas en la imagen"
    )
    visual_indicators: List[Dict[str, Any]] = Field(
        ..., description="Indicadores visuales identificados"
    )
    health_insights: List[str] = Field(
        ..., description="Insights de salud basados en el análisis visual"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones basadas en el análisis visual"
    )
    confidence_score: float = Field(
        ..., description="Puntuación de confianza del análisis (0.0-1.0)"
    )


# ===============================
# HYBRID SKILLS SCHEMAS (New)
# ===============================


class RecoveryAnalyticsFusionInput(BaseModel):
    """Esquema de entrada para fusión de recuperación y análisis."""

    query: str = Field(
        ..., description="Consulta del usuario sobre recuperación optimizada por datos"
    )
    recovery_goals: Optional[List[str]] = Field(
        None, description="Objetivos de recuperación"
    )
    biometric_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos biométricos para informar recuperación"
    )
    injury_history: Optional[List[str]] = Field(
        None, description="Historial de lesiones"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class RecoveryAnalyticsFusionOutput(BaseModel):
    """Esquema de salida para fusión de recuperación y análisis."""

    response: str = Field(
        ..., description="Respuesta integrada combinando recuperación y análisis"
    )
    data_driven_recovery_plan: Dict[str, Any] = Field(
        ..., description="Plan de recuperación basado en datos"
    )
    biometric_insights: Dict[str, Any] = Field(
        ..., description="Insights biométricos que informan la recuperación"
    )
    adaptive_recommendations: List[str] = Field(
        ..., description="Recomendaciones que se adaptan a los datos"
    )
    monitoring_protocol: Dict[str, Any] = Field(
        ..., description="Protocolo de monitoreo para ajustes futuros"
    )


class PerformanceRecoveryOptimizationInput(BaseModel):
    """Esquema de entrada para optimización de recuperación basada en rendimiento."""

    query: str = Field(
        ..., description="Consulta sobre optimización de rendimiento y recuperación"
    )
    performance_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos de rendimiento del usuario"
    )
    recovery_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos de recuperación del usuario"
    )
    training_schedule: Optional[Dict[str, Any]] = Field(
        None, description="Horario de entrenamiento"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class PerformanceRecoveryOptimizationOutput(BaseModel):
    """Esquema de salida para optimización de recuperación basada en rendimiento."""

    response: str = Field(
        ..., description="Respuesta sobre optimización de recuperación para rendimiento"
    )
    optimized_recovery_protocol: Dict[str, Any] = Field(
        ..., description="Protocolo de recuperación optimizado"
    )
    performance_predictions: List[str] = Field(
        ..., description="Predicciones de rendimiento basadas en recuperación"
    )
    training_adjustments: List[str] = Field(
        ..., description="Ajustes sugeridos al entrenamiento"
    )
    recovery_metrics_tracking: Dict[str, Any] = Field(
        ..., description="Métricas clave para seguimiento"
    )


class InjuryPredictionAnalyticsInput(BaseModel):
    """Esquema de entrada para predicción de lesiones usando análisis."""

    query: str = Field(..., description="Consulta sobre predicción de lesiones")
    movement_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos de movimiento y biomecánica"
    )
    biometric_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos biométricos del usuario"
    )
    training_load: Optional[Dict[str, Any]] = Field(
        None, description="Carga de entrenamiento"
    )
    injury_history: Optional[List[str]] = Field(
        None, description="Historial de lesiones"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class InjuryPredictionAnalyticsOutput(BaseModel):
    """Esquema de salida para predicción de lesiones usando análisis."""

    response: str = Field(..., description="Respuesta sobre predicción de lesiones")
    injury_risk_assessment: Dict[str, Any] = Field(
        ..., description="Evaluación del riesgo de lesión"
    )
    risk_factors_identified: List[Dict[str, Any]] = Field(
        ..., description="Factores de riesgo identificados"
    )
    preventive_interventions: List[Dict[str, Any]] = Field(
        ..., description="Intervenciones preventivas recomendadas"
    )
    monitoring_plan: Dict[str, Any] = Field(
        ..., description="Plan de monitoreo para prevención"
    )
    confidence_score: float = Field(
        ..., description="Confianza en las predicciones (0.0-1.0)"
    )


class HolisticWellnessDashboardInput(BaseModel):
    """Esquema de entrada para dashboard holístico de bienestar."""

    query: str = Field(..., description="Consulta sobre vista holística de bienestar")
    data_sources: Optional[List[str]] = Field(
        None, description="Fuentes de datos a incluir"
    )
    time_range: Optional[str] = Field(None, description="Rango de tiempo para análisis")
    focus_areas: Optional[List[str]] = Field(
        None, description="Áreas de enfoque específicas"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class HolisticWellnessDashboardOutput(BaseModel):
    """Esquema de salida para dashboard holístico de bienestar."""

    response: str = Field(..., description="Respuesta sobre dashboard holístico")
    wellness_overview: Dict[str, Any] = Field(
        ..., description="Vista general del bienestar"
    )
    recovery_status: Dict[str, Any] = Field(
        ..., description="Estado actual de recuperación"
    )
    performance_metrics: Dict[str, Any] = Field(
        ..., description="Métricas de rendimiento"
    )
    health_insights: List[str] = Field(..., description="Insights de salud integrados")
    actionable_recommendations: List[str] = Field(
        ..., description="Recomendaciones accionables"
    )
    dashboard_artifact: "WellnessDashboardArtifact" = Field(
        ..., description="Artefacto de dashboard generado"
    )


class AdaptiveRecoveryProtocolInput(BaseModel):
    """Esquema de entrada para protocolo de recuperación adaptativo."""

    query: str = Field(..., description="Consulta sobre protocolo adaptativo")
    current_protocol: Optional[Dict[str, Any]] = Field(
        None, description="Protocolo actual de recuperación"
    )
    recent_biometric_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos biométricos recientes"
    )
    performance_feedback: Optional[Dict[str, Any]] = Field(
        None, description="Retroalimentación de rendimiento"
    )
    environmental_factors: Optional[Dict[str, Any]] = Field(
        None, description="Factores ambientales"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )


class AdaptiveRecoveryProtocolOutput(BaseModel):
    """Esquema de salida para protocolo de recuperación adaptativo."""

    response: str = Field(..., description="Respuesta sobre protocolo adaptativo")
    adapted_protocol: Dict[str, Any] = Field(
        ..., description="Protocolo de recuperación adaptado"
    )
    adaptation_rationale: str = Field(
        ..., description="Justificación de las adaptaciones"
    )
    sensitivity_analysis: Dict[str, Any] = Field(
        ..., description="Análisis de sensibilidad a cambios"
    )
    future_adjustments: List[str] = Field(
        ..., description="Ajustes futuros recomendados"
    )
    effectiveness_metrics: Dict[str, Any] = Field(
        ..., description="Métricas para evaluar efectividad"
    )


# ===============================
# CONVERSATIONAL SKILLS SCHEMAS
# ===============================


class RecoveryAnalyticsConversationInput(BaseModel):
    """Esquema de entrada para conversaciones de recuperación y análisis."""

    message: str = Field(..., description="Mensaje del usuario")
    conversation_context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto de la conversación"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario"
    )
    session_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos de la sesión"
    )


class RecoveryAnalyticsConversationOutput(BaseModel):
    """Esquema de salida para conversaciones de recuperación y análisis."""

    response: str = Field(..., description="Respuesta conversacional")
    conversation_type: str = Field(
        ..., description="Tipo de conversación (recovery, analytics, hybrid)"
    )
    insights_shared: List[str] = Field(
        ..., description="Insights compartidos durante la conversación"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones conversacionales"
    )
    follow_up_questions: Optional[List[str]] = Field(
        None, description="Preguntas de seguimiento sugeridas"
    )


# ===============================
# ARTIFACTS
# ===============================


class BiometricAnalysisArtifact(BaseModel):
    """Artefacto para análisis biométrico."""

    id: str = Field(..., description="ID único del análisis")
    label: str = Field(..., description="Etiqueta descriptiva del análisis")
    content: str = Field(..., description="Contenido del análisis")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del análisis")


class BiometricVisualizationArtifact(BaseModel):
    """Artefacto para visualización de datos biométricos."""

    visualization_id: str = Field(..., description="ID único de la visualización")
    visualization_type: str = Field(..., description="Tipo de visualización")
    metrics_included: List[str] = Field(..., description="Métricas incluidas")
    timestamp: float = Field(..., description="Timestamp de la visualización")
    url: str = Field(..., description="URL o ruta a la visualización")


class WellnessDashboardArtifact(BaseModel):
    """Artefacto para dashboard de bienestar holístico."""

    dashboard_id: str = Field(..., description="ID único del dashboard")
    components: List[str] = Field(
        ..., description="Componentes incluidos en el dashboard"
    )
    data_sources: List[str] = Field(..., description="Fuentes de datos utilizadas")
    timestamp: float = Field(..., description="Timestamp de generación")
    interactive_elements: Dict[str, Any] = Field(
        ..., description="Elementos interactivos del dashboard"
    )
    url: str = Field(..., description="URL del dashboard")


# Fix forward references
BiometricAnalysisOutput.model_rebuild()
DataVisualizationOutput.model_rebuild()
HolisticWellnessDashboardOutput.model_rebuild()
