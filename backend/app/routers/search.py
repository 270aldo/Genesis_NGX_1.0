"""
Router de búsqueda para NGX Agents.

Proporciona endpoints para búsqueda de texto completo en diferentes
tipos de contenido del sistema.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from core.search_manager import search_manager, SearchType
from core.logging_config import get_logger

logger = get_logger(__name__)

# Crear router
router = APIRouter(prefix="/search", tags=["search"])


# Schemas Pydantic
class SearchRequest(BaseModel):
    """Solicitud de búsqueda."""

    query: str = Field(..., min_length=1, max_length=200, description="Texto a buscar")
    search_type: SearchType = Field(
        default="all", description="Tipo de contenido a buscar"
    )
    limit: int = Field(
        default=20, ge=1, le=100, description="Número máximo de resultados"
    )
    offset: int = Field(default=0, ge=0, description="Desplazamiento para paginación")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Filtros adicionales"
    )


class SearchSuggestionRequest(BaseModel):
    """Solicitud de sugerencias de búsqueda."""

    partial_query: str = Field(
        ..., min_length=1, max_length=50, description="Texto parcial"
    )
    search_type: SearchType = Field(default="all", description="Tipo de contenido")
    limit: int = Field(default=5, ge=1, le=10, description="Número de sugerencias")


class SearchResult(BaseModel):
    """Resultado de búsqueda."""

    query: str
    search_type: str
    results: List[Dict[str, Any]]
    total_results: int
    limit: int
    offset: int
    timestamp: str


class SearchSuggestions(BaseModel):
    """Sugerencias de búsqueda."""

    partial_query: str
    suggestions: List[str]
    search_type: str


class SearchStats(BaseModel):
    """Estadísticas de búsqueda."""

    stats: Dict[str, Any]
    search_types_available: List[str]
    initialized: bool
    timestamp: str


@router.post("/", response_model=SearchResult)
async def search(
    request: SearchRequest, current_user: dict = Depends(get_current_user)
) -> SearchResult:
    """
    Realiza una búsqueda de texto completo.

    Busca en diferentes tipos de contenido según el search_type:
    - conversations: Historiales de conversación
    - training_plans: Planes de entrenamiento
    - nutrition_logs: Registros de nutrición
    - progress_metrics: Métricas de progreso
    - user_notes: Notas del usuario
    - all: Busca en todos los tipos
    """
    try:
        logger.info(
            f"Usuario {current_user['id']} buscando: '{request.query}' en {request.search_type}"
        )

        # Realizar búsqueda
        results = await search_manager.search(
            query=request.query,
            search_type=request.search_type,
            user_id=current_user["id"],
            limit=request.limit,
            offset=request.offset,
            filters=request.filters,
        )

        return SearchResult(**results)

    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al realizar búsqueda: {str(e)}"
        )


@router.get("/quick", response_model=SearchResult)
async def quick_search(
    q: str = Query(..., min_length=1, max_length=200, description="Texto a buscar"),
    type: SearchType = Query(default="all", description="Tipo de contenido"),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
) -> SearchResult:
    """
    Búsqueda rápida con parámetros de query.

    Endpoint simplificado para búsquedas rápidas desde la UI.
    """
    try:
        results = await search_manager.search(
            query=q, search_type=type, user_id=current_user["id"], limit=limit, offset=0
        )

        return SearchResult(**results)

    except Exception as e:
        logger.error(f"Error en búsqueda rápida: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al realizar búsqueda: {str(e)}"
        )


@router.post("/suggestions", response_model=SearchSuggestions)
async def get_suggestions(
    request: SearchSuggestionRequest, current_user: dict = Depends(get_current_user)
) -> SearchSuggestions:
    """
    Obtiene sugerencias de búsqueda para autocompletado.

    Retorna sugerencias basadas en el texto parcial ingresado.
    """
    try:
        suggestions = await search_manager.get_search_suggestions(
            partial_query=request.partial_query,
            search_type=request.search_type,
            user_id=current_user["id"],
            limit=request.limit,
        )

        return SearchSuggestions(
            partial_query=request.partial_query,
            suggestions=suggestions,
            search_type=request.search_type,
        )

    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener sugerencias: {str(e)}"
        )


@router.get("/types", response_model=List[str])
async def get_search_types() -> List[str]:
    """
    Obtiene los tipos de búsqueda disponibles.

    No requiere autenticación.
    """
    return [
        "all",
        "conversations",
        "training_plans",
        "nutrition_logs",
        "progress_metrics",
        "user_notes",
    ]


@router.get("/stats", response_model=SearchStats)
async def get_search_stats(
    current_user: dict = Depends(get_current_user),
) -> SearchStats:
    """
    Obtiene estadísticas del sistema de búsqueda.

    Solo disponible para usuarios con rol admin.
    """
    # Verificar permisos (simplificado, en producción usar un sistema de roles)
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")

    try:
        stats = await search_manager.get_stats()
        return SearchStats(**stats)

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.post("/reindex")
async def trigger_reindex(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Dispara la creación/actualización de índices de búsqueda.

    Solo disponible para usuarios con rol admin.
    Retorna las consultas SQL que deben ejecutarse en Supabase.
    """
    # Verificar permisos
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")

    try:
        sql_queries = await search_manager.create_search_indexes()

        return {
            "status": "success",
            "message": "Consultas SQL generadas. Ejecutar en Supabase Dashboard.",
            "queries": sql_queries,
        }

    except Exception as e:
        logger.error(f"Error generando índices: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al generar índices: {str(e)}"
        )
