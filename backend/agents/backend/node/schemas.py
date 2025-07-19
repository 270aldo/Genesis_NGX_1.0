"""
Esquemas para el agente NODE - Systems Integration & Ops.

Este módulo define los esquemas de entrada y salida para las skills del agente
NODE utilizando modelos Pydantic. NODE es un especialista técnico con
personalidad ENTP - The Innovator, enfocado en integración de sistemas y
automatización operativa.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime, date


# Esquemas principales para las skills del agente
class IntegrationRequestInput(BaseModel):
    """Esquema de entrada para solicitudes de integración de sistemas."""

    query: str = Field(
        ..., description="Consulta del usuario sobre integración de sistemas"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class IntegrationRequestOutput(BaseModel):
    """Esquema de salida para solicitudes de integración de sistemas."""

    response: str = Field(
        ..., description="Respuesta detallada sobre integración de sistemas"
    )
    systems: List[str] = Field(
        ..., description="Sistemas identificados para integración"
    )
    integration_report: Optional[Dict[str, Any]] = Field(
        None, description="Informe de integración estructurado"
    )


class AutomationRequestInput(BaseModel):
    """Esquema de entrada para solicitudes de automatización."""

    query: str = Field(
        ...,
        description="Consulta del usuario sobre automatización de flujos de trabajo",
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class AutomationRequestOutput(BaseModel):
    """Esquema de salida para solicitudes de automatización."""

    response: str = Field(..., description="Respuesta detallada sobre automatización")
    automation_plan: Optional[Dict[str, Any]] = Field(
        None, description="Plan de automatización estructurado"
    )


class ApiRequestInput(BaseModel):
    """Esquema de entrada para gestión de APIs."""

    query: str = Field(..., description="Consulta del usuario sobre gestión de APIs")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class ApiRequestOutput(BaseModel):
    """Esquema de salida para gestión de APIs."""

    response: str = Field(..., description="Respuesta detallada sobre gestión de APIs")
    apis: List[str] = Field(..., description="APIs identificadas")
    api_guide: Optional[Dict[str, Any]] = Field(
        None, description="Guía de API estructurada"
    )


class InfrastructureRequestInput(BaseModel):
    """Esquema de entrada para optimización de infraestructura."""

    query: str = Field(..., description="Consulta del usuario sobre infraestructura")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class InfrastructureRequestOutput(BaseModel):
    """Esquema de salida para optimización de infraestructura."""

    response: str = Field(..., description="Respuesta detallada sobre infraestructura")
    infrastructure_report: Optional[Dict[str, Any]] = Field(
        None, description="Informe de infraestructura estructurado"
    )


class DataPipelineRequestInput(BaseModel):
    """Esquema de entrada para diseño de pipelines de datos."""

    query: str = Field(..., description="Consulta del usuario sobre pipelines de datos")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class DataPipelineRequestOutput(BaseModel):
    """Esquema de salida para diseño de pipelines de datos."""

    response: str = Field(
        ..., description="Respuesta detallada sobre pipelines de datos"
    )
    pipeline_design: Optional[Dict[str, Any]] = Field(
        None, description="Diseño de pipeline estructurado"
    )


class GeneralRequestInput(BaseModel):
    """Esquema de entrada para consultas generales."""

    query: str = Field(..., description="Consulta general del usuario")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class GeneralRequestOutput(BaseModel):
    """Esquema de salida para consultas generales."""

    response: str = Field(..., description="Respuesta detallada a la consulta general")


# Esquemas para capacidades de visión
class VisualSystemAnalysisInput(BaseModel):
    """Esquema de entrada para análisis visual de sistemas."""

    query: str = Field(
        ..., description="Consulta del usuario sobre análisis visual de sistemas"
    )
    image_data: str = Field(..., description="Datos de la imagen en formato base64")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class VisualSystemAnalysisOutput(BaseModel):
    """Esquema de salida para análisis visual de sistemas."""

    analysis_id: str = Field(..., description="ID único del análisis")
    response: str = Field(
        ..., description="Respuesta detallada del análisis visual de sistemas"
    )
    analysis_summary: str = Field(..., description="Resumen del análisis")
    system_components: List[Dict[str, Any]] = Field(
        ..., description="Componentes del sistema identificados"
    )
    integration_points: List[Dict[str, Any]] = Field(
        ..., description="Puntos de integración identificados"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones basadas en el análisis visual"
    )
    confidence_score: float = Field(
        ..., description="Puntuación de confianza del análisis"
    )


class VisualIntegrationVerificationInput(BaseModel):
    """Esquema de entrada para verificación visual de integración."""

    query: str = Field(
        ..., description="Consulta del usuario sobre verificación visual de integración"
    )
    image_data: str = Field(..., description="Datos de la imagen en formato base64")
    integration_type: Optional[str] = Field(
        None, description="Tipo de integración a verificar"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class VisualIntegrationVerificationOutput(BaseModel):
    """Esquema de salida para verificación visual de integración."""

    verification_id: str = Field(..., description="ID único de la verificación")
    response: str = Field(
        ..., description="Respuesta detallada de la verificación visual de integración"
    )
    verification_summary: str = Field(..., description="Resumen de la verificación")
    integration_status: Dict[str, Any] = Field(
        ..., description="Estado de la integración verificada"
    )
    issues_detected: List[Dict[str, Any]] = Field(
        ..., description="Problemas detectados en la integración"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones para mejorar la integración"
    )
    confidence_score: float = Field(
        ..., description="Puntuación de confianza de la verificación"
    )


class VisualDataFlowAnalysisInput(BaseModel):
    """Esquema de entrada para análisis visual de flujo de datos."""

    query: str = Field(
        ..., description="Consulta del usuario sobre análisis visual de flujo de datos"
    )
    image_data: str = Field(..., description="Datos de la imagen en formato base64")
    flow_type: Optional[str] = Field(
        None, description="Tipo de flujo de datos a analizar"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class VisualDataFlowAnalysisOutput(BaseModel):
    """Esquema de salida para análisis visual de flujo de datos."""

    analysis_id: str = Field(..., description="ID único del análisis")
    response: str = Field(
        ..., description="Respuesta detallada del análisis visual de flujo de datos"
    )
    analysis_summary: str = Field(..., description="Resumen del análisis")
    data_flow_components: List[Dict[str, Any]] = Field(
        ..., description="Componentes del flujo de datos identificados"
    )
    bottlenecks: List[Dict[str, Any]] = Field(
        ..., description="Cuellos de botella identificados"
    )
    optimization_suggestions: List[str] = Field(
        ..., description="Sugerencias de optimización"
    )
    confidence_score: float = Field(
        ..., description="Puntuación de confianza del análisis"
    )


# ===== ESQUEMAS CONVERSACIONALES - NODE PERSONALIDAD ENTP =====


class APIIntegrationConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre integración de APIs."""

    user_text: str = Field(
        ..., description="Texto del usuario sobre integración de APIs"
    )
    target_api: Optional[str] = Field(None, description="API objetivo para integración")
    current_tech_stack: Optional[List[str]] = Field(
        None, description="Stack tecnológico actual"
    )
    integration_complexity: Optional[str] = Field(
        None, description="Complejidad de integración (simple, medium, complex)"
    )
    conversation_context: Optional[str] = Field(
        None, description="Contexto de la conversación técnica"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class APIIntegrationConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre integración de APIs."""

    technical_response: str = Field(
        ..., description="Respuesta técnica eficiente sobre integración de APIs"
    )
    conversation_id: str = Field(..., description="ID único de la conversación")
    integration_steps: List[str] = Field(
        ..., description="Pasos específicos de integración"
    )
    code_examples: Optional[str] = Field(
        None, description="Ejemplos de código cuando sean relevantes"
    )
    optimization_tips: List[str] = Field(
        ..., description="Tips de optimización técnica"
    )
    follow_up_suggestions: List[str] = Field(
        ..., description="Sugerencias de seguimiento técnico"
    )


class AutomationDesignConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre diseño de automatización."""

    user_text: str = Field(..., description="Texto del usuario sobre automatización")
    process_to_automate: Optional[str] = Field(
        None, description="Proceso específico a automatizar"
    )
    current_workflow: Optional[Dict[str, Any]] = Field(
        None, description="Flujo de trabajo actual"
    )
    automation_tools: Optional[List[str]] = Field(
        None, description="Herramientas de automatización disponibles"
    )
    efficiency_goals: Optional[str] = Field(None, description="Objetivos de eficiencia")
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class AutomationDesignConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre diseño de automatización."""

    automation_response: str = Field(
        ..., description="Respuesta sobre diseño de automatización"
    )
    workflow_optimization: str = Field(
        ..., description="Optimización de flujo de trabajo propuesta"
    )
    implementation_strategy: List[str] = Field(
        ..., description="Estrategia de implementación"
    )
    tools_recommendation: List[str] = Field(
        ..., description="Herramientas recomendadas"
    )
    efficiency_metrics: Dict[str, Any] = Field(
        ..., description="Métricas de eficiencia esperadas"
    )


class InfrastructureOptimizationConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre optimización de infraestructura."""

    user_text: str = Field(..., description="Texto del usuario sobre infraestructura")
    current_architecture: Optional[str] = Field(
        None, description="Arquitectura actual del sistema"
    )
    performance_issues: Optional[List[str]] = Field(
        None, description="Problemas de rendimiento identificados"
    )
    scalability_requirements: Optional[str] = Field(
        None, description="Requisitos de escalabilidad"
    )
    budget_constraints: Optional[str] = Field(
        None, description="Restricciones presupuestarias"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class InfrastructureOptimizationConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre optimización de infraestructura."""

    optimization_response: str = Field(
        ..., description="Respuesta sobre optimización de infraestructura"
    )
    architecture_recommendations: List[str] = Field(
        ..., description="Recomendaciones de arquitectura"
    )
    performance_improvements: List[str] = Field(
        ..., description="Mejoras de rendimiento"
    )
    scalability_strategy: str = Field(..., description="Estrategia de escalabilidad")
    cost_optimization: List[str] = Field(..., description="Optimizaciones de costo")


class DataPipelineConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre pipelines de datos."""

    user_text: str = Field(
        ..., description="Texto del usuario sobre pipelines de datos"
    )
    data_sources: Optional[List[str]] = Field(
        None, description="Fuentes de datos disponibles"
    )
    processing_requirements: Optional[str] = Field(
        None, description="Requisitos de procesamiento"
    )
    data_volume: Optional[str] = Field(
        None, description="Volumen de datos (small, medium, large)"
    )
    real_time_needs: Optional[bool] = Field(
        None, description="Necesidades de procesamiento en tiempo real"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class DataPipelineConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre pipelines de datos."""

    pipeline_response: str = Field(
        ..., description="Respuesta sobre diseño de pipeline de datos"
    )
    architecture_design: str = Field(
        ..., description="Diseño de arquitectura del pipeline"
    )
    technology_stack: List[str] = Field(
        ..., description="Stack tecnológico recomendado"
    )
    processing_strategy: str = Field(..., description="Estrategia de procesamiento")
    monitoring_approach: List[str] = Field(
        ..., description="Enfoque de monitoreo y alertas"
    )


class TechnicalTroubleshootingConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre troubleshooting técnico."""

    user_text: str = Field(..., description="Texto del usuario sobre problema técnico")
    error_description: Optional[str] = Field(
        None, description="Descripción del error o problema"
    )
    system_context: Optional[str] = Field(
        None, description="Contexto del sistema afectado"
    )
    error_logs: Optional[str] = Field(None, description="Logs de error relevantes")
    attempted_solutions: Optional[List[str]] = Field(
        None, description="Soluciones ya intentadas"
    )
    urgency_level: Optional[str] = Field(
        None, description="Nivel de urgencia (low, medium, high, critical)"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class TechnicalTroubleshootingConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre troubleshooting técnico."""

    troubleshooting_response: str = Field(
        ..., description="Respuesta de troubleshooting técnico"
    )
    problem_analysis: str = Field(..., description="Análisis del problema identificado")
    solution_steps: List[str] = Field(
        ..., description="Pasos de solución ordenados por prioridad"
    )
    preventive_measures: List[str] = Field(
        ..., description="Medidas preventivas para evitar recurrencia"
    )
    escalation_path: Optional[str] = Field(
        None, description="Ruta de escalación si es necesaria"
    )
    monitoring_recommendations: List[str] = Field(
        ..., description="Recomendaciones de monitoreo post-solución"
    )
