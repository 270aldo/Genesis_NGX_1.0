"""
Dependencias comunes para la aplicación FastAPI.

Este módulo centraliza todas las dependencias reutilizables
que se usan en múltiples endpoints.
"""

from typing import Optional, Dict, Any, Annotated
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Header, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.logging_config import get_logger
from core.settings_lazy import settings
from clients.supabase_client import get_supabase_client
from clients.vertex_ai.client import get_vertex_ai_client
from core.redis_manager import get_redis_pool
from app.auth import get_current_user, verify_token

logger = get_logger(__name__)

# Security scheme para Bearer tokens
security = HTTPBearer()


# =============================================================================
# DEPENDENCIAS DE AUTENTICACIÓN
# =============================================================================

async def get_authenticated_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> Dict[str, Any]:
    """
    Obtiene el usuario autenticado desde el token.
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        Información del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido
    """
    token = credentials.credentials
    
    try:
        user = await verify_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """
    Obtiene el usuario si está autenticado (opcional).
    
    Args:
        authorization: Header de autorización opcional
        
    Returns:
        Información del usuario o None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    
    try:
        return await verify_token(token)
    except Exception:
        return None


# =============================================================================
# DEPENDENCIAS DE CLIENTES
# =============================================================================

async def get_supabase():
    """
    Obtiene el cliente de Supabase.
    
    Returns:
        Cliente de Supabase configurado
    """
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )
    return client


async def get_vertex_ai():
    """
    Obtiene el cliente de Vertex AI.
    
    Returns:
        Cliente de Vertex AI configurado
    """
    client = get_vertex_ai_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable"
        )
    return client


async def get_redis():
    """
    Obtiene el pool de Redis.
    
    Returns:
        Pool de conexiones Redis
    """
    pool = await get_redis_pool()
    if not pool:
        logger.warning("Redis no disponible, continuando sin caché")
    return pool


# =============================================================================
# DEPENDENCIAS DE REQUEST
# =============================================================================

def get_request_id(request: Request) -> str:
    """
    Obtiene el ID único del request actual.
    
    Args:
        request: Request actual
        
    Returns:
        Request ID
    """
    return getattr(request.state, 'request_id', 'unknown')


def get_client_ip(request: Request) -> str:
    """
    Obtiene la IP del cliente.
    
    Args:
        request: Request actual
        
    Returns:
        Dirección IP del cliente
    """
    # Intentar obtener la IP real si está detrás de un proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


# =============================================================================
# DEPENDENCIAS DE PAGINACIÓN
# =============================================================================

class PaginationParams:
    """Parámetros de paginación comunes."""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(
            20, 
            ge=1, 
            le=100, 
            description="Elementos por página"
        ),
        sort_by: Optional[str] = Query(
            None, 
            description="Campo para ordenar"
        ),
        sort_order: str = Query(
            "desc", 
            pattern="^(asc|desc)$",
            description="Orden de clasificación"
        )
    ):
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order
        
        # Calcular offset para queries
        self.offset = (page - 1) * page_size
        self.limit = page_size
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset,
            "limit": self.limit,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order
        }


# =============================================================================
# DEPENDENCIAS DE VALIDACIÓN
# =============================================================================

def validate_agent_id(agent_id: str) -> str:
    """
    Valida que el agent_id sea válido.
    
    Args:
        agent_id: ID del agente
        
    Returns:
        agent_id validado
        
    Raises:
        HTTPException: Si el agent_id no es válido
    """
    valid_agents = [
        "nexus_orchestrator",
        "blaze_trainer", 
        "sage_nutritionist",
        "code_genetic",
        "wave_analytics",
        "luna_wellness",
        "stella_progress",
        "spark_motivation",
        "nova_biohacking",
        "guardian_security",
        "node_integration"
    ]
    
    if agent_id not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent_id. Must be one of: {valid_agents}"
        )
    
    return agent_id


def validate_program_type(program_type: str) -> str:
    """
    Valida el tipo de programa.
    
    Args:
        program_type: Tipo de programa
        
    Returns:
        program_type validado
        
    Raises:
        HTTPException: Si el tipo no es válido
    """
    valid_types = ["PRIME", "LONGEVITY", "GENERAL"]
    
    program_type_upper = program_type.upper()
    
    if program_type_upper not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid program_type. Must be one of: {valid_types}"
        )
    
    return program_type_upper


# =============================================================================
# DEPENDENCIAS DE CONTEXTO
# =============================================================================

class RequestContext:
    """Contexto del request actual con información útil."""
    
    def __init__(
        self,
        request: Request,
        user: Optional[Dict[str, Any]] = Depends(get_optional_user),
        request_id: str = Depends(get_request_id),
        client_ip: str = Depends(get_client_ip)
    ):
        self.request = request
        self.user = user
        self.request_id = request_id
        self.client_ip = client_ip
        self.timestamp = datetime.now(timezone.utc)
        
        # Agregar información adicional si está disponible
        self.user_id = user.get("id") if user else None
        self.user_email = user.get("email") if user else None
        self.is_authenticated = user is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el contexto a diccionario."""
        return {
            "request_id": self.request_id,
            "client_ip": self.client_ip,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "is_authenticated": self.is_authenticated,
            "timestamp": self.timestamp.isoformat()
        }