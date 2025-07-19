#!/usr/bin/env python3
"""
Script de prueba para validar la integración del MultiAgentCoordinator con NEXUS.

Este script prueba los nuevos flujos de comunicación multi-agente implementados.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.multi_agent_coordinator import multi_agent_coordinator
from core.logging_config import get_logger

logger = get_logger(__name__)


async def test_query_complexity_analysis():
    """Prueba el análisis de complejidad de consultas."""
    print("\n🧠 Probando análisis de complejidad de consultas...")
    
    test_queries = [
        ("Necesito ayuda con mi rutina", "SIMPLE"),
        ("Me siento cansado y no veo progreso en mis entrenamientos", "MODERADA"), 
        ("Quiero un análisis completo de mi salud, nutrición y entrenamiento", "COMPLEJA"),
        ("Tengo dolor de espalda, estoy estresado, no duermo bien y mi dieta es un desastre", "INTEGRAL")
    ]
    
    for query, expected_complexity in test_queries:
        try:
            complexity, agents = await multi_agent_coordinator.analyze_query_complexity(query)
            print(f"✅ Query: '{query[:50]}...'")
            print(f"   Complejidad detectada: {complexity.value} (esperado: {expected_complexity})")
            print(f"   Agentes sugeridos: {agents[:3]}...")  # Mostrar solo primeros 3
            print()
        except Exception as e:
            print(f"❌ Error en query '{query[:30]}...': {e}")


async def test_multi_agent_coordination():
    """Prueba la coordinación multi-agente completa."""
    print("\n🤝 Probando coordinación multi-agente...")
    
    complex_query = "Me siento agotado después de mis entrenamientos, no estoy viendo progreso y creo que mi nutrición no es la adecuada. ¿Qué debo hacer?"
    
    try:
        # Probar coordinación sin a2a_adapter (modo simulado)
        result = await multi_agent_coordinator.orchestrate_multi_agent_response(
            query=complex_query,
            user_context={"user_id": "test_user", "program_type": "PRIME"},
            a2a_adapter=None  # Usar modo simulado
        )
        
        print(f"✅ Consulta procesada exitosamente")
        print(f"   Complejidad: {result.complexity.value}")
        print(f"   Tipo de colaboración: {result.collaboration_type.value}")
        print(f"   Agentes participantes: {result.participating_agents}")
        print(f"   Nivel de consenso: {result.consensus_level:.2f}")
        print(f"   Tiempo de ejecución: {result.execution_time:.2f}s")
        print(f"   Recomendaciones unificadas: {len(result.unified_recommendations)}")
        print(f"   Respuesta sintetizada: {result.synthesized_response[:100]}...")
        
    except Exception as e:
        print(f"❌ Error en coordinación multi-agente: {e}")
        import traceback
        traceback.print_exc()


async def test_agent_perspectives():
    """Prueba la recopilación de perspectivas de agentes."""
    print("\n👥 Probando recopilación de perspectivas...")
    
    query = "¿Cómo puedo mejorar mi rendimiento?"
    agents = ["elite_training_strategist", "precision_nutrition_architect", "motivation_behavior_coach"]
    
    try:
        perspectives = await multi_agent_coordinator._gather_agent_perspectives(
            query=query,
            agents=agents,
            user_context={"program_type": "PRIME"},
            a2a_adapter=None  # Modo simulado
        )
        
        print(f"✅ Perspectivas recopiladas: {len(perspectives)}")
        for perspective in perspectives:
            print(f"   Agente: {perspective.agent_id}")
            print(f"   Confianza: {perspective.confidence_score:.2f}")
            print(f"   Respuesta: {perspective.response[:60]}...")
            print(f"   Recomendaciones: {len(perspective.recommendations)}")
            print()
            
    except Exception as e:
        print(f"❌ Error recopilando perspectivas: {e}")


async def test_orchestrator_integration():
    """Prueba la integración con el orchestrator NEXUS."""
    print("\n🎭 Probando integración con NEXUS orchestrator...")
    
    try:
        # Importar el orchestrator
        from agents.orchestrator.agent import NGXNexusOrchestrator
        
        # Crear instancia del orchestrator
        orchestrator = NGXNexusOrchestrator()
        print("✅ NEXUS Orchestrator creado exitosamente")
        
        # Verificar que tiene el MultiAgentCoordinator
        if hasattr(orchestrator, 'multi_agent_coordinator'):
            print("✅ MultiAgentCoordinator integrado en NEXUS")
        else:
            print("❌ MultiAgentCoordinator NO encontrado en NEXUS")
            
        # Probar métodos de decisión
        query = "Me siento cansado y no veo progreso"
        agent_ids = ["elite_training_strategist", "motivation_behavior_coach"]
        confidence = 0.7
        
        should_use_coordination = await orchestrator._should_use_multi_agent_coordination(
            query, agent_ids, confidence
        )
        print(f"✅ Decisión de coordinación: {should_use_coordination}")
        
    except Exception as e:
        print(f"❌ Error en integración con orchestrator: {e}")
        import traceback
        traceback.print_exc()


async def test_collaboration_stats():
    """Prueba las estadísticas de colaboración."""
    print("\n📊 Probando estadísticas de colaboración...")
    
    try:
        stats = multi_agent_coordinator.get_collaboration_stats()
        print("✅ Estadísticas de colaboración:")
        print(f"   Agentes disponibles: {stats['available_agents']}")
        print(f"   Mapeos de temas: {stats['topic_mappings']}")
        print(f"   Niveles de complejidad: {stats['supported_complexity_levels']}")
        print(f"   Tipos de colaboración: {stats['collaboration_types']}")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")


async def main():
    """Función principal de prueba."""
    print("🚀 Iniciando pruebas de integración MultiAgentCoordinator")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    await test_query_complexity_analysis()
    await test_multi_agent_coordination()
    await test_agent_perspectives()
    await test_orchestrator_integration()
    await test_collaboration_stats()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")


if __name__ == "__main__":
    asyncio.run(main())