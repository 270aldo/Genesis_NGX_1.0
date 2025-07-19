"""
Esquemas para el agente PrecisionNutritionArchitect.

Este módulo define los esquemas de entrada y salida para las skills del agente
PrecisionNutritionArchitect utilizando modelos Pydantic.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


# Modelos para la skill de creación de plan de comidas
class CreateMealPlanInput(BaseModel):
    """Esquema de entrada para la skill de creación de plan de comidas."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        None, description="Restricciones alimenticias del usuario"
    )
    allergies: Optional[List[str]] = Field(
        None, description="Alergias alimentarias del usuario"
    )
    goals: Optional[List[str]] = Field(
        None, description="Objetivos nutricionales del usuario"
    )


class MealItem(BaseModel):
    """Modelo para un elemento de comida en un plan de alimentación."""

    name: str = Field(..., description="Nombre del alimento")
    portion: str = Field(..., description="Porción o cantidad")
    calories: Optional[int] = Field(None, description="Calorías aproximadas")
    macros: Optional[Dict[str, Any]] = Field(None, description="Macronutrientes")


class Meal(BaseModel):
    """Modelo para una comida en un plan de alimentación."""

    name: str = Field(..., description="Nombre de la comida (desayuno, almuerzo, etc.)")
    time: str = Field(..., description="Hora recomendada")
    items: List[MealItem] = Field(..., description="Elementos de la comida")
    notes: Optional[str] = Field(None, description="Notas adicionales")


class CreateMealPlanOutput(BaseModel):
    """Esquema de salida para la skill de creación de plan de comidas."""

    daily_plan: List[Meal] = Field(..., description="Plan diario de comidas")
    total_calories: Optional[int] = Field(None, description="Total de calorías diarias")
    macronutrient_distribution: Optional[Dict[str, Any]] = Field(
        None, description="Distribución de macronutrientes"
    )
    recommendations: Optional[List[str]] = Field(
        None, description="Recomendaciones generales"
    )
    notes: Optional[str] = Field(None, description="Notas adicionales")


# Modelos para la skill de recomendación de suplementos
class RecommendSupplementsInput(BaseModel):
    """Esquema de entrada para la skill de recomendación de suplementos."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )
    biomarkers: Optional[Dict[str, Any]] = Field(
        None, description="Biomarcadores del usuario"
    )
    current_supplements: Optional[List[str]] = Field(
        None, description="Suplementos actuales del usuario"
    )
    goals: Optional[List[str]] = Field(None, description="Objetivos del usuario")


class Supplement(BaseModel):
    """Modelo para un suplemento recomendado."""

    name: str = Field(..., description="Nombre del suplemento")
    dosage: str = Field(..., description="Dosis recomendada")
    timing: str = Field(..., description="Momento óptimo de consumo")
    benefits: List[str] = Field(..., description="Beneficios esperados")
    precautions: Optional[List[str]] = Field(
        None, description="Precauciones a considerar"
    )
    natural_alternatives: Optional[List[str]] = Field(
        None, description="Alternativas naturales"
    )


class RecommendSupplementsOutput(BaseModel):
    """Esquema de salida para la skill de recomendación de suplementos."""

    supplements: List[Supplement] = Field(..., description="Suplementos recomendados")
    general_recommendations: str = Field(
        ..., description="Recomendaciones generales sobre suplementación"
    )
    notes: Optional[str] = Field(None, description="Notas adicionales")


# Modelos para la skill de análisis de biomarcadores
class AnalyzeBiomarkersInput(BaseModel):
    """Esquema de entrada para la skill de análisis de biomarcadores."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    biomarkers: Dict[str, Any] = Field(
        ..., description="Biomarcadores del usuario a analizar"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )
    reference_ranges: Optional[Dict[str, Any]] = Field(
        None, description="Rangos de referencia para los biomarcadores"
    )


class BiomarkerAnalysis(BaseModel):
    """Modelo para el análisis de un biomarcador."""

    name: str = Field(..., description="Nombre del biomarcador")
    value: Any = Field(..., description="Valor del biomarcador")
    reference_range: Optional[str] = Field(None, description="Rango de referencia")
    status: str = Field(..., description="Estado (normal, bajo, alto)")
    interpretation: str = Field(..., description="Interpretación del valor")
    nutritional_implications: List[str] = Field(
        ..., description="Implicaciones nutricionales"
    )
    recommendations: List[str] = Field(
        ..., description="Recomendaciones basadas en el valor"
    )


class AnalyzeBiomarkersOutput(BaseModel):
    """Esquema de salida para la skill de análisis de biomarcadores."""

    analyses: List[BiomarkerAnalysis] = Field(
        ..., description="Análisis de biomarcadores"
    )
    overall_assessment: str = Field(
        ..., description="Evaluación general de los biomarcadores"
    )
    nutritional_priorities: List[str] = Field(
        ..., description="Prioridades nutricionales basadas en biomarcadores"
    )
    supplement_considerations: Optional[List[str]] = Field(
        None, description="Consideraciones sobre suplementación"
    )


# Modelos para la skill de planificación de crononutrición
class PlanChrononutritionInput(BaseModel):
    """Esquema de entrada para la skill de planificación de crononutrición."""

    input_text: str = Field(..., description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )
    daily_schedule: Optional[Dict[str, Any]] = Field(
        None, description="Horario diario del usuario"
    )
    training_schedule: Optional[Dict[str, Any]] = Field(
        None, description="Horario de entrenamiento del usuario"
    )
    sleep_pattern: Optional[Dict[str, Any]] = Field(
        None, description="Patrón de sueño del usuario"
    )


class NutritionTimeWindow(BaseModel):
    """Modelo para una ventana de tiempo nutricional."""

    name: str = Field(
        ..., description="Nombre de la ventana (ej. 'Alimentación', 'Ayuno')"
    )
    start_time: str = Field(..., description="Hora de inicio")
    end_time: str = Field(..., description="Hora de fin")
    description: str = Field(..., description="Descripción de la ventana")
    nutritional_focus: List[str] = Field(
        ..., description="Enfoque nutricional para esta ventana"
    )
    recommended_foods: Optional[List[str]] = Field(
        None, description="Alimentos recomendados"
    )
    foods_to_avoid: Optional[List[str]] = Field(None, description="Alimentos a evitar")


class PlanChrononutritionOutput(BaseModel):
    """Esquema de salida para la skill de planificación de crononutrición."""

    time_windows: List[NutritionTimeWindow] = Field(
        ..., description="Ventanas de tiempo nutricionales"
    )
    fasting_period: Optional[str] = Field(
        None, description="Período de ayuno recomendado"
    )
    eating_period: Optional[str] = Field(
        None, description="Período de alimentación recomendado"
    )
    pre_workout_nutrition: Optional[Dict[str, Any]] = Field(
        None, description="Nutrición pre-entrenamiento"
    )
    post_workout_nutrition: Optional[Dict[str, Any]] = Field(
        None, description="Nutrición post-entrenamiento"
    )
    general_recommendations: str = Field(
        ..., description="Recomendaciones generales de crononutrición"
    )


# Artefactos
class MealPlanArtifact(BaseModel):
    """Artefacto para un plan de comidas."""

    plan_id: str = Field(..., description="ID único del plan de comidas")
    created_at: str = Field(..., description="Timestamp de creación")
    total_meals: int = Field(..., description="Número total de comidas")
    calories: Optional[int] = Field(None, description="Calorías totales")
    user_goals: Optional[List[str]] = Field(None, description="Objetivos del usuario")


class SupplementRecommendationArtifact(BaseModel):
    """Artefacto para recomendaciones de suplementos."""

    recommendation_id: str = Field(..., description="ID único de la recomendación")
    created_at: str = Field(..., description="Timestamp de creación")
    supplement_count: int = Field(..., description="Número de suplementos recomendados")
    based_on_biomarkers: bool = Field(..., description="Si se basó en biomarcadores")


class BiomarkerAnalysisArtifact(BaseModel):
    """Artefacto para análisis de biomarcadores."""

    analysis_id: str = Field(..., description="ID único del análisis")
    created_at: str = Field(..., description="Timestamp de creación")
    biomarker_count: int = Field(..., description="Número de biomarcadores analizados")
    critical_findings: bool = Field(
        ..., description="Si se encontraron hallazgos críticos"
    )


class ChrononutritionPlanArtifact(BaseModel):
    """Artefacto para un plan de crononutrición."""

    plan_id: str = Field(..., description="ID único del plan")
    created_at: str = Field(..., description="Timestamp de creación")
    window_count: int = Field(..., description="Número de ventanas nutricionales")
    fasting_hours: Optional[int] = Field(
        None, description="Horas de ayuno recomendadas"
    )


# Modelos para la skill de análisis de imágenes de alimentos
class AnalyzeFoodImageInput(BaseModel):
    """Esquema de entrada para la skill de análisis de imágenes de alimentos."""

    image_data: Union[str, Dict[str, Any]] = Field(
        ..., description="Datos de la imagen (base64, URL o ruta de archivo)"
    )
    user_input: Optional[str] = Field("", description="Texto de entrada del usuario")
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con información relevante"
    )
    dietary_preferences: Optional[List[str]] = Field(
        None, description="Preferencias dietéticas del usuario"
    )


class NutrientInfo(BaseModel):
    """Modelo para información nutricional de un alimento."""

    name: str = Field(..., description="Nombre del nutriente")
    amount: str = Field(..., description="Cantidad del nutriente")
    unit: str = Field(..., description="Unidad de medida")
    daily_value_percent: Optional[float] = Field(
        None, description="Porcentaje del valor diario recomendado"
    )


class FoodItem(BaseModel):
    """Modelo para un alimento identificado en la imagen."""

    name: str = Field(..., description="Nombre del alimento")
    confidence_score: float = Field(
        ..., description="Puntuación de confianza (0.0-1.0)"
    )
    estimated_calories: Optional[str] = Field(None, description="Calorías estimadas")
    estimated_portion: Optional[str] = Field(None, description="Porción estimada")
    macronutrients: Optional[Dict[str, str]] = Field(
        None, description="Macronutrientes estimados"
    )
    nutrients: Optional[List[NutrientInfo]] = Field(
        None, description="Información nutricional detallada"
    )


class AnalyzeFoodImageOutput(BaseModel):
    """Esquema de salida para la skill de análisis de imágenes de alimentos."""

    identified_foods: List[FoodItem] = Field(
        ..., description="Alimentos identificados en la imagen"
    )
    total_calories: Optional[str] = Field(
        None, description="Calorías totales estimadas"
    )
    meal_type: Optional[str] = Field(
        None, description="Tipo de comida (desayuno, almuerzo, cena, snack)"
    )
    nutritional_assessment: str = Field(
        ..., description="Evaluación nutricional general"
    )
    health_score: Optional[float] = Field(
        None, description="Puntuación de salud (0-10)"
    )
    recommendations: List[str] = Field(..., description="Recomendaciones nutricionales")
    alternatives: Optional[List[Dict[str, str]]] = Field(
        None, description="Alternativas más saludables"
    )


class FoodImageAnalysisArtifact(BaseModel):
    """Artefacto para análisis de imágenes de alimentos."""

    analysis_id: str = Field(..., description="ID único del análisis")
    created_at: str = Field(..., description="Timestamp de creación")
    food_count: int = Field(..., description="Número de alimentos identificados")
    health_score: Optional[float] = Field(
        None, description="Puntuación de salud (0-10)"
    )
    processed_image_url: Optional[str] = Field(
        None, description="URL de la imagen procesada con anotaciones"
    )


# Modelos para la skill de sincronización con MyFitnessPal
class SyncNutritionDataInput(BaseModel):
    """Esquema de entrada para sincronización de datos nutricionales."""

    user_id: str = Field(..., description="ID del usuario NGX")
    days_back: int = Field(7, description="Número de días hacia atrás para sincronizar")
    platform: str = Field("myfitnesspal", description="Plataforma de nutrición")
    force_refresh: bool = Field(False, description="Forzar actualización de datos")


class SyncNutritionDataOutput(BaseModel):
    """Esquema de salida para sincronización de datos nutricionales."""

    success: bool = Field(..., description="Si la sincronización fue exitosa")
    days_synced: int = Field(..., description="Número de días sincronizados")
    meals_synced: int = Field(..., description="Número de comidas sincronizadas")
    foods_synced: int = Field(..., description="Número de alimentos sincronizados")
    summary: Dict[str, Any] = Field(..., description="Resumen de datos nutricionales")
    insights: List[str] = Field(..., description="Insights nutricionales generados")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")


# Modelos para la skill de análisis de tendencias nutricionales
class AnalyzeNutritionTrendsInput(BaseModel):
    """Esquema de entrada para análisis de tendencias nutricionales."""

    user_id: str = Field(..., description="ID del usuario NGX")
    days: int = Field(30, description="Número de días para analizar")
    metrics: List[str] = Field(
        ["calories", "protein", "carbs", "fat"], description="Métricas a analizar"
    )


class NutritionTrend(BaseModel):
    """Modelo para una tendencia nutricional."""

    metric: str = Field(..., description="Métrica analizada")
    average: float = Field(..., description="Promedio en el período")
    trend: str = Field(
        ..., description="Dirección de la tendencia: increasing, decreasing, stable"
    )
    variation: float = Field(..., description="Porcentaje de variación")
    recommendation: str = Field(..., description="Recomendación basada en la tendencia")


class AnalyzeNutritionTrendsOutput(BaseModel):
    """Esquema de salida para análisis de tendencias nutricionales."""

    trends: List[NutritionTrend] = Field(..., description="Tendencias analizadas")
    overall_compliance: float = Field(
        ..., description="Porcentaje de cumplimiento general"
    )
    macro_balance: Dict[str, float] = Field(
        ..., description="Balance de macronutrientes"
    )
    recommendations: List[str] = Field(..., description="Recomendaciones generales")
    needs_adjustment: bool = Field(..., description="Si el plan necesita ajustes")


# ===== ESQUEMAS CONVERSACIONALES =====


class NutritionalAssessmentConversationInput(BaseModel):
    """Esquema de entrada para evaluación nutricional conversacional."""

    user_text: str = Field(..., description="Texto del usuario sobre su nutrición")
    current_diet: Optional[List[str]] = Field(
        None, description="Alimentación actual típica"
    )
    health_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones de salud"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        None, description="Restricciones alimentarias"
    )
    nutrition_goals: Optional[List[str]] = Field(
        None, description="Objetivos nutricionales"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class NutritionalAssessmentConversationOutput(BaseModel):
    """Esquema de salida para evaluación nutricional conversacional."""

    assessment_response: str = Field(
        ..., description="Respuesta de evaluación nutricional"
    )
    conversation_id: str = Field(..., description="ID único de la conversación")
    nutritional_insights: List[str] = Field(
        ..., description="Insights nutricionales clave"
    )
    suggested_improvements: List[str] = Field(..., description="Mejoras sugeridas")
    follow_up_questions: List[str] = Field(..., description="Preguntas de seguimiento")


class MealPlanningConversationInput(BaseModel):
    """Esquema de entrada para planificación de comidas conversacional."""

    user_text: str = Field(..., description="Texto del usuario sobre planificación")
    lifestyle: Optional[str] = Field(
        None, description="Estilo de vida (activo, sedentario, etc.)"
    )
    cooking_skills: Optional[str] = Field(None, description="Habilidades culinarias")
    time_constraints: Optional[List[str]] = Field(
        None, description="Limitaciones de tiempo"
    )
    food_preferences: Optional[List[str]] = Field(
        None, description="Preferencias alimentarias"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class MealPlanningConversationOutput(BaseModel):
    """Esquema de salida para planificación de comidas conversacional."""

    planning_response: str = Field(
        ..., description="Respuesta de planificación conversacional"
    )
    meal_suggestions: List[str] = Field(..., description="Sugerencias de comidas")
    prep_strategies: List[str] = Field(..., description="Estrategias de preparación")
    shopping_tips: List[str] = Field(..., description="Consejos de compras")


class SupplementGuidanceConversationInput(BaseModel):
    """Esquema de entrada para guía de suplementos conversacional."""

    user_text: str = Field(..., description="Consulta sobre suplementos")
    current_supplements: Optional[List[str]] = Field(
        None, description="Suplementos actuales"
    )
    health_conditions: Optional[List[str]] = Field(
        None, description="Condiciones de salud"
    )
    specific_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones específicas"
    )
    biomarker_data: Optional[Dict[str, Any]] = Field(
        None, description="Datos de biomarcadores"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class SupplementGuidanceConversationOutput(BaseModel):
    """Esquema de salida para guía de suplementos conversacional."""

    guidance_response: str = Field(
        ..., description="Respuesta de guía sobre suplementos"
    )
    supplement_insights: List[str] = Field(
        ..., description="Insights sobre suplementos"
    )
    safety_considerations: List[str] = Field(
        ..., description="Consideraciones de seguridad"
    )
    timing_recommendations: List[str] = Field(
        ..., description="Recomendaciones de timing"
    )


class BiomarkerInterpretationConversationInput(BaseModel):
    """Esquema de entrada para interpretación de biomarcadores conversacional."""

    user_text: str = Field(..., description="Consulta sobre biomarcadores")
    biomarker_results: Optional[Dict[str, Any]] = Field(
        None, description="Resultados de biomarcadores"
    )
    previous_results: Optional[Dict[str, Any]] = Field(
        None, description="Resultados previos"
    )
    symptoms: Optional[List[str]] = Field(None, description="Síntomas reportados")
    medications: Optional[List[str]] = Field(None, description="Medicamentos actuales")
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class BiomarkerInterpretationConversationOutput(BaseModel):
    """Esquema de salida para interpretación de biomarcadores conversacional."""

    interpretation_response: str = Field(..., description="Respuesta de interpretación")
    key_findings: List[str] = Field(..., description="Hallazgos clave")
    nutrition_implications: List[str] = Field(
        ..., description="Implicaciones nutricionales"
    )
    monitoring_recommendations: List[str] = Field(
        ..., description="Recomendaciones de monitoreo"
    )


class LifestyleNutritionConversationInput(BaseModel):
    """Esquema de entrada para asesoramiento nutricional de estilo de vida."""

    user_text: str = Field(..., description="Consulta sobre nutrición y estilo de vida")
    daily_routine: Optional[str] = Field(None, description="Rutina diaria típica")
    work_schedule: Optional[str] = Field(None, description="Horario de trabajo")
    stress_levels: Optional[str] = Field(None, description="Niveles de estrés")
    sleep_quality: Optional[str] = Field(None, description="Calidad del sueño")
    exercise_routine: Optional[str] = Field(None, description="Rutina de ejercicio")
    conversation_id: Optional[str] = Field(
        None, description="ID de conversación existente"
    )


class LifestyleNutritionConversationOutput(BaseModel):
    """Esquema de salida para asesoramiento nutricional de estilo de vida."""

    lifestyle_response: str = Field(..., description="Respuesta de asesoramiento")
    lifestyle_adaptations: List[str] = Field(
        ..., description="Adaptaciones de estilo de vida"
    )
    meal_timing_tips: List[str] = Field(
        ..., description="Consejos de timing de comidas"
    )
    stress_nutrition_strategies: List[str] = Field(
        ..., description="Estrategias nutricionales para estrés"
    )


# Modelos para análisis de etiquetas nutricionales
class AnalyzeNutritionLabelInput(BaseModel):
    """Esquema de entrada para el análisis de etiquetas nutricionales."""

    image_data: Union[str, Dict[str, Any]] = Field(
        ...,
        description="Datos de la imagen de la etiqueta (base64, URL o ruta de archivo)",
    )
    user_input: Optional[str] = Field(
        "", description="Pregunta específica del usuario sobre el producto"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con restricciones dietéticas y objetivos"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        None,
        description="Restricciones dietéticas específicas (alérgenos, intolerancias)",
    )
    comparison_mode: bool = Field(
        False, description="Si se debe comparar con productos similares"
    )


class IngredientAnalysis(BaseModel):
    """Modelo para análisis de un ingrediente específico."""

    name: str = Field(..., description="Nombre del ingrediente")
    category: str = Field(
        ..., description="Categoría del ingrediente (natural, procesado, aditivo)"
    )
    health_impact: str = Field(
        ..., description="Impacto en la salud (positivo, neutro, negativo)"
    )
    allergen_risk: Optional[str] = Field(None, description="Riesgo de alérgeno")
    processing_level: str = Field(
        ..., description="Nivel de procesamiento (mínimo, moderado, alto)"
    )
    recommendations: Optional[str] = Field(
        None, description="Recomendaciones específicas"
    )


class NutritionFacts(BaseModel):
    """Modelo para información nutricional extraída de la etiqueta."""

    serving_size: Optional[str] = Field(None, description="Tamaño de la porción")
    servings_per_container: Optional[str] = Field(
        None, description="Porciones por envase"
    )
    calories_per_serving: Optional[float] = Field(
        None, description="Calorías por porción"
    )
    total_fat: Optional[str] = Field(None, description="Grasa total")
    saturated_fat: Optional[str] = Field(None, description="Grasa saturada")
    trans_fat: Optional[str] = Field(None, description="Grasa trans")
    cholesterol: Optional[str] = Field(None, description="Colesterol")
    sodium: Optional[str] = Field(None, description="Sodio")
    total_carbs: Optional[str] = Field(None, description="Carbohidratos totales")
    dietary_fiber: Optional[str] = Field(None, description="Fibra dietética")
    sugars: Optional[str] = Field(None, description="Azúcares")
    added_sugars: Optional[str] = Field(None, description="Azúcares añadidos")
    protein: Optional[str] = Field(None, description="Proteína")
    vitamins_minerals: Optional[Dict[str, str]] = Field(
        None, description="Vitaminas y minerales"
    )


class ProductAssessment(BaseModel):
    """Modelo para evaluación general del producto."""

    health_score: float = Field(..., description="Puntuación de salud (0-10)")
    processing_level: str = Field(
        ...,
        description="Nivel de procesamiento (ultra-procesado, procesado, mínimamente procesado)",
    )
    quality_grade: str = Field(
        ..., description="Calificación de calidad (A, B, C, D, F)"
    )
    allergen_warnings: List[str] = Field(..., description="Advertencias de alérgenos")
    dietary_compatibility: Dict[str, bool] = Field(
        ..., description="Compatibilidad con dietas específicas"
    )
    environmental_impact: Optional[str] = Field(
        None, description="Impacto ambiental estimado"
    )


class AnalyzeNutritionLabelOutput(BaseModel):
    """Esquema de salida para el análisis de etiquetas nutricionales."""

    product_name: str = Field(..., description="Nombre del producto identificado")
    brand: Optional[str] = Field(None, description="Marca del producto")
    nutrition_facts: NutritionFacts = Field(
        ..., description="Información nutricional extraída"
    )
    ingredients_list: List[str] = Field(..., description="Lista de ingredientes")
    ingredient_analysis: List[IngredientAnalysis] = Field(
        ..., description="Análisis detallado de ingredientes"
    )
    product_assessment: ProductAssessment = Field(
        ..., description="Evaluación general del producto"
    )
    personalized_recommendations: List[str] = Field(
        ..., description="Recomendaciones personalizadas"
    )
    alternatives: Optional[List[Dict[str, str]]] = Field(
        None, description="Alternativas más saludables"
    )
    warnings: List[str] = Field(..., description="Advertencias importantes")
    summary: str = Field(..., description="Resumen ejecutivo del análisis")


class NutritionLabelAnalysisArtifact(BaseModel):
    """Artefacto para análisis de etiquetas nutricionales."""

    analysis_id: str = Field(..., description="ID único del análisis")
    created_at: str = Field(..., description="Timestamp de creación")
    product_name: str = Field(..., description="Nombre del producto")
    health_score: float = Field(..., description="Puntuación de salud (0-10)")
    quality_grade: str = Field(..., description="Calificación de calidad")
    processed_image_url: Optional[str] = Field(
        None, description="URL de la imagen procesada con anotaciones"
    )


# Modelos mejorados para análisis avanzado de platos preparados
class AnalyzePreparedMealInput(BaseModel):
    """Esquema de entrada para análisis avanzado de platos preparados."""

    image_data: Union[str, Dict[str, Any]] = Field(
        ..., description="Datos de la imagen del plato (base64, URL o ruta de archivo)"
    )
    user_input: Optional[str] = Field(
        "", description="Descripción adicional del usuario sobre el plato"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="Perfil del usuario con objetivos y restricciones"
    )
    meal_context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto de la comida (hora, tipo de comida, ocasión)"
    )
    portion_estimation_mode: bool = Field(
        True, description="Si se debe incluir estimación detallada de porciones"
    )
    nutrition_precision: str = Field(
        "standard",
        description="Nivel de precisión nutricional (basic, standard, detailed)",
    )


class FoodComponent(BaseModel):
    """Modelo para un componente individual del plato."""

    name: str = Field(..., description="Nombre del alimento/ingrediente")
    category: str = Field(
        ..., description="Categoría (proteína, carbohidrato, grasa, vegetal, etc.)"
    )
    confidence_score: float = Field(
        ..., description="Confianza en la identificación (0.0-1.0)"
    )
    estimated_weight: Optional[str] = Field(
        None, description="Peso estimado del componente"
    )
    estimated_volume: Optional[str] = Field(
        None, description="Volumen estimado del componente"
    )
    portion_size: str = Field(..., description="Tamaño de porción en términos comunes")
    cooking_method: Optional[str] = Field(
        None, description="Método de cocción detectado"
    )
    visible_percentage: float = Field(
        ..., description="Porcentaje visible del componente (0.0-1.0)"
    )
    nutrition_density: str = Field(
        ..., description="Densidad nutricional (alta, media, baja)"
    )


class MacronutrientBreakdown(BaseModel):
    """Modelo detallado para desglose de macronutrientes."""

    protein_grams: Optional[float] = Field(None, description="Proteína en gramos")
    carbs_grams: Optional[float] = Field(None, description="Carbohidratos en gramos")
    fat_grams: Optional[float] = Field(None, description="Grasas en gramos")
    fiber_grams: Optional[float] = Field(None, description="Fibra en gramos")
    sugar_grams: Optional[float] = Field(None, description="Azúcares en gramos")
    sodium_mg: Optional[float] = Field(None, description="Sodio en miligramos")
    protein_quality_score: Optional[float] = Field(
        None, description="Calidad de proteína (0-10)"
    )
    carb_complexity: str = Field(
        ..., description="Complejidad de carbohidratos (simple, complejo, mixto)"
    )


class MealNutritionAnalysis(BaseModel):
    """Modelo para análisis nutricional completo de la comida."""

    total_calories: Optional[float] = Field(
        None, description="Calorías totales estimadas"
    )
    calories_range: Dict[str, float] = Field(
        ..., description="Rango de calorías (min, max)"
    )
    macronutrient_breakdown: MacronutrientBreakdown = Field(
        ..., description="Desglose de macronutrientes"
    )
    micronutrient_highlights: List[str] = Field(
        ..., description="Micronutrientes destacados"
    )
    nutritional_balance_score: float = Field(
        ..., description="Puntuación de balance nutricional (0-10)"
    )
    meal_completeness: str = Field(
        ...,
        description="Completitud de la comida (completa, incompleta, necesita_complementos)",
    )


class PortionAssessment(BaseModel):
    """Modelo para evaluación de porciones."""

    total_volume_assessment: str = Field(
        ..., description="Evaluación del volumen total del plato"
    )
    portion_adequacy: str = Field(
        ..., description="Adecuación de la porción (pequeña, adecuada, grande)"
    )
    portion_recommendations: List[str] = Field(
        ..., description="Recomendaciones sobre porciones"
    )
    visual_satiety_cues: List[str] = Field(
        ..., description="Señales visuales de saciedad"
    )
    caloric_density: str = Field(
        ..., description="Densidad calórica del plato (baja, media, alta)"
    )


class MealTimingAnalysis(BaseModel):
    """Modelo para análisis del timing de la comida."""

    optimal_timing: List[str] = Field(
        ..., description="Momentos óptimos para esta comida"
    )
    pre_post_workout_suitability: str = Field(
        ..., description="Idoneidad pre/post entrenamiento"
    )
    digestion_considerations: List[str] = Field(
        ..., description="Consideraciones de digestión"
    )
    energy_profile: str = Field(
        ..., description="Perfil energético (rápida, sostenida, prolongada)"
    )


class AnalyzePreparedMealOutput(BaseModel):
    """Esquema de salida para análisis avanzado de platos preparados."""

    meal_identification: str = Field(
        ..., description="Identificación general del plato/comida"
    )
    cuisine_type: Optional[str] = Field(None, description="Tipo de cocina detectado")
    food_components: List[FoodComponent] = Field(
        ..., description="Componentes individuales del plato"
    )
    nutrition_analysis: MealNutritionAnalysis = Field(
        ..., description="Análisis nutricional completo"
    )
    portion_assessment: PortionAssessment = Field(
        ..., description="Evaluación de porciones"
    )
    timing_analysis: MealTimingAnalysis = Field(
        ..., description="Análisis de timing óptimo"
    )
    health_score: float = Field(..., description="Puntuación de salud general (0-10)")
    program_compatibility: Dict[str, str] = Field(
        ..., description="Compatibilidad con programas NGX"
    )
    personalized_feedback: List[str] = Field(
        ..., description="Feedback personalizado para el usuario"
    )
    improvement_suggestions: List[str] = Field(..., description="Sugerencias de mejora")
    similar_healthier_options: Optional[List[Dict[str, str]]] = Field(
        None, description="Opciones similares más saludables"
    )
    preparation_insights: List[str] = Field(
        ..., description="Insights sobre la preparación"
    )
    summary: str = Field(..., description="Resumen ejecutivo del análisis")


class PreparedMealAnalysisArtifact(BaseModel):
    """Artefacto para análisis de platos preparados."""

    analysis_id: str = Field(..., description="ID único del análisis")
    created_at: str = Field(..., description="Timestamp de creación")
    meal_type: str = Field(..., description="Tipo de comida identificado")
    component_count: int = Field(..., description="Número de componentes identificados")
    health_score: float = Field(..., description="Puntuación de salud (0-10)")
    calories_estimated: Optional[float] = Field(None, description="Calorías estimadas")
    processed_image_url: Optional[str] = Field(
        None, description="URL de la imagen procesada con anotaciones"
    )
