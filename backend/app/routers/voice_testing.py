"""
Router para testing de voces de agentes con ElevenLabs.

Este módulo proporciona endpoints para probar las implementaciones
de voz personalizada de todos los agentes NGX con ElevenLabs.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

from infrastructure.adapters.hybrid_voice_adapter import hybrid_voice_adapter
from clients.elevenlabs_client import elevenlabs_client

# Importar agentes con integración ElevenLabs
from agents.elite_training_strategist.agent import EliteTrainingStrategist
from agents.female_wellness_coach.agent import FemaleWellnessCoach
from agents.code_genetic_specialist.agent import CodeGeneticSpecialist

from core.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

# Crear router
router = APIRouter(prefix="/voice-testing", tags=["Voice Testing"])


# Esquemas de entrada
class VoiceTestRequest(BaseModel):
    """Solicitud para probar voz de agente."""

    agent_id: str
    text: str
    program_type: str = "PRIME"
    emotion_context: Optional[str] = "motivated"


class AgentVoicePreviewRequest(BaseModel):
    """Solicitud para preview de voz de agente."""

    agent_id: str
    sample_text: Optional[str] = None


class BulkVoiceTestRequest(BaseModel):
    """Solicitud para prueba masiva de voces."""

    test_text: str = (
        "Hola, soy tu agente NGX especializado. Estoy aquí para ayudarte a alcanzar tu mejor versión."
    )
    program_type: str = "PRIME"
    agents_to_test: Optional[List[str]] = None  # Si es None, prueba todos


@router.get("/capabilities")
async def get_voice_capabilities():
    """
    Obtiene las capacidades de voz disponibles en el sistema.

    Returns:
        Dict con capacidades de ElevenLabs y Vertex AI
    """
    try:
        capabilities = await hybrid_voice_adapter.get_voice_capabilities()
        return {"status": "success", "capabilities": capabilities}
    except Exception as e:
        logger.error(f"Error obteniendo capacidades de voz: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_voice_enabled_agents():
    """
    Lista todos los agentes con capacidades de voz implementadas.

    Returns:
        Dict con lista de agentes y sus capacidades de voz
    """
    voice_enabled_agents = {
        "blaze_elite_training": {
            "name": "BLAZE - Elite Training Strategist",
            "personality": "ESTP - The Entrepreneur",
            "voice_style": "Energetic, motivational, empowering",
            "specialization": "Training motivation and form correction",
            "emotion_contexts": ["motivated", "excited", "calm", "frustrated"],
        },
        "luna_female_wellness": {
            "name": "LUNA - Female Wellness Coach",
            "personality": "ENFJ - The Protagonist (maternal variant)",
            "voice_style": "Nurturing, empowering, maternal",
            "specialization": "Hormonal guidance and emotional wellness",
            "emotion_contexts": ["calm", "nurturing", "motivated", "frustrated"],
        },
        "code_genetic": {
            "name": "CODE - Genetic Performance Specialist",
            "personality": "INTJ - The Architect (scientific variant)",
            "voice_style": "Scientific precision with controlled excitement",
            "specialization": "Genetic findings and optimization guidance",
            "emotion_contexts": ["analytical", "excited", "cautious", "confident"],
        },
    }

    return {
        "status": "success",
        "voice_enabled_agents": voice_enabled_agents,
        "total_agents": len(voice_enabled_agents),
        "integration_status": "ElevenLabs + Vertex AI Hybrid",
    }


@router.post("/test-agent-voice")
async def test_agent_voice(request: VoiceTestRequest):
    """
    Prueba la voz de un agente específico con texto personalizado.

    Args:
        request: Configuración de prueba de voz

    Returns:
        Dict con audio sintetizado y metadatos
    """
    try:
        # Validar agente
        valid_agents = ["blaze_elite_training", "luna_female_wellness", "code_genetic"]
        if request.agent_id not in valid_agents:
            raise HTTPException(
                status_code=400,
                detail=f"Agent ID '{request.agent_id}' not supported. Valid agents: {valid_agents}",
            )

        # Sintetizar voz usando el adaptador híbrido
        result = await hybrid_voice_adapter.synthesize_speech(
            text=request.text,
            agent_id=request.agent_id,
            program_type=request.program_type,
            emotion_context=request.emotion_context,
        )

        return {
            "status": "success",
            "agent_id": request.agent_id,
            "test_request": request.dict(),
            "voice_result": result,
        }

    except Exception as e:
        logger.error(
            f"Error en prueba de voz para agente {request.agent_id}: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-voice-preview")
async def get_agent_voice_preview(request: AgentVoicePreviewRequest):
    """
    Obtiene una preview de la voz de un agente con texto predefinido.

    Args:
        request: Solicitud de preview

    Returns:
        Dict con preview de audio del agente
    """
    try:
        # Generar preview usando ElevenLabs client
        result = await elevenlabs_client.get_agent_voice_preview(
            agent_id=request.agent_id, sample_text=request.sample_text
        )

        return {
            "status": "success",
            "agent_id": request.agent_id,
            "preview_result": result,
        }

    except Exception as e:
        logger.error(
            f"Error generando preview para agente {request.agent_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-voice-test")
async def bulk_voice_test(request: BulkVoiceTestRequest):
    """
    Prueba las voces de múltiples agentes simultáneamente.

    Args:
        request: Configuración de prueba masiva

    Returns:
        Dict con resultados de todos los agentes probados
    """
    try:
        # Determinar qué agentes probar
        all_agents = ["blaze_elite_training", "luna_female_wellness", "code_genetic"]
        agents_to_test = request.agents_to_test or all_agents

        # Validar agentes
        invalid_agents = [agent for agent in agents_to_test if agent not in all_agents]
        if invalid_agents:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agents: {invalid_agents}. Valid agents: {all_agents}",
            )

        # Probar cada agente
        results = {}
        for agent_id in agents_to_test:
            try:
                result = await hybrid_voice_adapter.synthesize_speech(
                    text=request.test_text,
                    agent_id=agent_id,
                    program_type=request.program_type,
                    emotion_context="motivated",
                )
                results[agent_id] = {"status": "success", "result": result}
            except Exception as e:
                results[agent_id] = {"status": "error", "error": str(e)}
                logger.error(f"Error probando agente {agent_id}: {e}")

        return {
            "status": "success",
            "test_configuration": request.dict(),
            "agents_tested": len(agents_to_test),
            "successful_tests": len(
                [r for r in results.values() if r["status"] == "success"]
            ),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error en prueba masiva de voces: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-agent-specialization")
async def test_agent_specialization(
    agent_id: str = Query(..., description="ID del agente a probar"),
    specialization_type: str = Query(
        ..., description="Tipo de especialización a probar"
    ),
    program_type: str = Query(default="PRIME", description="Tipo de programa"),
):
    """
    Prueba las capacidades especializadas de voz de cada agente.

    Args:
        agent_id: ID del agente
        specialization_type: Tipo de especialización específica
        program_type: Tipo de programa

    Returns:
        Dict con resultado de la prueba especializada
    """
    try:
        # Crear instancias de agentes para pruebas específicas
        agent_instances = {
            "blaze_elite_training": EliteTrainingStrategist(),
            "luna_female_wellness": FemaleWellnessCoach(),
            "code_genetic": CodeGeneticSpecialist(),
        }

        if agent_id not in agent_instances:
            raise HTTPException(
                status_code=400, detail=f"Agent ID '{agent_id}' not supported"
            )

        agent = agent_instances[agent_id]
        result = None

        # Probar especialización según el agente
        if agent_id == "blaze_elite_training":
            if specialization_type == "workout_motivation":
                result = await agent.provide_workout_motivation(
                    workout_phase="training",
                    user_performance={"energy_level": 75},
                    program_type=program_type,
                )
            elif specialization_type == "form_correction":
                result = await agent.provide_form_correction_audio(
                    exercise_name="sentadillas",
                    correction_points=[
                        "postura de espalda",
                        "profundidad del movimiento",
                    ],
                    program_type=program_type,
                )
            else:
                raise HTTPException(
                    status_code=400, detail="Invalid specialization for BLAZE"
                )

        elif agent_id == "luna_female_wellness":
            if specialization_type == "cycle_guidance":
                result = await agent.provide_hormonal_cycle_guidance(
                    cycle_phase="ovulatory",
                    user_symptoms=["energy"],
                    program_type=program_type,
                )
            elif specialization_type == "menopause_support":
                result = await agent.provide_menopause_support(
                    menopause_stage="perimenopause",
                    support_type="emotional",
                    program_type=program_type,
                )
            elif specialization_type == "emotional_wellness":
                result = await agent.provide_emotional_wellness_audio(
                    emotional_state="confident",
                    wellness_focus="self_care",
                    program_type=program_type,
                )
            else:
                raise HTTPException(
                    status_code=400, detail="Invalid specialization for LUNA"
                )

        elif agent_id == "code_genetic":
            if specialization_type == "genetic_findings":
                result = await agent.explain_genetic_findings(
                    finding_type="advantage",
                    genetic_data={"test": "data"},
                    complexity_level="intermediate",
                    program_type=program_type,
                )
            elif specialization_type == "genetic_guidance":
                result = await agent.provide_genetic_guidance(
                    guidance_type="nutrition", program_type=program_type
                )
            else:
                raise HTTPException(
                    status_code=400, detail="Invalid specialization for CODE"
                )

        return {
            "status": "success",
            "agent_id": agent_id,
            "specialization_type": specialization_type,
            "program_type": program_type,
            "specialization_result": result,
        }

    except Exception as e:
        logger.error(
            f"Error probando especialización {specialization_type} para {agent_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def voice_system_health():
    """
    Verifica el estado de salud del sistema de voz.

    Returns:
        Dict con estado de salud de ElevenLabs y Vertex AI
    """
    try:
        # Verificar adaptador híbrido
        await hybrid_voice_adapter.initialize()

        # Verificar ElevenLabs
        elevenlabs_status = (
            "available" if not elevenlabs_client.mock_mode else "mock_mode"
        )

        # Obtener estadísticas de uso
        usage_stats = hybrid_voice_adapter.usage_stats

        return {
            "status": "healthy",
            "elevenlabs_status": elevenlabs_status,
            "hybrid_adapter_initialized": hybrid_voice_adapter.is_initialized,
            "usage_statistics": usage_stats,
            "agents_with_voice": 3,
            "total_voice_capabilities": [
                "personality_adaptation",
                "emotion_context",
                "program_adaptation",
                "specialization_support",
            ],
        }

    except Exception as e:
        logger.error(f"Error verificando salud del sistema de voz: {e}", exc_info=True)
        return {
            "status": "degraded",
            "error": str(e),
            "elevenlabs_status": "unknown",
            "hybrid_adapter_initialized": False,
        }
