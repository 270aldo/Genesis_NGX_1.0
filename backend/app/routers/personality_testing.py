"""
Router para testing de adaptaciones de personalidad de agentes.

Este módulo proporciona endpoints para probar y demostrar cómo los agentes
adaptan su comunicación según el programa del usuario (PRIME/LONGEVITY).
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

from core.personality.personality_adapter import PersonalityAdapter, PersonalityProfile
from core.personality.communication_styles import CommunicationStyles
from agents.elite_training_strategist.agent import EliteTrainingStrategist
from agents.elite_training_strategist.schemas import (
    GenerateTrainingPlanInput,
    UserProfile as TrainingUserProfile,
)
from agents.precision_nutrition_architect.agent import PrecisionNutritionArchitect
from agents.precision_nutrition_architect.schemas import (
    CreateMealPlanInput,
    UserProfile as NutritionUserProfile,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personality", tags=["personality-testing"])


class PersonalityTestRequest(BaseModel):
    """Request para testing de adaptación de personalidad."""

    agent_id: str = Field(..., description="ID del agente (BLAZE, SAGE, etc.)")
    program_type: str = Field(..., description="Tipo de programa (PRIME, LONGEVITY)")
    sample_message: str = Field(
        default="Genera un plan de entrenamiento personalizado para mis objetivos.",
        description="Mensaje de ejemplo para adaptar",
    )
    user_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Contexto adicional del usuario"
    )


class PersonalityTestResponse(BaseModel):
    """Response del testing de adaptación de personalidad."""

    agent_id: str
    program_type: str
    original_message: str
    adapted_message: str
    adaptation_details: Dict[str, Any]
    style_applied: Dict[str, Any]
    confidence_score: float


class PersonalityPreviewRequest(BaseModel):
    """Request para vista previa de estilos de personalidad."""

    agent_id: str
    program_type: str


@router.post("/test-adaptation", response_model=PersonalityTestResponse)
async def test_personality_adaptation(request: PersonalityTestRequest):
    """
    Prueba la adaptación de personalidad para un agente específico.

    Permite probar cómo diferentes agentes adaptan su comunicación
    según el programa del usuario (PRIME vs LONGEVITY).
    """
    try:
        # Inicializar PersonalityAdapter
        personality_adapter = PersonalityAdapter()

        # Crear perfil de usuario
        user_profile = PersonalityProfile(
            program_type=request.program_type,
            preferences=(
                request.user_context.get("preferences")
                if request.user_context
                else None
            ),
            emotional_patterns=(
                request.user_context.get("emotional_patterns")
                if request.user_context
                else None
            ),
        )

        # Aplicar adaptación
        adaptation_result = personality_adapter.adapt_response(
            agent_id=request.agent_id,
            original_message=request.sample_message,
            user_profile=user_profile,
            context=request.user_context,
        )

        return PersonalityTestResponse(
            agent_id=request.agent_id,
            program_type=request.program_type,
            original_message=request.sample_message,
            adapted_message=adaptation_result["adapted_message"],
            adaptation_details=adaptation_result["adaptation_metrics"],
            style_applied=adaptation_result["style_applied"],
            confidence_score=adaptation_result["adaptation_metrics"].get(
                "confidence_score", 0.0
            ),
        )

    except Exception as e:
        logger.error(f"Error testing personality adaptation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview-styles/{agent_id}/{program_type}")
async def get_personality_preview(agent_id: str, program_type: str):
    """
    Obtiene una vista previa de los estilos de personalidad disponibles.

    Muestra cómo se adapta la comunicación de un agente específico
    para diferentes tipos de programa.
    """
    try:
        personality_adapter = PersonalityAdapter()

        preview = personality_adapter.get_personality_preview(
            agent_id=agent_id, program_type=program_type
        )

        return preview

    except Exception as e:
        logger.error(f"Error getting personality preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-combinations")
async def get_supported_combinations():
    """
    Obtiene las combinaciones soportadas de agente-programa.

    Retorna qué agentes soportan qué tipos de programa para
    adaptación de personalidad.
    """
    try:
        personality_adapter = PersonalityAdapter()
        combinations = personality_adapter.get_supported_combinations()

        return {
            "supported_combinations": combinations,
            "available_programs": CommunicationStyles.get_available_programs(),
            "available_agents": CommunicationStyles.get_available_agents(),
        }

    except Exception as e:
        logger.error(f"Error getting supported combinations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-blaze-integration")
async def test_blaze_integration(
    user_query: str = "Necesito un plan de entrenamiento para mejorar mi rendimiento",
    program_type: str = "PRIME",
):
    """
    Prueba la integración completa de adaptación de personalidad con BLAZE.

    Ejecuta una skill real de BLAZE y muestra cómo se adapta la respuesta
    según el programa del usuario.
    """
    try:
        # Inicializar agente BLAZE
        blaze_agent = EliteTrainingStrategist()

        # Crear input para la skill
        user_profile = TrainingUserProfile(
            name="Usuario Test",
            age=35,
            fitness_level="intermediate",
            goals=["improve_performance"],
            restrictions=[],
        )

        training_input = GenerateTrainingPlanInput(
            user_query=user_query, user_profile=user_profile, program_type=program_type
        )

        # Ejecutar skill con adaptación de personalidad
        result = await blaze_agent._skill_generate_training_plan(training_input)

        return {
            "agent": "BLAZE",
            "program_type": program_type,
            "user_query": user_query,
            "generated_plan": {
                "plan_name": result.plan_name,
                "description": result.description,
                "duration_weeks": result.duration_weeks,
                "adapted_response": result.response,  # Esta respuesta ya está adaptada
            },
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Error testing BLAZE integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-analytics")
async def get_performance_analytics():
    """
    Obtiene analytics de rendimiento de las adaptaciones de personalidad.

    Muestra estadísticas sobre precisión, velocidad y efectividad
    de las adaptaciones realizadas.
    """
    try:
        personality_adapter = PersonalityAdapter()
        analytics = personality_adapter.analyze_adaptation_performance()

        return {
            "performance_analytics": analytics,
            "system_status": "operational",
            "cache_enabled": True,
        }

    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear-cache")
async def clear_adaptation_cache():
    """
    Limpia el caché de adaptaciones de personalidad.

    Útil para testing y desarrollo cuando se quieren probar
    nuevas configuraciones sin usar resultados cacheados.
    """
    try:
        personality_adapter = PersonalityAdapter()
        personality_adapter.clear_cache()

        return {
            "message": "Personality adaptation cache cleared successfully",
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Error clearing adaptation cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints de demostración con casos específicos


@router.get("/demo/blaze-prime-vs-longevity")
async def demo_blaze_prime_vs_longevity():
    """
    Demostración que compara las adaptaciones de BLAZE para PRIME vs LONGEVITY.

    Muestra la diferencia en comunicación para el mismo mensaje base
    adaptado a diferentes audiencias.
    """
    try:
        personality_adapter = PersonalityAdapter()

        base_message = "He creado un plan de entrenamiento que optimizará tu rendimiento físico. Incluye ejercicios de fuerza, cardio y flexibilidad con progresión gradual."

        # Adaptación para PRIME
        prime_profile = PersonalityProfile(program_type="PRIME")
        prime_result = personality_adapter.adapt_response(
            agent_id="BLAZE", original_message=base_message, user_profile=prime_profile
        )

        # Adaptación para LONGEVITY
        longevity_profile = PersonalityProfile(program_type="LONGEVITY")
        longevity_result = personality_adapter.adapt_response(
            agent_id="BLAZE",
            original_message=base_message,
            user_profile=longevity_profile,
        )

        return {
            "demo": "BLAZE - PRIME vs LONGEVITY",
            "base_message": base_message,
            "adaptations": {
                "PRIME": {
                    "adapted_message": prime_result["adapted_message"],
                    "style": prime_result["style_applied"],
                    "confidence": prime_result["adaptation_metrics"][
                        "confidence_score"
                    ],
                },
                "LONGEVITY": {
                    "adapted_message": longevity_result["adapted_message"],
                    "style": longevity_result["style_applied"],
                    "confidence": longevity_result["adaptation_metrics"][
                        "confidence_score"
                    ],
                },
            },
            "key_differences": [
                "PRIME: Tono ejecutivo, orientado a ROI y rendimiento",
                "LONGEVITY: Tono consultivo, enfocado en bienestar a largo plazo",
                "PRIME: Lenguaje técnico-estratégico, métricas de performance",
                "LONGEVITY: Lenguaje claro-explicativo, marcadores de salud",
            ],
        }

    except Exception as e:
        logger.error(f"Error in BLAZE demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-sage-integration")
async def test_sage_integration(
    user_query: str = "Necesito un plan nutricional para optimizar mi rendimiento",
    program_type: str = "PRIME",
):
    """
    Prueba la integración completa de adaptación de personalidad con SAGE.

    Ejecuta una skill real de SAGE y muestra cómo se adapta la respuesta
    según el programa del usuario.
    """
    try:
        # Inicializar agente SAGE
        sage_agent = PrecisionNutritionArchitect()

        # Crear input para la skill
        user_profile = NutritionUserProfile(
            name="Usuario Test",
            age=35,
            goals=["optimize_performance"],
            dietary_restrictions=[],
            activity_level="moderate",
        )

        nutrition_input = CreateMealPlanInput(
            user_input=user_query, user_profile=user_profile, program_type=program_type
        )

        # Ejecutar skill con adaptación de personalidad
        result = await sage_agent._skill_create_meal_plan(nutrition_input)

        return {
            "agent": "SAGE",
            "program_type": program_type,
            "user_query": user_query,
            "generated_plan": {
                "total_calories": result.total_calories,
                "macronutrient_distribution": result.macronutrient_distribution,
                "adapted_recommendations": result.recommendations,  # Estas están adaptadas
                "daily_plan_count": len(result.daily_plan) if result.daily_plan else 0,
            },
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Error testing SAGE integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo/sage-prime-vs-longevity")
async def demo_sage_prime_vs_longevity():
    """
    Demostración que compara las adaptaciones de SAGE para PRIME vs LONGEVITY.

    Muestra la diferencia en comunicación nutricional para el mismo mensaje base
    adaptado a diferentes audiencias.
    """
    try:
        personality_adapter = PersonalityAdapter()

        base_message = "He diseñado un plan nutricional que optimiza tu metabolismo y energía. Incluye macronutrientes balanceados, timing estratégico de comidas y suplementación personalizada."

        # Adaptación para PRIME
        prime_profile = PersonalityProfile(program_type="PRIME")
        prime_result = personality_adapter.adapt_response(
            agent_id="SAGE", original_message=base_message, user_profile=prime_profile
        )

        # Adaptación para LONGEVITY
        longevity_profile = PersonalityProfile(program_type="LONGEVITY")
        longevity_result = personality_adapter.adapt_response(
            agent_id="SAGE",
            original_message=base_message,
            user_profile=longevity_profile,
        )

        return {
            "demo": "SAGE - PRIME vs LONGEVITY",
            "base_message": base_message,
            "adaptations": {
                "PRIME": {
                    "adapted_message": prime_result["adapted_message"],
                    "style": prime_result["style_applied"],
                    "confidence": prime_result["adaptation_metrics"][
                        "confidence_score"
                    ],
                },
                "LONGEVITY": {
                    "adapted_message": longevity_result["adapted_message"],
                    "style": longevity_result["style_applied"],
                    "confidence": longevity_result["adaptation_metrics"][
                        "confidence_score"
                    ],
                },
            },
            "key_differences": [
                "PRIME: Enfoque en optimización metabólica y rendimiento ejecutivo",
                "LONGEVITY: Enfoque en salud a largo plazo y bienestar sostenible",
                "PRIME: Vocabulario estratégico - ROI nutricional, eficiencia metabólica",
                "LONGEVITY: Vocabulario educativo - nutrición preventiva, salud integral",
            ],
        }

    except Exception as e:
        logger.error(f"Error in SAGE demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo/blaze-vs-sage-comparison")
async def demo_blaze_vs_sage_comparison():
    """
    Demostración que compara las adaptaciones entre BLAZE y SAGE para el mismo programa.

    Muestra cómo diferentes agentes adaptan su comunicación de manera específica
    a su dominio de expertise (Training vs Nutrition).
    """
    try:
        personality_adapter = PersonalityAdapter()

        base_message = "He creado un protocolo personalizado que optimizará tu rendimiento y te ayudará a alcanzar tus objetivos de manera eficiente."
        program_type = "PRIME"

        # Adaptación BLAZE (Training)
        profile = PersonalityProfile(program_type=program_type)
        blaze_result = personality_adapter.adapt_response(
            agent_id="BLAZE", original_message=base_message, user_profile=profile
        )

        # Adaptación SAGE (Nutrition)
        sage_result = personality_adapter.adapt_response(
            agent_id="SAGE", original_message=base_message, user_profile=profile
        )

        return {
            "demo": f"BLAZE vs SAGE - {program_type}",
            "base_message": base_message,
            "program_type": program_type,
            "agent_adaptations": {
                "BLAZE": {
                    "adapted_message": blaze_result["adapted_message"],
                    "domain": "Elite Training",
                    "confidence": blaze_result["adaptation_metrics"][
                        "confidence_score"
                    ],
                },
                "SAGE": {
                    "adapted_message": sage_result["adapted_message"],
                    "domain": "Precision Nutrition",
                    "confidence": sage_result["adaptation_metrics"]["confidence_score"],
                },
            },
            "specialization_differences": [
                "BLAZE: Enfoque en protocolo de entrenamiento y rendimiento físico",
                "SAGE: Enfoque en optimización nutricional y metabolismo",
                "BLAZE: Vocabulario deportivo - protocolo, intensidad, recuperación",
                "SAGE: Vocabulario nutricional - metabolismo, nutrientes, suplementación",
            ],
        }

    except Exception as e:
        logger.error(f"Error in BLAZE vs SAGE demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))
