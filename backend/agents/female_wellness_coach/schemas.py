"""
Esquemas para el agente Female Wellness Coach.

Este módulo define los esquemas de entrada y salida para las skills del agente
Female Wellness Coach utilizando modelos Pydantic.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime, date


# Modelos para la skill de análisis del ciclo menstrual
class AnalyzeMenstrualCycleInput(BaseModel):
    """Esquema de entrada para análisis del ciclo menstrual."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información menstrual"
    )
    cycle_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos del ciclo menstrual actual"
    )
    symptoms: Optional[List[str]] = Field(
        None, description="Síntomas reportados por la usuaria"
    )


class CycleInsight(BaseModel):
    """Modelo para insights del ciclo menstrual."""

    current_phase: str = Field(..., description="Fase actual del ciclo")
    predicted_next_period: str = Field(
        ..., description="Predicción del próximo período"
    )
    optimal_workout_window: str = Field(
        ..., description="Ventana óptima para entrenamientos intensos"
    )
    hormonal_insights: str = Field(
        ..., description="Insights sobre fluctuaciones hormonales"
    )


class AnalyzeMenstrualCycleOutput(BaseModel):
    """Esquema de salida para análisis del ciclo menstrual."""

    cycle_insights: CycleInsight = Field(
        ..., description="Insights del ciclo menstrual"
    )
    recommendations: List[str] = Field(..., description="Recomendaciones específicas")
    tracking_suggestions: List[str] = Field(
        ..., description="Sugerencias de seguimiento"
    )
    warning_signs: Optional[List[str]] = Field(None, description="Señales de alerta")


# Modelos para la skill de entrenamiento adaptado al ciclo
class CreateCycleBasedWorkoutInput(BaseModel):
    """Esquema de entrada para entrenamiento basado en ciclo menstrual."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con historial de entrenamiento"
    )
    current_cycle_phase: Optional[str] = Field(
        None, description="Fase actual del ciclo menstrual"
    )
    energy_level: Optional[str] = Field(
        None, description="Nivel de energía reportado: low, moderate, high"
    )
    available_equipment: Optional[List[str]] = Field(
        None, description="Equipamiento disponible"
    )


class WorkoutModification(BaseModel):
    """Modelo para modificaciones específicas del entrenamiento."""

    exercise: str = Field(..., description="Ejercicio específico")
    modification: str = Field(..., description="Modificación recomendada")
    reason: str = Field(..., description="Razón de la modificación")


class CycleBasedWorkout(BaseModel):
    """Modelo para entrenamiento adaptado al ciclo."""

    phase: str = Field(..., description="Fase del ciclo menstrual")
    workout_type: str = Field(..., description="Tipo de entrenamiento")
    intensity: str = Field(..., description="Intensidad recomendada")
    duration_minutes: int = Field(..., description="Duración en minutos")
    exercises: List[str] = Field(..., description="Lista de ejercicios")
    modifications: List[WorkoutModification] = Field(
        ..., description="Modificaciones específicas"
    )


class CreateCycleBasedWorkoutOutput(BaseModel):
    """Esquema de salida para entrenamiento basado en ciclo."""

    workout_plan: CycleBasedWorkout = Field(..., description="Plan de entrenamiento")
    hormonal_considerations: str = Field(..., description="Consideraciones hormonales")
    recovery_focus: str = Field(..., description="Enfoque de recuperación")
    adaptations: List[str] = Field(..., description="Adaptaciones sugeridas")


# Modelos para la skill de nutrición hormonal
class HormonalNutritionPlanInput(BaseModel):
    """Esquema de entrada para plan nutricional hormonal."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil nutricional del usuario"
    )
    life_stage: Optional[str] = Field(
        None,
        description="Etapa de vida: reproductive, perimenopause, menopause, postmenopause",
    )
    hormonal_symptoms: Optional[List[str]] = Field(
        None, description="Síntomas hormonales reportados"
    )
    dietary_preferences: Optional[List[str]] = Field(
        None, description="Preferencias dietéticas"
    )


class NutritionalRecommendation(BaseModel):
    """Modelo para recomendación nutricional específica."""

    nutrient: str = Field(..., description="Nutriente específico")
    recommended_amount: str = Field(..., description="Cantidad recomendada")
    food_sources: List[str] = Field(..., description="Fuentes alimentarias")
    timing: str = Field(..., description="Momento óptimo de consumo")
    benefits: str = Field(..., description="Beneficios para la salud hormonal")


class HormonalNutritionPlanOutput(BaseModel):
    """Esquema de salida para plan nutricional hormonal."""

    nutritional_recommendations: List[NutritionalRecommendation] = Field(
        ..., description="Recomendaciones nutricionales específicas"
    )
    meal_timing_strategy: str = Field(
        ..., description="Estrategia de timing de comidas"
    )
    supplements_consideration: List[str] = Field(
        ..., description="Consideraciones de suplementación"
    )
    foods_to_limit: List[str] = Field(..., description="Alimentos a limitar")
    hydration_guidance: str = Field(..., description="Guía de hidratación")


# Modelos para la skill de manejo de perimenopausia/menopausia
class ManageMenopauseInput(BaseModel):
    """Esquema de entrada para manejo de perimenopausia/menopausia."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con historial médico"
    )
    current_symptoms: Optional[List[str]] = Field(
        None, description="Síntomas actuales de perimenopausia/menopausia"
    )
    severity_level: Optional[str] = Field(
        None, description="Nivel de severidad: mild, moderate, severe"
    )
    current_treatments: Optional[List[str]] = Field(
        None, description="Tratamientos actuales"
    )


class SymptomManagementStrategy(BaseModel):
    """Modelo para estrategia de manejo de síntomas."""

    symptom: str = Field(..., description="Síntoma específico")
    lifestyle_interventions: List[str] = Field(
        ..., description="Intervenciones de estilo de vida"
    )
    nutritional_approach: str = Field(..., description="Enfoque nutricional")
    exercise_recommendations: str = Field(
        ..., description="Recomendaciones de ejercicio"
    )
    when_to_seek_help: str = Field(..., description="Cuándo buscar ayuda médica")


class ManageMenopauseOutput(BaseModel):
    """Esquema de salida para manejo de perimenopausia/menopausia."""

    symptom_management: List[SymptomManagementStrategy] = Field(
        ..., description="Estrategias de manejo de síntomas"
    )
    lifestyle_modifications: List[str] = Field(
        ..., description="Modificaciones de estilo de vida"
    )
    bone_health_focus: str = Field(..., description="Enfoque en salud ósea")
    cardiovascular_considerations: str = Field(
        ..., description="Consideraciones cardiovasculares"
    )
    mental_health_support: str = Field(..., description="Apoyo para salud mental")


# Modelos para la skill de salud ósea femenina
class AssessBoneHealthInput(BaseModel):
    """Esquema de entrada para evaluación de salud ósea."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con factores de riesgo"
    )
    age: Optional[int] = Field(None, description="Edad de la usuaria")
    family_history: Optional[List[str]] = Field(
        None, description="Historial familiar de problemas óseos"
    )
    lifestyle_factors: Optional[Dict[str, Any]] = Field(
        None, description="Factores de estilo de vida"
    )


class BoneHealthRecommendation(BaseModel):
    """Modelo para recomendación de salud ósea."""

    intervention_type: str = Field(..., description="Tipo de intervención")
    specific_recommendations: List[str] = Field(
        ..., description="Recomendaciones específicas"
    )
    frequency: str = Field(..., description="Frecuencia recomendada")
    expected_benefits: str = Field(..., description="Beneficios esperados")
    monitoring_approach: str = Field(..., description="Enfoque de monitoreo")


class AssessBoneHealthOutput(BaseModel):
    """Esquema de salida para evaluación de salud ósea."""

    risk_assessment: str = Field(..., description="Evaluación del riesgo")
    exercise_recommendations: List[BoneHealthRecommendation] = Field(
        ..., description="Recomendaciones de ejercicio para salud ósea"
    )
    nutrition_recommendations: List[BoneHealthRecommendation] = Field(
        ..., description="Recomendaciones nutricionales para salud ósea"
    )
    lifestyle_modifications: List[str] = Field(
        ..., description="Modificaciones de estilo de vida"
    )
    screening_recommendations: str = Field(
        ..., description="Recomendaciones de screening"
    )


# Modelos para la skill de bienestar emocional femenino
class EmotionalWellnessInput(BaseModel):
    """Esquema de entrada para bienestar emocional."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil emocional del usuario"
    )
    current_mood: Optional[str] = Field(None, description="Estado de ánimo actual")
    stress_level: Optional[str] = Field(
        None, description="Nivel de estrés: low, moderate, high"
    )
    hormonal_phase: Optional[str] = Field(None, description="Fase hormonal actual")


class MoodSupportStrategy(BaseModel):
    """Modelo para estrategia de apoyo emocional."""

    strategy_name: str = Field(..., description="Nombre de la estrategia")
    description: str = Field(..., description="Descripción de la estrategia")
    implementation_steps: List[str] = Field(..., description="Pasos de implementación")
    expected_timeframe: str = Field(
        ..., description="Marco temporal esperado para beneficios"
    )
    hormonal_alignment: str = Field(..., description="Alineación con ciclo hormonal")


class EmotionalWellnessOutput(BaseModel):
    """Esquema de salida para bienestar emocional."""

    mood_support_strategies: List[MoodSupportStrategy] = Field(
        ..., description="Estrategias de apoyo emocional"
    )
    stress_management_techniques: List[str] = Field(
        ..., description="Técnicas de manejo del estrés"
    )
    hormonal_mood_connection: str = Field(
        ..., description="Conexión entre hormonas y estado de ánimo"
    )
    self_care_recommendations: List[str] = Field(
        ..., description="Recomendaciones de autocuidado"
    )
    professional_support_guidance: str = Field(
        ..., description="Guía para apoyo profesional"
    )


# ===== ESQUEMAS CONVERSACIONALES =====


class StartMenstrualConversationInput(BaseModel):
    """Esquema de entrada para iniciar conversación sobre ciclo menstrual."""

    user_text: str = Field(..., description="Texto del usuario")
    menstrual_cycle_day: Optional[int] = Field(
        None, description="Día del ciclo menstrual actual"
    )
    current_symptoms: Optional[List[str]] = Field(None, description="Síntomas actuales")
    conversation_context: Optional[str] = Field(
        None, description="Contexto de la conversación"
    )
    user_emotion: Optional[str] = Field(
        None, description="Emoción detectada del usuario"
    )


class StartMenstrualConversationOutput(BaseModel):
    """Esquema de salida para iniciar conversación sobre ciclo menstrual."""

    conversation_response: str = Field(
        ..., description="Respuesta conversacional empática"
    )
    conversation_id: str = Field(..., description="ID único de la conversación")
    suggested_topics: List[str] = Field(
        ..., description="Temas sugeridos para continuar"
    )
    phase_specific_guidance: str = Field(
        ..., description="Guía específica para la fase actual"
    )


class HormonalGuidanceConversationInput(BaseModel):
    """Esquema de entrada para conversación de guía hormonal."""

    user_text: str = Field(..., description="Texto del usuario")
    hormonal_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones hormonales específicas"
    )
    life_stage: Optional[str] = Field(
        None,
        description="Etapa de vida (adolescencia, edad reproductiva, perimenopausia, etc.)",
    )
    current_treatments: Optional[List[str]] = Field(
        None, description="Tratamientos actuales"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class HormonalGuidanceConversationOutput(BaseModel):
    """Esquema de salida para conversación de guía hormonal."""

    guidance_response: str = Field(..., description="Respuesta de guía hormonal")
    educational_content: str = Field(
        ..., description="Contenido educativo sobre hormonas"
    )
    lifestyle_recommendations: List[str] = Field(
        ..., description="Recomendaciones de estilo de vida"
    )
    follow_up_questions: List[str] = Field(..., description="Preguntas de seguimiento")


class PregnancyWellnessConversationInput(BaseModel):
    """Esquema de entrada para conversación de bienestar en embarazo."""

    user_text: str = Field(..., description="Texto del usuario")
    pregnancy_stage: Optional[str] = Field(None, description="Etapa del embarazo")
    specific_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones específicas"
    )
    previous_pregnancies: Optional[int] = Field(
        None, description="Número de embarazos previos"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class PregnancyWellnessConversationOutput(BaseModel):
    """Esquema de salida para conversación de bienestar en embarazo."""

    wellness_response: str = Field(
        ..., description="Respuesta de bienestar para embarazo"
    )
    safety_guidelines: List[str] = Field(..., description="Pautas de seguridad")
    nutrition_tips: List[str] = Field(..., description="Consejos nutricionales")
    exercise_recommendations: List[str] = Field(
        ..., description="Recomendaciones de ejercicio"
    )


class MenopauseCoachingConversationInput(BaseModel):
    """Esquema de entrada para conversación de coaching en menopausia."""

    user_text: str = Field(..., description="Texto del usuario")
    menopause_stage: Optional[str] = Field(
        None,
        description="Etapa de menopausia (perimenopausia, menopausia, postmenopausia)",
    )
    symptoms_experienced: Optional[List[str]] = Field(
        None, description="Síntomas experimentados"
    )
    current_management: Optional[List[str]] = Field(
        None, description="Manejo actual de síntomas"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class MenopauseCoachingConversationOutput(BaseModel):
    """Esquema de salida para conversación de coaching en menopausia."""

    coaching_response: str = Field(
        ..., description="Respuesta de coaching para menopausia"
    )
    symptom_management: List[str] = Field(
        ..., description="Estrategias de manejo de síntomas"
    )
    lifestyle_adaptations: List[str] = Field(
        ..., description="Adaptaciones de estilo de vida"
    )
    empowerment_message: str = Field(..., description="Mensaje de empoderamiento")


class FemaleTrainingAdaptationConversationInput(BaseModel):
    """Esquema de entrada para conversación de adaptación de entrenamiento femenino."""

    user_text: str = Field(..., description="Texto del usuario")
    current_cycle_phase: Optional[str] = Field(
        None, description="Fase actual del ciclo"
    )
    fitness_level: Optional[str] = Field(None, description="Nivel de fitness actual")
    training_goals: Optional[List[str]] = Field(
        None, description="Objetivos de entrenamiento"
    )
    physical_limitations: Optional[List[str]] = Field(
        None, description="Limitaciones físicas"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class FemaleTrainingAdaptationConversationOutput(BaseModel):
    """Esquema de salida para conversación de adaptación de entrenamiento femenino."""

    training_response: str = Field(
        ..., description="Respuesta de adaptación de entrenamiento"
    )
    cycle_specific_workout: str = Field(
        ..., description="Entrenamiento específico para la fase del ciclo"
    )
    intensity_recommendations: List[str] = Field(
        ..., description="Recomendaciones de intensidad"
    )
    recovery_guidance: List[str] = Field(..., description="Guía de recuperación")
