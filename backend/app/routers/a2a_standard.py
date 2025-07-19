"""
Router de endpoints estándar A2A según especificación de Google ADK.

Este módulo implementa los endpoints requeridos por el protocolo A2A v0.2
para descubrimiento y ejecución de agentes.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from core.logging_config import get_logger
from core.auth import get_optional_user
from infrastructure.a2a_server import A2AServer
from app.schemas.auth import User

logger = get_logger(__name__)

# Crear router
router = APIRouter(
    tags=["A2A Standard"],
    responses={
        404: {"description": "Agent not found"},
        500: {"description": "Internal server error"},
    },
)

# Esquemas según especificación A2A v0.2
class RunRequest(BaseModel):
    """Esquema de solicitud para ejecutar un agente."""
    messages: List[Dict[str, Any]] = Field(
        ..., 
        description="Lista de mensajes en formato JSON-RPC con roles y contenido"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto adicional para la ejecución"
    )
    stream: Optional[bool] = Field(
        default=False,
        description="Si true, retorna respuestas en streaming"
    )

class RunResponse(BaseModel):
    """Esquema de respuesta de ejecución de agente."""
    messages: List[Dict[str, Any]] = Field(
        ..., 
        description="Respuestas del agente en formato JSON-RPC"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadatos adicionales de la ejecución"
    )

class AgentCard(BaseModel):
    """Agent Card según especificación A2A."""
    name: str
    description: str
    version: str = "1.0.0"
    capabilities: List[str]
    auth: Dict[str, Any] = {"type": "none"}
    endpoints: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None

class AgentDiscovery(BaseModel):
    """Respuesta de descubrimiento de agentes."""
    version: str = "1.0"
    agents: List[AgentCard]
    server_info: Dict[str, Any]


@router.get("/.well-known/agent.json", response_model=AgentDiscovery)
async def get_agent_discovery() -> AgentDiscovery:
    """
    Endpoint de descubrimiento de agentes según estándar A2A.
    
    Returns:
        AgentDiscovery: Información de todos los agentes disponibles
    """
    try:
        # Obtener instancia del servidor A2A
        a2a_server = A2AServer()
        
        # Construir lista de agent cards
        agent_cards = []
        
        # Definir los agentes disponibles
        agents_info = [
            {
                "id": "nexus_orchestrator",
                "name": "NEXUS - Master Orchestrator",
                "description": "Central coordinator for multi-agent collaboration",
                "capabilities": ["orchestration", "routing", "synthesis", "vision", "multimodal"]
            },
            {
                "id": "blaze_elite_training",
                "name": "BLAZE - Elite Training Strategist",
                "description": "Personalized training program specialist",
                "capabilities": ["training", "fitness", "performance", "adaptation"]
            },
            {
                "id": "sage_nutrition_architect",
                "name": "SAGE - Precision Nutrition Architect",
                "description": "Advanced nutrition planning and optimization",
                "capabilities": ["nutrition", "meal_planning", "supplementation", "dietary_analysis"]
            },
            {
                "id": "stella_progress_tracker",
                "name": "STELLA - Progress Tracker",
                "description": "Comprehensive progress monitoring and insights",
                "capabilities": ["tracking", "analytics", "visualization", "reporting"]
            },
            {
                "id": "luna_female_wellness",
                "name": "LUNA - Female Wellness Coach",
                "description": "Female-specific health and wellness specialist",
                "capabilities": ["female_health", "hormonal_wellness", "cycle_optimization"]
            },
            {
                "id": "spark_motivation_coach",
                "name": "SPARK - Motivation & Behavior Coach",
                "description": "Behavioral psychology and motivation specialist",
                "capabilities": ["motivation", "behavior_change", "habit_formation", "psychology"]
            },
            {
                "id": "nova_biohacking",
                "name": "NOVA - Biohacking Innovator",
                "description": "Advanced optimization and biohacking strategies",
                "capabilities": ["biohacking", "optimization", "recovery", "performance_enhancement"]
            },
            {
                "id": "wave_performance_analytics",
                "name": "WAVE - Performance Analytics",
                "description": "Deep performance analysis and insights",
                "capabilities": ["analytics", "performance_metrics", "data_visualization", "insights"]
            },
            {
                "id": "code_genetic_specialist",
                "name": "CODE - Genetic Optimization Specialist",
                "description": "Genetic analysis and personalized recommendations",
                "capabilities": ["genetics", "dna_analysis", "personalization", "epigenetics"]
            },
            {
                "id": "guardian_security",
                "name": "GUARDIAN - Security & Compliance",
                "description": "Security, privacy, and compliance management",
                "capabilities": ["security", "compliance", "audit", "privacy"]
            },
            {
                "id": "node_integration",
                "name": "NODE - Systems Integration",
                "description": "External systems integration and data flow",
                "capabilities": ["integration", "api_management", "data_sync", "webhooks"]
            }
        ]
        
        # Crear agent cards
        for agent_info in agents_info:
            agent_card = AgentCard(
                name=agent_info["name"],
                description=agent_info["description"],
                version="1.0.0",
                capabilities=agent_info["capabilities"],
                auth={"type": "bearer", "scheme": "jwt"},
                endpoints={
                    "run": f"/agents/{agent_info['id']}/run",
                    "status": f"/agents/{agent_info['id']}/status",
                    "health": f"/agents/{agent_info['id']}/health"
                },
                metadata={
                    "agent_id": agent_info["id"],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            )
            agent_cards.append(agent_card)
        
        # Construir respuesta de descubrimiento
        discovery = AgentDiscovery(
            version="1.0",
            agents=agent_cards,
            server_info={
                "name": "NGX Agents A2A Server",
                "version": "1.0.0",
                "protocol": "a2a/0.2",
                "features": [
                    "multi-agent-orchestration",
                    "streaming-responses",
                    "vision-processing",
                    "multimodal-support"
                ],
                "contact": {
                    "email": "support@ngxagents.com",
                    "url": "https://ngxagents.com"
                }
            }
        )
        
        logger.info("Agent discovery endpoint called successfully")
        return discovery
        
    except Exception as e:
        logger.error(f"Error in agent discovery: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent information: {str(e)}"
        )


@router.post("/agents/{agent_id}/run", response_model=RunResponse)
async def run_agent(
    agent_id: str,
    request: RunRequest,
    current_user: Optional[User] = Depends(get_optional_user)
) -> RunResponse:
    """
    Ejecuta un agente específico según el estándar A2A.
    
    Args:
        agent_id: ID del agente a ejecutar
        request: Solicitud de ejecución con mensajes
        current_user: Usuario actual (opcional)
        
    Returns:
        RunResponse: Respuesta del agente
    """
    try:
        logger.info(f"Running agent {agent_id} with A2A standard endpoint")
        
        # Obtener servidor A2A
        a2a_server = A2AServer()
        
        # Verificar que el agente existe
        if agent_id not in a2a_server.agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found"
            )
        
        # Extraer el mensaje principal de la solicitud
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail="No messages provided in request"
            )
        
        # Convertir mensajes al formato interno
        # Los mensajes A2A tienen formato: {"role": "user", "content": [{"text": "..."}]}
        user_message = ""
        for msg in request.messages:
            if msg.get("role") == "user":
                content = msg.get("content", [])
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        user_message += part["text"] + " "
                    elif isinstance(part, str):
                        user_message += part + " "
        
        user_message = user_message.strip()
        
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No user message found in request"
            )
        
        # Preparar contexto
        context = request.context or {}
        if current_user:
            context["user_id"] = current_user.id
            context["user_profile"] = {
                "email": current_user.email,
                "name": getattr(current_user, "name", None)
            }
        
        # Enviar mensaje al agente
        response = await a2a_server.send_message(
            agent_id=agent_id,
            message={
                "type": "user_message",
                "content": user_message,
                "context": context
            }
        )
        
        # Formatear respuesta según estándar A2A
        response_messages = []
        
        if response.get("success") and response.get("response"):
            agent_response = response["response"]
            
            # Crear mensaje de respuesta en formato A2A
            response_message = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": agent_response.get("content", "")
                    }
                ]
            }
            
            # Agregar contenido adicional si existe
            if agent_response.get("data"):
                response_message["content"].append({
                    "type": "data",
                    "data": agent_response["data"]
                })
            
            response_messages.append(response_message)
        else:
            # Error en la respuesta
            error_msg = response.get("error", "Unknown error occurred")
            response_messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {error_msg}"
                    }
                ]
            })
        
        # Construir respuesta final
        run_response = RunResponse(
            messages=response_messages,
            metadata={
                "agent_id": agent_id,
                "execution_time": response.get("execution_time", 0),
                "tokens_used": response.get("tokens_used", 0),
                "confidence": response.get("confidence", 0.0)
            }
        )
        
        logger.info(f"Agent {agent_id} executed successfully via A2A endpoint")
        return run_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running agent {agent_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing agent: {str(e)}"
        )


@router.get("/agents/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
) -> Dict[str, Any]:
    """
    Obtiene el estado actual de un agente.
    
    Args:
        agent_id: ID del agente
        current_user: Usuario actual (opcional)
        
    Returns:
        Dict con el estado del agente
    """
    try:
        a2a_server = A2AServer()
        
        if agent_id not in a2a_server.agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found"
            )
        
        # Obtener estado del agente
        agent = a2a_server.agents[agent_id]
        
        status = {
            "agent_id": agent_id,
            "status": "active" if agent else "inactive",
            "last_activity": a2a_server.agent_last_activity.get(agent_id),
            "metrics": {
                "total_requests": 0,  # TODO: Implementar métricas reales
                "average_response_time": 0,
                "success_rate": 100
            }
        }
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent status: {str(e)}"
        )