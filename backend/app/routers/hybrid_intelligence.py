"""
Router para Hybrid Intelligence API endpoints.

Este módulo proporciona endpoints REST para el sistema de Hybrid Intelligence,
permitiendo personalización avanzada de 2 capas para todos los agentes NGX.

Endpoints principales:
- POST /personalize - Personalización de 2 capas
- GET /user/{user_id}/insights - Insights del usuario
- POST /user/{user_id}/feedback - Feedback para aprendizaje
- GET /user/{user_id}/profile - Perfil de personalización
- PUT /user/{user_id}/profile - Actualizar perfil
- GET /archetypes - Información de arquetipos disponibles

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from fastapi.responses import JSONResponse

from core.auth import get_current_user
from core.logging_config import get_logger
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from core.state_manager_optimized import StateManager

# Import Hybrid Intelligence components
from core.hybrid_intelligence import (
    HybridIntelligenceEngine,
    UserProfile,
    PersonalizationContext,
    PersonalizationResult,
    UserArchetype,
    PersonalizationMode
)

from core.hybrid_intelligence.models import (
    UserProfileData,
    PersonalizationContextData,
    HybridIntelligenceRequest,
    HybridIntelligenceResponse,
    UserInsights,
    UserBiometrics,
    WorkoutData,
    BiomarkerData,
    LearningEntry
)

# Import request/response schemas
from app.schemas.hybrid_intelligence import (
    PersonalizeRequest,
    PersonalizeResponse,
    UserProfileRequest,
    UserProfileResponse,
    UserInsightsResponse,
    FeedbackRequest,
    FeedbackResponse,
    ArchetypesResponse,
    PersonalizationHistoryResponse,
    BiometricsUpdateRequest,
    WorkoutSubmissionRequest
)

# Configurar logger
logger = get_logger(__name__)

# Crear router
router = APIRouter(
    prefix="/hybrid-intelligence",
    tags=["hybrid-intelligence"],
    responses={401: {"description": "No autorizado"}},
)

# Singleton para el Hybrid Intelligence Engine
_hybrid_engine = None


def get_hybrid_engine() -> HybridIntelligenceEngine:
    """
    Dependencia para obtener una instancia del Hybrid Intelligence Engine.
    Utiliza patrón singleton para optimizar recursos.
    
    Returns:
        Instancia del HybridIntelligenceEngine
    """
    global _hybrid_engine
    if _hybrid_engine is None:
        _hybrid_engine = HybridIntelligenceEngine()
        logger.info("Hybrid Intelligence Engine initialized")
    return _hybrid_engine


def get_state_manager() -> StateManager:
    """
    Dependencia para obtener una instancia del StateManager.
    
    Returns:
        Instancia del StateManager
    """
    return state_manager_adapter


@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize_request(
    request: PersonalizeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    hybrid_engine: HybridIntelligenceEngine = Depends(get_hybrid_engine),
    state_manager: StateManager = Depends(get_state_manager)
) -> PersonalizeResponse:
    """
    Endpoint principal para personalización usando Hybrid Intelligence.
    
    Combina adaptación por arquetipo (PRIME/LONGEVITY) con modulación
    fisiológica en tiempo real para generar personalización avanzada.
    
    Args:
        request: Datos del request de personalización
        current_user: Usuario autenticado
        hybrid_engine: Engine de Hybrid Intelligence
        state_manager: Gestor de estado
        
    Returns:
        Resultado de personalización con adaptaciones aplicadas
        
    Raises:
        HTTPException: Error en el proceso de personalización
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting personalization for user {current_user['id']}")
        
        # Crear UserProfile desde request
        user_profile = UserProfile(
            user_id=current_user["id"],
            archetype=UserArchetype(request.user_data.archetype),
            age=request.user_data.age,
            gender=request.user_data.gender,
            fitness_level=request.user_data.fitness_level,
            injury_history=request.user_data.injury_history,
            current_medications=request.user_data.current_medications,
            sleep_quality=request.user_data.biometrics.sleep_quality if request.user_data.biometrics else None,
            stress_level=request.user_data.biometrics.stress_level if request.user_data.biometrics else None,
            energy_level=request.user_data.biometrics.energy_level if request.user_data.biometrics else None,
            recent_workouts=[workout.dict() for workout in request.user_data.recent_workouts],
            time_constraints=request.user_data.constraints.time_constraints,
            equipment_access=request.user_data.constraints.equipment_access,
            dietary_restrictions=request.user_data.constraints.dietary_restrictions,
            biomarkers={marker.marker_name: marker.value for marker in request.user_data.biomarkers},
            preference_scores=request.user_data.preference_scores,
            interaction_history=request.user_data.interaction_history
        )
        
        # Crear PersonalizationContext
        context = PersonalizationContext(
            user_profile=user_profile,
            agent_type=request.agent_type,
            request_type=request.request_type,
            request_content=request.request_content,
            session_context=request.session_context or {}
        )
        
        # Ejecutar personalización
        personalization_result = await hybrid_engine.personalize_for_user(
            context=context,
            mode=PersonalizationMode(request.personalization_mode)
        )
        
        # Calcular tiempo de procesamiento
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Almacenar resultado en estado para tracking
        await state_manager.store_state(
            f"personalization_{current_user['id']}_{start_time.isoformat()}",
            {
                "user_id": current_user["id"],
                "agent_type": request.agent_type,
                "result": personalization_result.dict() if hasattr(personalization_result, 'dict') else str(personalization_result),
                "processing_time_ms": processing_time,
                "timestamp": start_time.isoformat()
            },
            ttl=3600  # 1 hora
        )
        
        logger.info(f"Personalization completed for user {current_user['id']} in {processing_time}ms")
        
        return PersonalizeResponse(
            success=True,
            result=personalization_result.dict() if hasattr(personalization_result, 'dict') else {
                "archetype_adaptation": personalization_result.archetype_adaptation,
                "physiological_modulation": personalization_result.physiological_modulation,
                "combined_recommendations": personalization_result.combined_recommendations,
                "confidence_score": personalization_result.confidence_score,
                "explanation": personalization_result.explanation,
                "learning_data": personalization_result.learning_data
            },
            processing_time_ms=processing_time,
            timestamp=start_time
        )
        
    except ValueError as e:
        logger.error(f"Validation error in personalization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Datos de entrada inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in personalization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en personalización: {str(e)}"
        )


@router.get("/user/{user_id}/insights", response_model=UserInsightsResponse)
async def get_user_insights(
    user_id: str = Path(..., description="ID del usuario"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    hybrid_engine: HybridIntelligenceEngine = Depends(get_hybrid_engine)
) -> UserInsightsResponse:
    """
    Obtiene insights de personalización para un usuario específico.
    
    Analiza patrones de interacción, efectividad de personalizaciones
    y tendencias de mejora para proporcionar insights accionables.
    
    Args:
        user_id: ID del usuario para obtener insights
        current_user: Usuario autenticado
        hybrid_engine: Engine de Hybrid Intelligence
        
    Returns:
        Insights completos del usuario
        
    Raises:
        HTTPException: Error al obtener insights
    """
    try:
        # Verificar autorización (usuario solo puede ver sus propios insights)
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para ver insights de otro usuario"
            )
        
        logger.info(f"Getting insights for user {user_id}")
        
        # Obtener insights del engine
        insights = await hybrid_engine.get_user_insights(user_id)
        
        return UserInsightsResponse(
            success=True,
            insights=insights,
            generated_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo insights: {str(e)}"
        )


@router.post("/user/{user_id}/feedback", response_model=FeedbackResponse)
async def submit_personalization_feedback(
    user_id: str = Path(..., description="ID del usuario"),
    feedback: FeedbackRequest = Body(..., description="Feedback de personalización"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    hybrid_engine: HybridIntelligenceEngine = Depends(get_hybrid_engine),
    state_manager: StateManager = Depends(get_state_manager)
) -> FeedbackResponse:
    """
    Submite feedback sobre una personalización para mejorar el aprendizaje.
    
    El feedback se utiliza para entrenar el sistema de aprendizaje continuo
    y mejorar futuras personalizaciones.
    
    Args:
        user_id: ID del usuario
        feedback: Datos de feedback
        current_user: Usuario autenticado
        hybrid_engine: Engine de Hybrid Intelligence
        state_manager: Gestor de estado
        
    Returns:
        Confirmación del feedback recibido
        
    Raises:
        HTTPException: Error al procesar feedback
    """
    try:
        # Verificar autorización
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para enviar feedback por otro usuario"
            )
        
        logger.info(f"Receiving feedback from user {user_id} for session {feedback.session_id}")
        
        # Recuperar contexto y resultado de personalización desde estado
        personalization_data = await state_manager.get_state(
            f"personalization_{user_id}_{feedback.session_id}"
        )
        
        if not personalization_data:
            # Crear contexto básico si no se encuentra
            logger.warning(f"Personalization data not found for session {feedback.session_id}")
            context = PersonalizationContext(
                user_profile=UserProfile(
                    user_id=user_id,
                    archetype=UserArchetype.PRIME,  # Default
                    age=30,  # Default
                    gender="unknown"
                ),
                agent_type="unknown",
                request_type="unknown",
                request_content="unknown"
            )
            
            result = PersonalizationResult(
                archetype_adaptation={},
                physiological_modulation={},
                combined_recommendations={},
                confidence_score=0.5,
                explanation="Unknown session"
            )
        else:
            # Reconstruir contexto y resultado desde datos almacenados
            context = None  # Sería reconstruido desde personalization_data
            result = None   # Sería reconstruido desde personalization_data
        
        # Preparar feedback para el learning engine
        feedback_data = {
            "satisfaction": feedback.satisfaction,
            "outcome_success": feedback.outcome_success,
            "found_helpful": feedback.found_helpful,
            "intensity_appropriate": feedback.intensity_appropriate,
            "communication_effective": feedback.communication_effective,
            "recommendations_relevant": feedback.recommendations_relevant,
            "comments": feedback.comments,
            "timestamp": datetime.now().isoformat()
        }
        
        # Solo procesar si tenemos contexto y resultado válidos
        if context and result:
            await hybrid_engine.learning_engine.learn_from_interaction(
                context=context,
                result=result,
                user_feedback=feedback_data
            )
        
        # Almacenar feedback independientemente
        await state_manager.store_state(
            f"feedback_{user_id}_{feedback.session_id}_{datetime.now().timestamp()}",
            feedback_data,
            ttl=86400  # 24 horas
        )
        
        logger.info(f"Feedback processed for user {user_id}")
        
        return FeedbackResponse(
            success=True,
            message="Feedback recibido exitosamente",
            feedback_id=f"{user_id}_{feedback.session_id}_{datetime.now().timestamp()}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando feedback: {str(e)}"
        )


@router.get("/user/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str = Path(..., description="ID del usuario"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    state_manager: StateManager = Depends(get_state_manager)
) -> UserProfileResponse:
    """
    Obtiene el perfil de personalización de un usuario.
    
    Args:
        user_id: ID del usuario
        current_user: Usuario autenticado
        state_manager: Gestor de estado
        
    Returns:
        Perfil completo del usuario
        
    Raises:
        HTTPException: Error al obtener perfil
    """
    try:
        # Verificar autorización
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para ver perfil de otro usuario"
            )
        
        logger.info(f"Getting profile for user {user_id}")
        
        # Intentar obtener perfil desde estado
        profile_data = await state_manager.get_state(f"user_profile_{user_id}")
        
        if not profile_data:
            # Crear perfil básico si no existe
            profile_data = {
                "user_id": user_id,
                "archetype": "prime",  # Default
                "age": 30,
                "gender": "unknown",
                "fitness_level": "intermediate",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            # Almacenar perfil básico
            await state_manager.store_state(f"user_profile_{user_id}", profile_data)
        
        return UserProfileResponse(
            success=True,
            profile=profile_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo perfil: {str(e)}"
        )


@router.put("/user/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: str = Path(..., description="ID del usuario"),
    profile_update: UserProfileRequest = Body(..., description="Datos de actualización del perfil"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    state_manager: StateManager = Depends(get_state_manager)
) -> UserProfileResponse:
    """
    Actualiza el perfil de personalización de un usuario.
    
    Args:
        user_id: ID del usuario
        profile_update: Datos de actualización
        current_user: Usuario autenticado
        state_manager: Gestor de estado
        
    Returns:
        Perfil actualizado
        
    Raises:
        HTTPException: Error al actualizar perfil
    """
    try:
        # Verificar autorización
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para actualizar perfil de otro usuario"
            )
        
        logger.info(f"Updating profile for user {user_id}")
        
        # Obtener perfil existente
        existing_profile = await state_manager.get_state(f"user_profile_{user_id}") or {}
        
        # Actualizar campos proporcionados
        updated_profile = {**existing_profile}
        update_data = profile_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            if value is not None:
                updated_profile[key] = value
        
        updated_profile["last_updated"] = datetime.now().isoformat()
        updated_profile["user_id"] = user_id
        
        # Almacenar perfil actualizado
        await state_manager.store_state(f"user_profile_{user_id}", updated_profile)
        
        logger.info(f"Profile updated for user {user_id}")
        
        return UserProfileResponse(
            success=True,
            profile=updated_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando perfil: {str(e)}"
        )


@router.get("/archetypes", response_model=ArchetypesResponse)
async def get_archetypes() -> ArchetypesResponse:
    """
    Obtiene información sobre los arquetipos disponibles (PRIME/LONGEVITY).
    
    Returns:
        Información detallada de arquetipos
    """
    try:
        archetypes_info = {
            "prime": {
                "name": "PRIME",
                "description": "Optimizadores que buscan rendimiento, eficiencia y ventaja competitiva",
                "characteristics": [
                    "Enfoque en rendimiento",
                    "Orientado a resultados",
                    "Busca eficiencia temporal",
                    "Motivado por competición",
                    "Prefiere métricas avanzadas"
                ],
                "communication_style": "Directo y orientado a datos",
                "training_approach": "Alta intensidad con optimización",
                "content_preferences": ["métricas de rendimiento", "benchmarks", "análisis avanzados"],
                "ideal_for": ["Atletas", "Ejecutivos", "Personas orientadas a metas"]
            },
            "longevity": {
                "name": "LONGEVITY",
                "description": "Arquitectos de vida enfocados en prevención, bienestar y sostenibilidad",
                "characteristics": [
                    "Enfoque en sostenibilidad",
                    "Orientado a procesos",
                    "Busca bienestar integral",
                    "Motivado por salud",
                    "Prefiere educación comprensiva"
                ],
                "communication_style": "Educativo y de apoyo",
                "training_approach": "Intensidad moderada con énfasis en seguridad",
                "content_preferences": ["educación", "beneficios a largo plazo", "prevención"],
                "ideal_for": ["Personas maduras", "Enfoque wellness", "Rehabilitación"]
            }
        }
        
        return ArchetypesResponse(
            success=True,
            archetypes=archetypes_info
        )
        
    except Exception as e:
        logger.error(f"Error getting archetypes info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información de arquetipos: {str(e)}"
        )


@router.post("/user/{user_id}/biometrics", response_model=Dict[str, Any])
async def update_user_biometrics(
    user_id: str = Path(..., description="ID del usuario"),
    biometrics: BiometricsUpdateRequest = Body(..., description="Datos biométricos"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    state_manager: StateManager = Depends(get_state_manager)
) -> Dict[str, Any]:
    """
    Actualiza datos biométricos del usuario para personalización en tiempo real.
    
    Args:
        user_id: ID del usuario
        biometrics: Datos biométricos actualizados
        current_user: Usuario autenticado
        state_manager: Gestor de estado
        
    Returns:
        Confirmación de actualización
    """
    try:
        # Verificar autorización
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para actualizar biométricos de otro usuario"
            )
        
        logger.info(f"Updating biometrics for user {user_id}")
        
        # Almacenar datos biométricos con timestamp
        biometrics_data = biometrics.dict()
        biometrics_data["timestamp"] = datetime.now().isoformat()
        biometrics_data["user_id"] = user_id
        
        # Almacenar en estado
        await state_manager.store_state(
            f"biometrics_{user_id}_{datetime.now().timestamp()}",
            biometrics_data,
            ttl=86400  # 24 horas
        )
        
        # Actualizar perfil del usuario con biométricos más recientes
        profile_key = f"user_profile_{user_id}"
        profile = await state_manager.get_state(profile_key) or {}
        profile["biometrics"] = biometrics_data
        profile["last_updated"] = datetime.now().isoformat()
        
        await state_manager.store_state(profile_key, profile)
        
        return {
            "success": True,
            "message": "Datos biométricos actualizados exitosamente",
            "timestamp": biometrics_data["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating biometrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando biométricos: {str(e)}"
        )


@router.post("/user/{user_id}/workout", response_model=Dict[str, Any])
async def submit_workout_data(
    user_id: str = Path(..., description="ID del usuario"),
    workout: WorkoutSubmissionRequest = Body(..., description="Datos del entrenamiento"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    state_manager: StateManager = Depends(get_state_manager)
) -> Dict[str, Any]:
    """
    Submite datos de entrenamiento para análisis y personalización futura.
    
    Args:
        user_id: ID del usuario
        workout: Datos del entrenamiento
        current_user: Usuario autenticado
        state_manager: Gestor de estado
        
    Returns:
        Confirmación de almacenamiento
    """
    try:
        # Verificar autorización
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para enviar datos de entrenamiento por otro usuario"
            )
        
        logger.info(f"Receiving workout data from user {user_id}")
        
        # Procesar datos del entrenamiento
        workout_data = workout.dict()
        workout_data["user_id"] = user_id
        workout_data["submitted_at"] = datetime.now().isoformat()
        
        # Almacenar entrenamiento
        workout_id = f"workout_{user_id}_{datetime.now().timestamp()}"
        await state_manager.store_state(
            workout_id,
            workout_data,
            ttl=604800  # 7 días
        )
        
        # Actualizar historial de entrenamientos en perfil
        profile_key = f"user_profile_{user_id}"
        profile = await state_manager.get_state(profile_key) or {}
        
        if "recent_workouts" not in profile:
            profile["recent_workouts"] = []
        
        profile["recent_workouts"].append(workout_data)
        
        # Mantener solo los últimos 30 entrenamientos
        profile["recent_workouts"] = profile["recent_workouts"][-30:]
        profile["last_updated"] = datetime.now().isoformat()
        
        await state_manager.store_state(profile_key, profile)
        
        return {
            "success": True,
            "message": "Datos de entrenamiento almacenados exitosamente",
            "workout_id": workout_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing workout data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error almacenando datos de entrenamiento: {str(e)}"
        )


@router.get("/user/{user_id}/history", response_model=PersonalizationHistoryResponse)
async def get_personalization_history(
    user_id: str = Path(..., description="ID del usuario"),
    limit: int = 10,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    state_manager: StateManager = Depends(get_state_manager)
) -> PersonalizationHistoryResponse:
    """
    Obtiene el historial de personalizaciones de un usuario.
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de resultados
        offset: Offset para paginación
        current_user: Usuario autenticado
        state_manager: Gestor de estado
        
    Returns:
        Historial de personalizaciones
    """
    try:
        # Verificar autorización
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para ver historial de otro usuario"
            )
        
        logger.info(f"Getting personalization history for user {user_id}")
        
        # Obtener claves de personalización del usuario
        # En una implementación real, usaríamos una base de datos con índices
        # Aquí simulamos obteniendo datos del state manager
        
        history_data = []
        
        # Esta sería la lógica para obtener historial real
        # Por ahora retornamos estructura vacía
        
        return PersonalizationHistoryResponse(
            success=True,
            history=history_data,
            total_count=len(history_data),
            limit=limit,
            offset=offset
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting personalization history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo historial: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, Any])
async def health_check(
    hybrid_engine: HybridIntelligenceEngine = Depends(get_hybrid_engine)
) -> Dict[str, Any]:
    """
    Health check para el sistema de Hybrid Intelligence.
    
    Returns:
        Estado del sistema
    """
    try:
        # Verificar que el engine esté funcionando
        test_profile = UserProfile(
            user_id="health_check",
            archetype=UserArchetype.PRIME,
            age=30,
            gender="test"
        )
        
        test_context = PersonalizationContext(
            user_profile=test_profile,
            agent_type="test",
            request_type="health_check",
            request_content="System health check"
        )
        
        # Test básico de funcionalidad
        result = await hybrid_engine.personalize_for_user(test_context, PersonalizationMode.BASIC)
        
        return {
            "status": "healthy",
            "service": "hybrid-intelligence",
            "version": "1.0.0",
            "engine_status": "operational",
            "test_confidence": result.confidence_score,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "hybrid-intelligence",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }