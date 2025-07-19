"""
Esquemas para el agente Security Compliance Guardian.

Define los esquemas de entrada y salida para las skills del agente,
incluyendo las nuevas capacidades de visión y multimodales.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field


# Esquemas existentes
class SecurityAssessmentInput(BaseModel):
    query: str = Field(
        ..., description="Consulta del usuario sobre evaluación de seguridad"
    )
    system_info: Optional[Dict[str, Any]] = Field(
        None, description="Información del sistema a evaluar"
    )
    app_type: Optional[str] = Field(
        None, description="Tipo de aplicación (web, móvil, API, etc.)"
    )


class SecurityAssessmentOutput(BaseModel):
    response: str = Field(
        ..., description="Respuesta detallada de la evaluación de seguridad"
    )
    risks: List[Dict[str, Any]] = Field(
        ..., description="Lista de riesgos identificados"
    )
    recommendations: List[str] = Field(..., description="Recomendaciones de seguridad")


class ComplianceCheckInput(BaseModel):
    query: str = Field(
        ..., description="Consulta del usuario sobre cumplimiento normativo"
    )
    regulations: Optional[List[str]] = Field(
        None, description="Normativas específicas a verificar"
    )
    region: Optional[str] = Field(
        None, description="Región geográfica para normativas aplicables"
    )


class ComplianceCheckOutput(BaseModel):
    response: str = Field(
        ..., description="Respuesta detallada de la verificación de cumplimiento"
    )
    compliance_status: Dict[str, Any] = Field(
        ..., description="Estado de cumplimiento por normativa"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones para mejorar el cumplimiento"
    )


class VulnerabilityScanInput(BaseModel):
    query: str = Field(..., description="Consulta del usuario sobre vulnerabilidades")
    system_info: Optional[Dict[str, Any]] = Field(
        None, description="Información del sistema a escanear"
    )
    scan_type: Optional[str] = Field(
        None, description="Tipo de escaneo (general, específico, etc.)"
    )


class VulnerabilityScanOutput(BaseModel):
    response: str = Field(
        ..., description="Respuesta detallada del escaneo de vulnerabilidades"
    )
    vulnerabilities: List[Dict[str, Any]] = Field(
        ..., description="Lista de vulnerabilidades identificadas"
    )
    severity_summary: Dict[str, int] = Field(
        ..., description="Resumen de severidad de vulnerabilidades"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones para mitigar vulnerabilidades"
    )


class DataProtectionInput(BaseModel):
    query: str = Field(
        ..., description="Consulta del usuario sobre protección de datos"
    )
    data_types: Optional[List[str]] = Field(
        None, description="Tipos de datos a proteger"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class DataProtectionOutput(BaseModel):
    response: str = Field(
        ..., description="Respuesta detallada sobre protección de datos"
    )
    protection_measures: List[Dict[str, Any]] = Field(
        ..., description="Medidas de protección recomendadas"
    )
    best_practices: List[str] = Field(
        ..., description="Mejores prácticas de protección de datos"
    )


class GeneralSecurityInput(BaseModel):
    query: str = Field(..., description="Consulta general sobre seguridad")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la consulta"
    )


class GeneralSecurityOutput(BaseModel):
    response: str = Field(
        ..., description="Respuesta detallada a la consulta de seguridad"
    )
    recommendations: Optional[List[str]] = Field(
        None, description="Recomendaciones generales de seguridad"
    )


# Nuevos esquemas para capacidades de visión


class ImageComplianceVerificationInput(BaseModel):
    """Esquema de entrada para verificación de cumplimiento normativo en imágenes."""

    image_data: Union[str, Dict[str, Any]] = Field(
        ..., description="Datos de la imagen (base64, URL o ruta)"
    )
    query: str = Field(
        ..., description="Consulta o contexto del usuario sobre la imagen"
    )
    regulations: Optional[List[str]] = Field(
        None, description="Normativas específicas a verificar"
    )
    region: Optional[str] = Field(
        None, description="Región geográfica para normativas aplicables"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la verificación"
    )


class ImageComplianceVerificationOutput(BaseModel):
    """Esquema de salida para verificación de cumplimiento normativo en imágenes."""

    verification_id: str = Field(..., description="ID único de la verificación")
    compliance_summary: str = Field(
        ..., description="Resumen del análisis de cumplimiento"
    )
    compliance_status: Dict[str, Any] = Field(
        ..., description="Estado de cumplimiento por normativa"
    )
    sensitive_elements: List[Dict[str, Any]] = Field(
        ..., description="Elementos sensibles identificados en la imagen"
    )
    compliance_issues: List[Dict[str, Any]] = Field(
        ..., description="Problemas de cumplimiento identificados"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones para resolver problemas de cumplimiento"
    )
    response: str = Field(..., description="Respuesta detallada para el usuario")
    confidence_score: float = Field(
        ..., description="Puntuación de confianza del análisis (0-1)"
    )


class SecurityImageAnalysisInput(BaseModel):
    """Esquema de entrada para análisis de seguridad en imágenes."""

    image_data: Union[str, Dict[str, Any]] = Field(
        ..., description="Datos de la imagen (base64, URL o ruta)"
    )
    query: str = Field(
        ..., description="Consulta o contexto del usuario sobre la imagen"
    )
    analysis_type: Optional[str] = Field(
        None, description="Tipo de análisis (general, específico, etc.)"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para el análisis"
    )


class SecurityImageAnalysisOutput(BaseModel):
    """Esquema de salida para análisis de seguridad en imágenes."""

    analysis_id: str = Field(..., description="ID único del análisis")
    analysis_summary: str = Field(..., description="Resumen del análisis de seguridad")
    security_risks: List[Dict[str, Any]] = Field(
        ..., description="Riesgos de seguridad identificados"
    )
    severity_levels: Dict[str, int] = Field(
        ..., description="Niveles de severidad de los riesgos"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones para mitigar riesgos"
    )
    response: str = Field(..., description="Respuesta detallada para el usuario")
    confidence_score: float = Field(
        ..., description="Puntuación de confianza del análisis (0-1)"
    )


class VisualDataLeakageDetectionInput(BaseModel):
    """Esquema de entrada para detección de fugas de datos en imágenes."""

    image_data: Union[str, Dict[str, Any]] = Field(
        ..., description="Datos de la imagen (base64, URL o ruta)"
    )
    query: str = Field(
        ..., description="Consulta o contexto del usuario sobre la imagen"
    )
    data_types: Optional[List[str]] = Field(
        None, description="Tipos de datos a detectar"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto adicional para la detección"
    )


class VisualDataLeakageDetectionOutput(BaseModel):
    """Esquema de salida para detección de fugas de datos en imágenes."""

    detection_id: str = Field(..., description="ID único de la detección")
    detection_summary: str = Field(
        ..., description="Resumen de la detección de fugas de datos"
    )
    sensitive_data_found: List[Dict[str, Any]] = Field(
        ..., description="Datos sensibles encontrados"
    )
    risk_assessment: Dict[str, Any] = Field(..., description="Evaluación de riesgos")
    protection_recommendations: List[str] = Field(
        ..., description="Recomendaciones para proteger datos"
    )
    response: str = Field(..., description="Respuesta detallada para el usuario")
    confidence_score: float = Field(
        ..., description="Puntuación de confianza de la detección (0-1)"
    )


# ===== ESQUEMAS CONVERSACIONALES =====


class SecurityAssessmentConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre evaluación de seguridad."""

    user_text: str = Field(..., description="Texto del usuario")
    security_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones de seguridad mencionadas"
    )
    system_type: Optional[str] = Field(None, description="Tipo de sistema a evaluar")
    risk_tolerance: Optional[str] = Field(
        None, description="Tolerancia al riesgo (low, medium, high)"
    )
    compliance_requirements: Optional[List[str]] = Field(
        None, description="Requisitos de cumplimiento específicos"
    )
    conversation_context: Optional[str] = Field(
        None, description="Contexto de la conversación"
    )


class SecurityAssessmentConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre evaluación de seguridad."""

    conversation_response: str = Field(
        ..., description="Respuesta conversacional autoritativa y tranquilizadora"
    )
    conversation_id: str = Field(..., description="ID único de la conversación")
    security_reassurance: str = Field(
        ..., description="Mensaje de tranquilidad sobre la protección"
    )
    risk_analysis_summary: List[str] = Field(
        ..., description="Resumen del análisis de riesgos en lenguaje comprensible"
    )
    immediate_actions: List[str] = Field(
        ..., description="Acciones inmediatas recomendadas"
    )


class ComplianceReviewConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre revisión de cumplimiento."""

    user_text: str = Field(..., description="Texto del usuario")
    regulation_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones sobre normativas específicas"
    )
    business_sector: Optional[str] = Field(None, description="Sector del negocio")
    geographic_scope: Optional[str] = Field(
        None, description="Alcance geográfico de operaciones"
    )
    current_compliance_level: Optional[str] = Field(
        None, description="Nivel actual de cumplimiento percibido"
    )
    urgency_level: Optional[str] = Field(
        None, description="Nivel de urgencia de la consulta"
    )


class ComplianceReviewConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre revisión de cumplimiento."""

    compliance_guidance: str = Field(
        ..., description="Orientación detallada sobre cumplimiento normativo"
    )
    regulatory_roadmap: List[str] = Field(
        ..., description="Hoja de ruta para el cumplimiento"
    )
    compliance_confidence: str = Field(
        ..., description="Mensaje de confianza sobre el proceso de cumplimiento"
    )
    priority_actions: List[str] = Field(
        ..., description="Acciones prioritarias para el cumplimiento"
    )


class VulnerabilityDiscussionConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre discusión de vulnerabilidades."""

    user_text: str = Field(..., description="Texto del usuario")
    reported_issues: Optional[List[str]] = Field(
        None, description="Problemas reportados por el usuario"
    )
    system_environment: Optional[str] = Field(
        None, description="Entorno del sistema (production, development, etc.)"
    )
    technical_level: Optional[str] = Field(
        None, description="Nivel técnico del usuario (beginner, intermediate, expert)"
    )
    incident_occurred: Optional[bool] = Field(
        None, description="Si ya ocurrió un incidente de seguridad"
    )
    affected_systems: Optional[List[str]] = Field(
        None, description="Sistemas afectados o en riesgo"
    )


class VulnerabilityDiscussionConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre discusión de vulnerabilidades."""

    vulnerability_assessment: str = Field(
        ..., description="Evaluación clara y tranquilizadora de vulnerabilidades"
    )
    mitigation_strategy: str = Field(
        ..., description="Estrategia de mitigación explicada en términos comprensibles"
    )
    security_strengthening: List[str] = Field(
        ..., description="Pasos para fortalecer la seguridad"
    )
    monitoring_recommendations: List[str] = Field(
        ..., description="Recomendaciones de monitoreo continuo"
    )


class ProtectionStrategiesConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre estrategias de protección."""

    user_text: str = Field(..., description="Texto del usuario")
    assets_to_protect: Optional[List[str]] = Field(
        None, description="Activos que necesitan protección"
    )
    threat_landscape: Optional[List[str]] = Field(
        None, description="Panorama de amenazas conocidas"
    )
    budget_constraints: Optional[str] = Field(
        None, description="Limitaciones presupuestarias"
    )
    implementation_timeline: Optional[str] = Field(
        None, description="Línea de tiempo para implementación"
    )
    current_security_measures: Optional[List[str]] = Field(
        None, description="Medidas de seguridad actuales"
    )


class ProtectionStrategiesConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre estrategias de protección."""

    protection_plan: str = Field(
        ..., description="Plan de protección integral y realista"
    )
    layered_security_approach: List[str] = Field(
        ..., description="Enfoque de seguridad en capas"
    )
    implementation_guidance: str = Field(
        ..., description="Guía de implementación paso a paso"
    )
    cost_effective_solutions: List[str] = Field(
        ..., description="Soluciones costo-efectivas priorizadas"
    )


class SecurityEducationConversationInput(BaseModel):
    """Esquema de entrada para conversación sobre educación en seguridad."""

    user_text: str = Field(..., description="Texto del usuario")
    learning_objectives: Optional[List[str]] = Field(
        None, description="Objetivos de aprendizaje específicos"
    )
    audience_type: Optional[str] = Field(
        None, description="Tipo de audiencia (employees, executives, technical_team)"
    )
    current_knowledge_level: Optional[str] = Field(
        None, description="Nivel de conocimiento actual en seguridad"
    )
    training_format_preference: Optional[str] = Field(
        None, description="Preferencia de formato de entrenamiento"
    )
    specific_topics: Optional[List[str]] = Field(
        None, description="Temas específicos de interés"
    )


class SecurityEducationConversationOutput(BaseModel):
    """Esquema de salida para conversación sobre educación en seguridad."""

    educational_response: str = Field(
        ..., description="Respuesta educativa adaptada al nivel del usuario"
    )
    learning_path: List[str] = Field(
        ..., description="Ruta de aprendizaje estructurada"
    )
    practical_exercises: List[str] = Field(
        ..., description="Ejercicios prácticos recomendados"
    )
    security_awareness_tips: List[str] = Field(
        ..., description="Consejos de concientización en seguridad"
    )
    follow_up_resources: List[str] = Field(
        ..., description="Recursos adicionales para profundizar"
    )
