"""
Conversation Memory API Router - FASE 12 POINT 1
===============================================

API endpoints para el sistema de memoria conversacional inteligente.
Proporciona acceso REST a todas las funcionalidades de memoria, sesiones y búsqueda.

ENDPOINTS PRINCIPALES:
- Gestión de memoria conversacional
- Administración de sesiones
- Búsqueda semántica avanzada
- Analíticas y estadísticas
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from core.conversation_memory import (
    init_conversation_memory,
    store_user_conversation,
    get_user_conversation_history,
    get_user_personality,
    ConversationContext,
    EmotionalState,
    MemoryEntry,
    PersonalityProfile,
    conversation_memory
)
from core.session_manager import (
    init_session_manager,
    create_user_session,
    get_user_session,
    update_user_session_activity,
    SessionInfo,
    DeviceType,
    session_manager
)
from core.memory_search import (
    search_user_memories,
    find_similar_conversations,
    get_memory_search_suggestions,
    SearchFilter,
    SearchScope,
    SortOrder,
    SearchResult,
    memory_search
)
from core.logging_config import get_logger
from app.schemas.pagination import PaginationParams, PaginatedResponse
from core.pagination_helpers import apply_pagination_to_dict_list

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/memory", tags=["conversation-memory"])


# Modelos Pydantic para requests/responses
class StoreConversationRequest(BaseModel):
    """Request para almacenar conversación"""
    user_id: str = Field(..., description="ID del usuario")
    agent_id: str = Field(..., description="ID del agente")
    content: str = Field(..., description="Contenido de la conversación")
    context: ConversationContext = Field(..., description="Contexto conversacional")
    emotional_state: Optional[EmotionalState] = Field(None, description="Estado emocional")
    session_id: Optional[str] = Field(None, description="ID de la sesión")
    importance_score: float = Field(0.5, ge=0.0, le=1.0, description="Score de importancia")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata adicional")


class StoreConversationResponse(BaseModel):
    """Response para almacenar conversación"""
    memory_id: str = Field(..., description="ID de la entrada de memoria creada")
    success: bool = Field(..., description="Indica si se almacenó exitosamente")
    message: str = Field(..., description="Mensaje descriptivo")


class ConversationHistoryRequest(BaseModel):
    """Request para obtener historial"""
    user_id: str = Field(..., description="ID del usuario")
    agent_id: Optional[str] = Field(None, description="Filtrar por agente específico")
    context: Optional[ConversationContext] = Field(None, description="Filtrar por contexto")
    limit: int = Field(50, ge=1, le=200, description="Máximo número de entradas")


class CreateSessionRequest(BaseModel):
    """Request para crear sesión"""
    user_id: str = Field(..., description="ID del usuario")
    device_id: str = Field(..., description="ID único del dispositivo")
    device_type: DeviceType = Field(DeviceType.UNKNOWN, description="Tipo de dispositivo")
    initial_context: Optional[Dict[str, Any]] = Field(None, description="Contexto inicial")


class UpdateSessionRequest(BaseModel):
    """Request para actualizar sesión"""
    session_id: str = Field(..., description="ID de la sesión")
    agent_id: Optional[str] = Field(None, description="Agente activo")
    context_update: Optional[Dict[str, Any]] = Field(None, description="Actualización de contexto")
    emotional_state: Optional[EmotionalState] = Field(None, description="Estado emocional")


class SearchMemoriesRequest(BaseModel):
    """Request para búsqueda de memorias"""
    user_id: str = Field(..., description="ID del usuario")
    query: str = Field(..., min_length=1, description="Texto de búsqueda")
    agent_ids: Optional[List[str]] = Field(None, description="Filtrar por agentes")
    contexts: Optional[List[ConversationContext]] = Field(None, description="Filtrar por contextos")
    emotional_states: Optional[List[EmotionalState]] = Field(None, description="Filtrar por estados emocionales")
    min_importance: Optional[float] = Field(None, ge=0.0, le=1.0, description="Importancia mínima")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    session_id: Optional[str] = Field(None, description="Filtrar por sesión")
    scope: SearchScope = Field(SearchScope.ALL, description="Alcance temporal")
    sort_order: SortOrder = Field(SortOrder.MIXED, description="Orden de resultados")
    limit: int = Field(20, ge=1, le=100, description="Máximo número de resultados")


# Dependency para inicialización
async def ensure_memory_initialized():
    """Asegura que el sistema de memoria esté inicializado"""
    try:
        await init_conversation_memory()
        await init_session_manager()
    except Exception as e:
        logger.error(f"Error inicializando sistema de memoria: {e}")
        raise HTTPException(status_code=500, detail="Error interno del sistema de memoria")


# ENDPOINTS DE MEMORIA CONVERSACIONAL

@router.post("/conversations", response_model=StoreConversationResponse)
async def store_conversation(
    request: StoreConversationRequest,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Almacena una nueva entrada de conversación en el sistema de memoria
    
    Este endpoint permite registrar interacciones entre usuarios y agentes,
    incluyendo contexto emocional y metadata relevante.
    """
    try:
        memory_id = await store_user_conversation(
            user_id=request.user_id,
            agent_id=request.agent_id,
            content=request.content,
            context=request.context,
            emotional_state=request.emotional_state,
            session_id=request.session_id,
            metadata=request.metadata
        )
        
        return StoreConversationResponse(
            memory_id=memory_id,
            success=True,
            message="Conversación almacenada exitosamente"
        )
        
    except Exception as e:
        logger.error(f"Error almacenando conversación: {e}")
        raise HTTPException(status_code=500, detail=f"Error almacenando conversación: {str(e)}")


@router.get("/conversations/{user_id}", response_model=PaginatedResponse[Dict[str, Any]])
async def get_conversation_history(
    user_id: str,
    request: Request,
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items por página"),
    sort_by: str = Query(default="timestamp", description="Campo para ordenar"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Orden"),
    agent_id: Optional[str] = Query(None, description="Filtrar por agente específico"),
    context: Optional[ConversationContext] = Query(None, description="Filtrar por contexto"),
    _: None = Depends(ensure_memory_initialized)
):
    """
    Obtiene el historial de conversaciones de un usuario con paginación.
    
    Permite filtrar por agente específico, contexto conversacional y paginar resultados.
    Las conversaciones se devuelven ordenadas por fecha (más recientes primero por defecto).
    """
    try:
        # Crear parámetros de paginación
        pagination_params = PaginationParams(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Obtener todas las memorias (sin límite, la paginación se aplicará después)
        memories = await get_user_conversation_history(
            user_id=user_id,
            agent_id=agent_id,
            context=context,
            limit=1000  # Límite alto para obtener todos los registros
        )
        
        # Convertir a diccionarios para respuesta JSON
        memory_dicts = [memory.to_dict() for memory in memories]
        
        # Aplicar paginación
        base_url = str(request.url).split('?')[0]
        paginated_response = apply_pagination_to_dict_list(
            items=memory_dicts,
            params=pagination_params,
            base_url=base_url,
            sort_key=sort_by
        )
        
        logger.info(
            f"Historial de conversaciones obtenido para usuario {user_id} "
            f"(página {page}, tamaño {page_size})"
        )
        
        return paginated_response
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")


@router.get("/personality/{user_id}")
async def get_personality_profile(
    user_id: str,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Obtiene el perfil de personalidad aprendido de un usuario
    
    El perfil incluye patrones de comunicación, tópicos preferidos,
    triggers de motivación y score de confianza del análisis.
    """
    try:
        profile = await get_user_personality(user_id)
        
        if not profile:
            return {
                "user_id": user_id,
                "profile_exists": False,
                "message": "Perfil de personalidad no encontrado. Se creará automáticamente con más interacciones."
            }
        
        return {
            "user_id": user_id,
            "profile_exists": True,
            "profile": profile.to_dict(),
            "last_updated": profile.last_updated.isoformat(),
            "confidence_score": profile.confidence_score
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil de personalidad: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo perfil: {str(e)}")


@router.get("/stats/{user_id}")
async def get_memory_statistics(
    user_id: str,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Obtiene estadísticas detalladas de memoria para un usuario
    
    Incluye conteos totales, memorias recientes, utilización del sistema
    y métricas de confianza del perfil de personalidad.
    """
    try:
        stats = await conversation_memory.get_memory_stats(user_id)
        
        return {
            "user_id": user_id,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


# ENDPOINTS DE GESTIÓN DE SESIONES

@router.post("/sessions", response_model=Dict[str, Any])
async def create_session(
    request: CreateSessionRequest,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Crea una nueva sesión conversacional para un usuario
    
    Las sesiones permiten mantener contexto persistente y sincronización
    cross-device para una experiencia de usuario continua.
    """
    try:
        session_info = await create_user_session(
            user_id=request.user_id,
            device_id=request.device_id,
            device_type=request.device_type,
            initial_context=request.initial_context
        )
        
        return {
            "success": True,
            "session": session_info.to_dict(),
            "message": "Sesión creada exitosamente"
        }
        
    except Exception as e:
        logger.error(f"Error creando sesión: {e}")
        raise HTTPException(status_code=500, detail=f"Error creando sesión: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Obtiene información detallada de una sesión específica
    
    Incluye estado actual, contexto conversacional, dispositivo
    y estadísticas de actividad.
    """
    try:
        session_info = await get_user_session(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        return {
            "session": session_info.to_dict(),
            "is_active": session_info.status.value == "active",
            "time_until_expiry": (
                session_info.expires_at - datetime.utcnow()
            ).total_seconds() if session_info.expires_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo sesión: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sesión: {str(e)}")


@router.put("/sessions/activity")
async def update_session_activity(
    request: UpdateSessionRequest,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Actualiza la actividad de una sesión existente
    
    Registra interacción del usuario, actualiza contexto conversacional
    y extiende automáticamente la expiración si es necesario.
    """
    try:
        success = await update_user_session_activity(
            session_id=request.session_id,
            agent_id=request.agent_id,
            context_update=request.context_update,
            emotional_state=request.emotional_state
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Sesión no encontrada o expirada")
        
        return {
            "success": True,
            "message": "Actividad de sesión actualizada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando actividad: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando actividad: {str(e)}")


@router.get("/sessions/user/{user_id}")
async def get_user_sessions(
    user_id: str,
    include_inactive: bool = Query(False, description="Incluir sesiones inactivas"),
    _: None = Depends(ensure_memory_initialized)
):
    """
    Obtiene todas las sesiones de un usuario específico
    
    Permite visualizar sesiones activas e inactivas para gestión
    multi-dispositivo y recuperación de sesiones.
    """
    try:
        sessions = await session_manager.get_user_sessions(
            user_id=user_id,
            include_inactive=include_inactive
        )
        
        session_dicts = [session.to_dict() for session in sessions]
        
        return {
            "user_id": user_id,
            "total_sessions": len(session_dicts),
            "sessions": session_dicts,
            "include_inactive": include_inactive
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo sesiones de usuario: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sesiones: {str(e)}")


@router.post("/sessions/{session_id}/pause")
async def pause_session(
    session_id: str,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Pausa temporalmente una sesión activa
    
    La sesión puede ser reanudada posteriormente manteniendo
    todo el contexto conversacional.
    """
    try:
        success = await session_manager.pause_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        return {
            "success": True,
            "message": "Sesión pausada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausando sesión: {e}")
        raise HTTPException(status_code=500, detail=f"Error pausando sesión: {str(e)}")


@router.post("/sessions/{session_id}/resume")
async def resume_session(
    session_id: str,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Reanuda una sesión previamente pausada
    
    Reactiva la sesión y extiende automáticamente
    el tiempo de expiración.
    """
    try:
        success = await session_manager.resume_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Sesión no encontrada o no está pausada")
        
        return {
            "success": True,
            "message": "Sesión reanudada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reanudando sesión: {e}")
        raise HTTPException(status_code=500, detail=f"Error reanudando sesión: {str(e)}")


@router.delete("/sessions/{session_id}")
async def end_session(
    session_id: str,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Termina definitivamente una sesión
    
    La sesión se archiva y no puede ser reanudada.
    Se recomienda para logout explícito del usuario.
    """
    try:
        success = await session_manager.end_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        return {
            "success": True,
            "message": "Sesión terminada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminando sesión: {e}")
        raise HTTPException(status_code=500, detail=f"Error terminando sesión: {str(e)}")


# ENDPOINTS DE BÚSQUEDA SEMÁNTICA

@router.post("/search")
async def search_memories(
    request: SearchMemoriesRequest,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Realiza búsqueda semántica avanzada en las memorias del usuario
    
    Combina múltiples criterios de relevancia incluyendo coincidencias textuales,
    contexto conversacional, recencia y importancia de las memorias.
    """
    try:
        # Construir filtros de búsqueda
        filters = SearchFilter(
            agent_ids=request.agent_ids,
            contexts=request.contexts,
            emotional_states=request.emotional_states,
            min_importance=request.min_importance,
            date_from=request.date_from,
            date_to=request.date_to,
            session_id=request.session_id
        )
        
        # Realizar búsqueda
        results = await search_user_memories(
            user_id=request.user_id,
            query=request.query,
            filters=filters,
            limit=request.limit
        )
        
        # Convertir resultados a diccionarios
        result_dicts = [result.to_dict() for result in results]
        
        return {
            "query": request.query,
            "user_id": request.user_id,
            "total_results": len(result_dicts),
            "results": result_dicts,
            "search_parameters": {
                "scope": request.scope.value,
                "sort_order": request.sort_order.value,
                "filters_applied": filters.to_dict(),
                "limit": request.limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error en búsqueda de memorias: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")


@router.get("/search/suggestions/{user_id}")
async def get_search_suggestions(
    user_id: str,
    partial_query: str = Query(..., min_length=2, description="Consulta parcial para sugerencias"),
    limit: int = Query(5, ge=1, le=10, description="Máximo número de sugerencias"),
    _: None = Depends(ensure_memory_initialized)
):
    """
    Obtiene sugerencias inteligentes de búsqueda basadas en el historial del usuario
    
    Analiza conversaciones previas para sugerir términos relevantes
    que completen la consulta parcial del usuario.
    """
    try:
        suggestions = await get_memory_search_suggestions(
            user_id=user_id,
            partial_query=partial_query
        )
        
        return {
            "user_id": user_id,
            "partial_query": partial_query,
            "suggestions": suggestions[:limit],
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sugerencias: {str(e)}")


@router.post("/search/similar")
async def find_similar_memories(
    memory_id: str = Body(..., description="ID de la memoria de referencia"),
    user_id: str = Body(..., description="ID del usuario"),
    limit: int = Body(10, ge=1, le=20, description="Máximo número de resultados"),
    _: None = Depends(ensure_memory_initialized)
):
    """
    Encuentra memorias similares a una conversación de referencia
    
    Utiliza análisis semántico para identificar conversaciones relacionadas
    por contenido, contexto o patrones emocionales.
    """
    try:
        # Obtener la memoria de referencia
        user_memories = await get_user_conversation_history(user_id=user_id, limit=500)
        reference_memory = None
        
        for memory in user_memories:
            if memory.id == memory_id:
                reference_memory = memory
                break
        
        if not reference_memory:
            raise HTTPException(status_code=404, detail="Memoria de referencia no encontrada")
        
        # Buscar conversaciones similares
        similar_results = await find_similar_conversations(
            user_id=user_id,
            reference_memory=reference_memory,
            limit=limit
        )
        
        result_dicts = [result.to_dict() for result in similar_results]
        
        return {
            "reference_memory_id": memory_id,
            "user_id": user_id,
            "similar_memories": result_dicts,
            "total_found": len(result_dicts),
            "reference_context": reference_memory.context.value if reference_memory.context else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error buscando memorias similares: {e}")
        raise HTTPException(status_code=500, detail=f"Error buscando similares: {str(e)}")


@router.get("/search/analytics/{user_id}")
async def get_search_analytics(
    user_id: str,
    _: None = Depends(ensure_memory_initialized)
):
    """
    Obtiene analíticas de búsqueda y patrones conversacionales del usuario
    
    Incluye distribución de contextos, estados emocionales,
    términos más frecuentes y rangos temporales de memorias.
    """
    try:
        analytics = await memory_search.get_search_analytics(user_id)
        
        return {
            "user_id": user_id,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo analíticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo analíticas: {str(e)}")


# ENDPOINTS ADMINISTRATIVOS

@router.post("/maintenance/cleanup")
async def cleanup_old_memories(
    _: None = Depends(ensure_memory_initialized)
):
    """
    Ejecuta limpieza de memorias antiguas según políticas de retención
    
    Endpoint administrativo para mantenimiento del sistema.
    Requiere permisos especiales en producción.
    """
    try:
        cleaned_count = await conversation_memory.cleanup_old_memories()
        
        return {
            "success": True,
            "memories_cleaned": cleaned_count,
            "message": f"Limpieza completada: {cleaned_count} memorias antiguas removidas"
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza de memorias: {e}")
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")


@router.get("/system/status")
async def get_system_status(_: None = Depends(ensure_memory_initialized)):
    """
    Obtiene estado general del sistema de memoria conversacional
    
    Incluye estadísticas globales, rendimiento y estado de componentes.
    """
    try:
        memory_stats = {
            "memory_engine": "initialized",
            "session_manager": "initialized",
            "search_engine": "initialized"
        }
        
        # Estadísticas de sesiones
        session_stats = await session_manager.get_session_stats()
        
        return {
            "system_status": "healthy",
            "components": memory_stats,
            "session_statistics": session_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


# Agregar endpoints a startup para inicialización automática
@router.on_event("startup")
async def startup_memory_system():
    """Inicializa el sistema de memoria al arrancar la aplicación"""
    try:
        await ensure_memory_initialized()
        logger.info("Sistema de memoria conversacional inicializado exitosamente")
    except Exception as e:
        logger.error(f"Error inicializando sistema de memoria en startup: {e}")