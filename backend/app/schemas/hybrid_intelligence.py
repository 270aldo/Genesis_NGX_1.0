"""
Schemas para Hybrid Intelligence API endpoints.

Define los modelos Pydantic para request/response de todos los endpoints
del sistema de Hybrid Intelligence.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# Import core models
from core.hybrid_intelligence.models import (
    UserArchetype,
    PersonalizationMode,
    FitnessLevel,
    WorkoutIntensity,
    UserBiometrics,
    WorkoutData,
    BiomarkerData,
    UserConstraints
)


class PersonalizationModeEnum(str, Enum):
    """Enum para modos de personalización en API"""
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ArchetypeEnum(str, Enum):
    """Enum para arquetipos en API"""
    PRIME = "prime"
    LONGEVITY = "longevity"


# Request Models

class BiometricsRequest(BaseModel):
    """Modelo para datos biométricos en requests"""
    sleep_quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="Calidad del sueño (0-1)")
    sleep_duration: Optional[float] = Field(None, ge=0.0, le=24.0, description="Duración del sueño en horas")
    stress_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nivel de estrés (0-1)")
    energy_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nivel de energía (0-1)")
    heart_rate_resting: Optional[int] = Field(None, ge=30, le=200, description="Frecuencia cardíaca en reposo")
    heart_rate_variability: Optional[float] = Field(None, ge=0.0, description="Variabilidad de frecuencia cardíaca")
    recovery_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Puntuación de recuperación (0-1)")
    hydration_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nivel de hidratación (0-1)")
    body_temperature: Optional[float] = Field(None, ge=35.0, le=42.0, description="Temperatura corporal en Celsius")


class WorkoutRequest(BaseModel):
    """Modelo para datos de entrenamiento en requests"""
    workout_id: str = Field(..., description="ID único del entrenamiento")
    date: datetime = Field(..., description="Fecha del entrenamiento")
    type: str = Field(..., description="Tipo de entrenamiento")
    duration_minutes: int = Field(..., ge=1, description="Duración en minutos")
    intensity: WorkoutIntensity = Field(..., description="Intensidad del entrenamiento")
    calories_burned: Optional[int] = Field(None, ge=0, description="Calorías quemadas")
    exercises: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de ejercicios")
    notes: Optional[str] = Field(None, description="Notas adicionales")


class BiomarkerRequest(BaseModel):
    """Modelo para datos de biomarcadores en requests"""
    marker_name: str = Field(..., description="Nombre del biomarcador")
    value: float = Field(..., description="Valor medido")
    unit: str = Field(..., description="Unidad de medida")
    reference_range: Optional[Dict[str, float]] = Field(None, description="Rango de referencia normal")
    date_measured: datetime = Field(..., description="Fecha de medición")
    lab_source: Optional[str] = Field(None, description="Fuente del laboratorio")


class ConstraintsRequest(BaseModel):
    """Modelo para restricciones del usuario en requests"""
    time_constraints: Dict[str, Any] = Field(default_factory=dict, description="Restricciones de tiempo")
    equipment_access: List[str] = Field(default_factory=list, description="Equipamiento disponible")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Restricciones dietéticas")
    physical_limitations: List[str] = Field(default_factory=list, description="Limitaciones físicas")
    location_constraints: Dict[str, Any] = Field(default_factory=dict, description="Restricciones de ubicación")
    budget_constraints: Optional[Dict[str, float]] = Field(None, description="Restricciones presupuestarias")


class UserDataRequest(BaseModel):
    """Modelo para datos completos del usuario en requests"""
    archetype: ArchetypeEnum = Field(..., description="Arquetipo del usuario")
    age: int = Field(..., ge=13, le=120, description="Edad del usuario")
    gender: str = Field(..., description="Género del usuario")
    weight_kg: Optional[float] = Field(None, ge=20.0, le=300.0, description="Peso en kg")
    height_cm: Optional[float] = Field(None, ge=100.0, le=250.0, description="Altura en cm")
    fitness_level: FitnessLevel = Field(default=FitnessLevel.INTERMEDIATE, description="Nivel de fitness")
    primary_goals: List[str] = Field(default_factory=list, description="Objetivos principales")
    injury_history: List[str] = Field(default_factory=list, description="Historial de lesiones")
    current_medications: List[str] = Field(default_factory=list, description="Medicamentos actuales")
    biometrics: Optional[BiometricsRequest] = Field(None, description="Datos biométricos")
    biomarkers: List[BiomarkerRequest] = Field(default_factory=list, description="Datos de biomarcadores")
    recent_workouts: List[WorkoutRequest] = Field(default_factory=list, description="Entrenamientos recientes")
    constraints: ConstraintsRequest = Field(default_factory=ConstraintsRequest, description="Restricciones del usuario")
    preference_scores: Dict[str, float] = Field(default_factory=dict, description="Puntuaciones de preferencias")
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list, description="Historial de interacciones")


class PersonalizeRequest(BaseModel):
    """Request para endpoint de personalización principal"""
    user_data: UserDataRequest = Field(..., description="Datos completos del usuario")
    agent_type: str = Field(..., description="Tipo de agente (ej: elite_training_strategist)")
    request_type: str = Field(..., description="Tipo de solicitud (ej: training_plan)")
    request_content: str = Field(..., description="Contenido específico de la solicitud")
    personalization_mode: PersonalizationModeEnum = Field(
        default=PersonalizationModeEnum.ADVANCED, 
        description="Modo de personalización"
    )
    session_context: Optional[Dict[str, Any]] = Field(None, description="Contexto de la sesión")

    @validator('agent_type')
    def validate_agent_type(cls, v):
        """Valida que el tipo de agente sea válido"""
        valid_agents = [
            'elite_training_strategist', 'nutrition_specialist', 'recovery_specialist',
            'womens_health_specialist', 'mindset_specialist', 'analytics_specialist',
            'optimization_expert', 'genetics_specialist', 'orchestrator'
        ]
        if v not in valid_agents:
            raise ValueError(f'Tipo de agente debe ser uno de: {valid_agents}')
        return v


class FeedbackRequest(BaseModel):
    """Request para feedback de personalización"""
    session_id: str = Field(..., description="ID de la sesión de personalización")
    satisfaction: float = Field(..., ge=0.0, le=1.0, description="Nivel de satisfacción (0-1)")
    outcome_success: float = Field(..., ge=0.0, le=1.0, description="Éxito del resultado (0-1)")
    found_helpful: bool = Field(..., description="Si encontró útil la personalización")
    intensity_appropriate: Optional[bool] = Field(None, description="Si la intensidad fue apropiada")
    communication_effective: Optional[bool] = Field(None, description="Si la comunicación fue efectiva")
    recommendations_relevant: Optional[bool] = Field(None, description="Si las recomendaciones fueron relevantes")
    comments: Optional[str] = Field(None, description="Comentarios adicionales")


class UserProfileRequest(BaseModel):
    """Request para actualización de perfil de usuario"""
    archetype: Optional[ArchetypeEnum] = Field(None, description="Arquetipo del usuario")
    age: Optional[int] = Field(None, ge=13, le=120, description="Edad del usuario")
    gender: Optional[str] = Field(None, description="Género del usuario")
    weight_kg: Optional[float] = Field(None, ge=20.0, le=300.0, description="Peso en kg")
    height_cm: Optional[float] = Field(None, ge=100.0, le=250.0, description="Altura en cm")
    fitness_level: Optional[FitnessLevel] = Field(None, description="Nivel de fitness")
    primary_goals: Optional[List[str]] = Field(None, description="Objetivos principales")
    injury_history: Optional[List[str]] = Field(None, description="Historial de lesiones")
    current_medications: Optional[List[str]] = Field(None, description="Medicamentos actuales")
    preference_scores: Optional[Dict[str, float]] = Field(None, description="Puntuaciones de preferencias")


class BiometricsUpdateRequest(BaseModel):
    """Request para actualización de datos biométricos"""
    sleep_quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="Calidad del sueño (0-1)")
    sleep_duration: Optional[float] = Field(None, ge=0.0, le=24.0, description="Duración del sueño en horas")
    stress_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nivel de estrés (0-1)")
    energy_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nivel de energía (0-1)")
    heart_rate_resting: Optional[int] = Field(None, ge=30, le=200, description="Frecuencia cardíaca en reposo")
    heart_rate_variability: Optional[float] = Field(None, ge=0.0, description="Variabilidad de frecuencia cardíaca")
    recovery_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Puntuación de recuperación (0-1)")
    hydration_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nivel de hidratación (0-1)")
    body_temperature: Optional[float] = Field(None, ge=35.0, le=42.0, description="Temperatura corporal en Celsius")


class WorkoutSubmissionRequest(BaseModel):
    """Request para envío de datos de entrenamiento"""
    type: str = Field(..., description="Tipo de entrenamiento")
    duration_minutes: int = Field(..., ge=1, description="Duración en minutos")
    intensity: WorkoutIntensity = Field(..., description="Intensidad del entrenamiento")
    calories_burned: Optional[int] = Field(None, ge=0, description="Calorías quemadas")
    exercises: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de ejercicios")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    date: Optional[datetime] = Field(None, description="Fecha del entrenamiento (default: ahora)")

    @validator('date', pre=True, always=True)
    def set_default_date(cls, v):
        """Establece fecha actual si no se proporciona"""
        return v or datetime.now()


# Response Models

class PersonalizeResponse(BaseModel):
    """Response para endpoint de personalización"""
    success: bool = Field(..., description="Si la personalización fue exitosa")
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado de personalización")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")
    processing_time_ms: int = Field(..., description="Tiempo de procesamiento en milisegundos")
    timestamp: datetime = Field(..., description="Timestamp de la respuesta")


class UserInsightsResponse(BaseModel):
    """Response para insights del usuario"""
    success: bool = Field(..., description="Si la obtención fue exitosa")
    insights: Dict[str, Any] = Field(..., description="Insights del usuario")
    generated_at: datetime = Field(..., description="Timestamp de generación")


class FeedbackResponse(BaseModel):
    """Response para feedback"""
    success: bool = Field(..., description="Si el feedback fue procesado")
    message: str = Field(..., description="Mensaje de confirmación")
    feedback_id: str = Field(..., description="ID del feedback")


class UserProfileResponse(BaseModel):
    """Response para perfil de usuario"""
    success: bool = Field(..., description="Si la operación fue exitosa")
    profile: Dict[str, Any] = Field(..., description="Datos del perfil")


class ArchetypesResponse(BaseModel):
    """Response para información de arquetipos"""
    success: bool = Field(..., description="Si la operación fue exitosa")
    archetypes: Dict[str, Any] = Field(..., description="Información de arquetipos")


class PersonalizationHistoryResponse(BaseModel):
    """Response para historial de personalizaciones"""
    success: bool = Field(..., description="Si la operación fue exitosa")
    history: List[Dict[str, Any]] = Field(..., description="Historial de personalizaciones")
    total_count: int = Field(..., description="Número total de registros")
    limit: int = Field(..., description="Límite de resultados")
    offset: int = Field(..., description="Offset de paginación")


# Error Models

class HybridIntelligenceError(BaseModel):
    """Modelo para errores específicos del sistema"""
    error_code: str = Field(..., description="Código de error")
    error_message: str = Field(..., description="Mensaje de error")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")


class ValidationError(BaseModel):
    """Modelo para errores de validación"""
    field: str = Field(..., description="Campo que falló la validación")
    message: str = Field(..., description="Mensaje de error de validación")
    value: Any = Field(..., description="Valor que falló la validación")


# Utility Models

class HealthCheckResponse(BaseModel):
    """Response para health check"""
    status: str = Field(..., description="Estado del servicio")
    service: str = Field(..., description="Nombre del servicio")
    version: str = Field(..., description="Versión del servicio")
    engine_status: str = Field(..., description="Estado del engine")
    timestamp: datetime = Field(..., description="Timestamp del check")
    test_confidence: Optional[float] = Field(None, description="Confidence del test")
    error: Optional[str] = Field(None, description="Error si no es healthy")


class MetricsResponse(BaseModel):
    """Response para métricas del sistema"""
    total_personalizations: int = Field(..., description="Total de personalizaciones")
    average_confidence: float = Field(..., description="Confidence promedio")
    average_processing_time: float = Field(..., description="Tiempo promedio de procesamiento")
    success_rate: float = Field(..., description="Tasa de éxito")
    active_users: int = Field(..., description="Usuarios activos")
    archetype_distribution: Dict[str, int] = Field(..., description="Distribución de arquetipos")
    timestamp: datetime = Field(..., description="Timestamp de las métricas")


# Export all models
__all__ = [
    # Request models
    "PersonalizeRequest",
    "FeedbackRequest", 
    "UserProfileRequest",
    "BiometricsUpdateRequest",
    "WorkoutSubmissionRequest",
    "UserDataRequest",
    "BiometricsRequest",
    "WorkoutRequest",
    "BiomarkerRequest",
    "ConstraintsRequest",
    
    # Response models
    "PersonalizeResponse",
    "UserInsightsResponse",
    "FeedbackResponse",
    "UserProfileResponse",
    "ArchetypesResponse",
    "PersonalizationHistoryResponse",
    "HealthCheckResponse",
    "MetricsResponse",
    
    # Error models
    "HybridIntelligenceError",
    "ValidationError",
    
    # Enums
    "PersonalizationModeEnum",
    "ArchetypeEnum"
]