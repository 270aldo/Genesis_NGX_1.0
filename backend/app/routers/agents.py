"""
Router de agentes para la API de NGX Agents.

Este módulo proporciona endpoints para interactuar con los agentes
del sistema NGX Agents.
"""

import importlib
import inspect
import os
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status

from agents.base.base_agent import BaseAgent
from agents.orchestrator.agent import NGXNexusOrchestrator
from app.schemas.agent import (
    AgentInfo,
    AgentRunRequest,
    AgentRunResponse,
)
from app.schemas.pagination import PaginatedResponse, PaginationParams
from core.auth import get_current_user
from core.logging_config import get_logger
from core.ngx_feature_flags import is_direct_agent_access_enabled, is_nexus_only_mode
from core.pagination_helpers import paginate_list
from core.settings_lazy import settings
from core.state_manager_optimized import StateManager
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from tools.mcp_toolkit import MCPToolkit

# Configurar logger
logger = get_logger(__name__)

# Crear router
router = APIRouter(
    prefix="/agents",
    tags=["agentes"],
    responses={401: {"description": "No autorizado"}},
)


def get_state_manager() -> StateManager:
    """
    Dependencia para obtener una instancia del StateManager.

    Returns:
        Instancia del StateManager
    """
    return state_manager_adapter


def discover_agents() -> Dict[str, BaseAgent]:
    """
    Descubre todos los agentes disponibles en el sistema.

    Returns:
        Diccionario con los agentes disponibles (agent_id -> instancia)
    """
    agents = {}
    agents_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agents"
    )

    # Excluir directorios y módulos que no son agentes
    exclude_dirs = ["__pycache__", "base"]

    # Preparar dependencias comunes
    try:
        sm_instance = get_state_manager()
        toolkit_instance = MCPToolkit()
        a2a_url = f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"
    except Exception as e:
        logger.error(
            f"Error al inicializar dependencias para discover_agents: {e}",
            exc_info=True,
        )
        # Si las dependencias fallan, no podemos instanciar agentes
        return agents

    # Recorrer todos los directorios en agents/
    for item in os.listdir(agents_path):
        item_path = os.path.join(agents_path, item)

        # Verificar si es un directorio y no está excluido
        if os.path.isdir(item_path) and item not in exclude_dirs:
            # Verificar si existe el archivo agent.py
            agent_file = os.path.join(item_path, "agent.py")
            if os.path.isfile(agent_file):
                try:
                    # Importar el módulo
                    module_name = f"agents.{item}.agent"
                    module = importlib.import_module(module_name)

                    # Buscar clases que heredan de BaseAgent
                    for name, obj_class in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj_class)
                            and issubclass(obj_class, BaseAgent)
                            and obj_class != BaseAgent
                        ):

                            # Preparar argumentos del constructor
                            constructor_args = {
                                "state_manager": sm_instance,
                                "mcp_toolkit": toolkit_instance,
                            }

                            # Si es el orquestador, añadir a2a_server_url
                            if obj_class == NGXNexusOrchestrator:
                                constructor_args["a2a_server_url"] = a2a_url
                                # Opcional: pasar un model_id específico si es necesario aquí
                                # constructor_args["model_id"] = settings.ORCHESTRATOR_DEFAULT_MODEL_ID

                            # Instanciar el agente con los argumentos preparados
                            agent_instance = obj_class(**constructor_args)
                            agents[agent_instance.agent_id] = agent_instance
                            logger.info(
                                f"Agente descubierto e instanciado: {agent_instance.agent_id} ({agent_instance.name})"
                            )

                except Exception as e:
                    logger.error(
                        f"Error al cargar o instanciar agente {item} ({module_name if 'module_name' in locals() else 'N/A'}): {e}",
                        exc_info=True,
                    )

    return agents


# Caché de agentes
_agents_cache: Dict[str, BaseAgent] = {}


def get_agents() -> Dict[str, BaseAgent]:
    """
    Obtiene todos los agentes disponibles (con caché).

    Returns:
        Diccionario con los agentes disponibles (agent_id -> instancia)
    """
    global _agents_cache

    if not _agents_cache:
        _agents_cache = discover_agents()

    return _agents_cache


def get_agent(agent_id: str) -> BaseAgent:
    """
    Obtiene un agente específico por su ID.

    Args:
        agent_id: ID del agente

    Returns:
        Instancia del agente

    Raises:
        HTTPException: Si el agente no existe
    """
    agents = get_agents()

    if agent_id not in agents:
        logger.warning(f"Agente no encontrado: {agent_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agente {agent_id} no encontrado",
        )

    return agents[agent_id]


@router.get("/", response_model=PaginatedResponse[AgentInfo])
async def list_agents(
    request: Request,
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items por página"),
    sort_by: str = Query(default="name", description="Campo para ordenar"),
    sort_order: str = Query(default="asc", regex="^(asc|desc)$", description="Orden"),
    user_id: str = Depends(get_current_user),
) -> PaginatedResponse[AgentInfo]:
    """
    Lista todos los agentes disponibles con paginación.

    Args:
        request: Request object para generar URLs
        page: Número de página (empieza en 1)
        page_size: Cantidad de items por página
        sort_by: Campo por el cual ordenar
        sort_order: Orden ascendente (asc) o descendente (desc)
        user_id: ID del usuario autenticado

    Returns:
        Lista paginada de agentes disponibles
    """
    # Crear parámetros de paginación
    pagination_params = PaginationParams(
        page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order
    )

    # Obtener todos los agentes
    agents = get_agents()

    # Convertir a lista de AgentInfo
    agent_list = [
        AgentInfo(
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            capabilities=agent.capabilities,
        )
        for agent in agents.values()
    ]

    # Aplicar paginación
    base_url = str(request.url).split("?")[0]
    paginated_response = paginate_list(
        items=agent_list, params=pagination_params, base_url=base_url
    )

    logger.info(
        f"Usuario {user_id} solicitó lista de agentes "
        f"(página {page}, tamaño {page_size})"
    )

    return paginated_response


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
async def run_agent(
    agent_id: str = Path(..., description="ID del agente a ejecutar"),
    request: AgentRunRequest = ...,
    user_id: str = Depends(get_current_user),
    state_manager: StateManager = Depends(get_state_manager),
) -> Dict[str, Any]:
    """
    Ejecuta un agente con un texto de entrada.

    IMPORTANTE: Con el nuevo modelo estratégico de NGX, los usuarios interactúan
    únicamente con NEXUS (el orquestador). Este endpoint redirige automáticamente
    a NEXUS cuando el modo NEXUS-only está activo.

    Args:
        agent_id: ID del agente a ejecutar
        request: Datos de la solicitud
        user_id: ID del usuario autenticado
        state_manager: Gestor de estados

    Returns:
        Respuesta del agente o redirección a NEXUS
    """
    # Check feature flags for NGX strategic pivot
    context = {"user_id": user_id}

    # If NEXUS-only mode is enabled and direct access is disabled
    if await is_nexus_only_mode(context) and not await is_direct_agent_access_enabled(
        context
    ):
        # Only allow direct access to NEXUS/orchestrator
        if agent_id not in ["nexus", "orchestrator", "ngx-nexus-orchestrator"]:
            logger.info(
                f"NEXUS-only mode active. Redirecting agent request from {agent_id} to NEXUS for user {user_id}"
            )

            # Option 1: Return a response indicating to use NEXUS
            return AgentRunResponse(
                agent_id="nexus",
                response=(
                    f"Hola, soy NEXUS, tu Director de Orquesta Personal. "
                    f"Veo que querías hablar con {agent_id}. "
                    f"Como tu coordinador principal, yo me encargaré de consultar "
                    f"con {agent_id} y con todo tu equipo de especialistas para darte "
                    f"la mejor respuesta. ¿En qué puedo ayudarte hoy?"
                ),
                session_id=request.session_id,
                metadata={
                    "redirected_from": agent_id,
                    "nexus_only_mode": True,
                    "message": "All interactions go through NEXUS in the new NGX model",
                },
            )

    # Legacy path: direct agent access (when feature flags allow it)
    # Obtener el agente
    agent = get_agent(agent_id)

    # Obtener o generar session_id
    session_id = request.session_id or None

    try:
        # Ejecutar el agente
        logger.info(f"Ejecutando agente {agent_id} para usuario {user_id}")

        result = await agent.run_async(
            input_text=request.input_text,
            user_id=user_id,
            session_id=session_id,
            context=request.context or {},
        )

        # Extraer session_id del resultado
        session_id = result.get("session_id", session_id)

        # Construir respuesta
        response = AgentRunResponse(
            agent_id=agent_id,
            response=result.get("response", ""),
            session_id=session_id,
            metadata=result.get("metadata", {}),
        )

        logger.info(f"Agente {agent_id} ejecutado correctamente para usuario {user_id}")

        return response

    except Exception as e:
        logger.error(f"Error al ejecutar agente {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al ejecutar agente: {str(e)}",
        )
