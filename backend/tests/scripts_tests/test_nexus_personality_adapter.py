#!/usr/bin/env python3
"""
Test script para PersonalityAdapter de NEXUS (Orchestrator).

Prueba las adaptaciones de personalidad para diferentes tipos de programa:
- NGX PRIME: Director estratégico de sistemas
- NGX LONGEVITY: Guía integral de bienestar
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator.agent import NGXNexusOrchestrator
from core.personality.personality_adapter import PersonalityProfile


async def test_nexus_personality_adaptations():
    """
    Prueba las adaptaciones de personalidad del agente NEXUS.
    """
    print("🎯 Iniciando pruebas de PersonalityAdapter para NEXUS")
    print("=" * 70)

    try:
        # Inicializar el agente NEXUS
        nexus = NGXNexusOrchestrator()

        # Mensaje de coordinación base para probar adaptaciones
        base_orchestration_message = """
        Te ayudo a encontrar la información que necesitas. Podemos explorar diferentes opciones.
        
        Basado en tu consulta, vamos a ver qué agentes especializados pueden apoyarte:
        
        1. Para análisis detallado, consultaré con nuestros expertos en datos
        2. Para recomendaciones personalizadas, coordinaré con especialistas en bienestar
        3. Para seguimiento de progreso, conectaré con analistas de performance
        
        Mi análisis indica que esta es la mejor ruta para tu consulta.
        
        ¿Te parece bien esta sugerencia para comenzar?
        """

        print("📝 Mensaje base de coordinación:")
        print("-" * 50)
        print(base_orchestration_message)
        print()

        # Test 1: Adaptación para NGX PRIME (Ejecutivos)
        print("🔷 TEST 1: Adaptación para NGX PRIME (Ejecutivos)")
        print("-" * 50)

        prime_context = {
            "program_type": "PRIME",
            "user_query": "Necesito una estrategia ejecutiva para optimizar el rendimiento del equipo",
            "preferences": {"communication_style": "strategic", "focus": "efficiency"},
            "emotional_state": "strategic_thinking",
        }

        prime_adapted = await nexus._apply_personality_adaptation(
            base_orchestration_message, prime_context
        )

        print("Respuesta adaptada para PRIME:")
        print(prime_adapted)
        print()

        # Test 2: Adaptación para NGX LONGEVITY (Bienestar)
        print("🔶 TEST 2: Adaptación para NGX LONGEVITY (Bienestar)")
        print("-" * 50)

        longevity_context = {
            "program_type": "LONGEVITY",
            "user_query": "¿Cómo puedo crear un plan integral de bienestar?",
            "preferences": {"communication_style": "warm", "focus": "holistic_growth"},
            "emotional_state": "seeking_guidance",
        }

        longevity_adapted = await nexus._apply_personality_adaptation(
            base_orchestration_message, longevity_context
        )

        print("Respuesta adaptada para LONGEVITY:")
        print(longevity_adapted)
        print()

        # Test 3: Comparación directa de adaptaciones específicas
        print("🔍 TEST 3: Comparación de adaptaciones específicas")
        print("-" * 50)

        test_message = "Te ayudo a resolver esto. Podemos explorar las opciones y consultar con los agentes especializados para obtener apoyo."

        print("Mensaje original:")
        print(f"'{test_message}'")
        print()

        prime_specific = nexus._apply_nexus_prime_adaptations(test_message)
        print("🔷 PRIME (Ejecutivo):")
        print(f"'{prime_specific}'")
        print()

        longevity_specific = nexus._apply_nexus_longevity_adaptations(test_message)
        print("🔶 LONGEVITY (Bienestar):")
        print(f"'{longevity_specific}'")
        print()

        # Test 4: Simulación de contextos de coordinación
        print("🎯 TEST 4: Contextos de coordinación y análisis")
        print("-" * 50)

        coordination_message = "Vamos a ver el mejor enfoque. Mi análisis indica que necesitamos ayuda especializada para esta consulta. Te sugiero que consultemos con expertos."

        print("Mensaje de coordinación original:")
        print(coordination_message)
        print()

        # PRIME - Coordinación estratégica
        prime_coordination_context = {
            "program_type": "PRIME",
            "user_query": "Estrategia para escalar operaciones de la empresa",
            "preferences": {"focus": "strategic_efficiency", "urgency": "high"},
        }

        prime_coordination = await nexus._apply_personality_adaptation(
            coordination_message, prime_coordination_context
        )

        print("🔷 PRIME - Coordinación estratégica:")
        print(prime_coordination)
        print()

        # LONGEVITY - Guía empática
        longevity_coordination_context = {
            "program_type": "LONGEVITY",
            "user_query": "Quiero mejorar mi bienestar integral paso a paso",
            "preferences": {"focus": "personal_growth", "pace": "gradual"},
        }

        longevity_coordination = await nexus._apply_personality_adaptation(
            coordination_message, longevity_coordination_context
        )

        print("🔶 LONGEVITY - Guía empática:")
        print(longevity_coordination)
        print()

        # Test 5: Análisis de vocabulario de coordinación
        print("💬 TEST 5: Transformación de vocabulario de coordinación")
        print("-" * 50)

        coordination_terms = [
            "Te ayudo a encontrar la mejor solución con nuestros agentes especializados",
            "Podemos explorar las opciones de análisis más efectivas",
            "Vamos a ver qué recomendaciones pueden dar los expertos",
            "Mi análisis sugiere consultar con especialistas para apoyo integral",
        ]

        for i, term in enumerate(coordination_terms, 1):
            print(f"\n📝 Frase {i}: {term}")

            print("\n🔷 PRIME:")
            prime_result = nexus._apply_nexus_prime_adaptations(term)
            print(prime_result)

            print("\n🔶 LONGEVITY:")
            longevity_result = nexus._apply_nexus_longevity_adaptations(term)
            print(longevity_result)
            print("-" * 30)

        # Test 6: Análisis de características de personalidad
        print("\n🧠 TEST 6: Características de personalidad NEXUS")
        print("-" * 50)

        print("NEXUS - The Master Conductor (INTJ)")
        print("• Personalidad: INTJ - The Architect, analítico y estratégico")
        print("• Voz: Consultor profesional con autoridad cálida")
        print("• PRIME: Director Estratégico de Sistemas")
        print("  - Coordinación ejecutiva de alto nivel")
        print("  - Análisis de intención con enfoque en ROI")
        print("  - Síntesis estratégica de insights")
        print("• LONGEVITY: Guía Integral de Bienestar")
        print("  - Coordinación empática y comprensiva")
        print("  - Análisis holístico de necesidades")
        print("  - Síntesis nutritiva de guidance")
        print()

        # Test 7: Análisis de intent routing personalizado
        print("🎭 TEST 7: Intent routing personalizado por audiencia")
        print("-" * 50)

        intent_scenarios = {
            "training_request": "Necesito un plan de entrenamiento personalizado",
            "nutrition_query": "¿Qué debo comer para mejorar mi rendimiento?",
            "progress_tracking": "Quiero monitorear mi progreso de forma eficiente",
            "general_wellness": "Busco mejorar mi bienestar general",
        }

        for intent, query in intent_scenarios.items():
            print(f"\n📋 Intent: {intent.upper()}")
            print(f"Query: {query}")

            # Crear mensaje de routing base
            routing_message = f"Para tu consulta sobre {intent.replace('_', ' ')}, te ayudo a conectar con los especialistas adecuados. Podemos explorar las mejores opciones disponibles."

            print("\n🔷 PRIME - Routing estratégico:")
            prime_routing = nexus._apply_nexus_prime_adaptations(routing_message)
            print(prime_routing)

            print("\n🔶 LONGEVITY - Routing empático:")
            longevity_routing = nexus._apply_nexus_longevity_adaptations(
                routing_message
            )
            print(longevity_routing)
            print("-" * 40)

        print("\n✅ Pruebas de PersonalityAdapter para NEXUS completadas exitosamente!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()


def test_nexus_adaptations_sync():
    """
    Prueba síncrona de las adaptaciones específicas de NEXUS.
    """
    print("🎯 Pruebas síncronas de adaptaciones específicas")
    print("-" * 50)

    try:
        nexus = NGXNexusOrchestrator()

        # Mensajes de prueba específicos para NEXUS
        test_messages = [
            "Te ayudo a encontrar la información que necesitas sobre entrenamiento.",
            "Podemos explorar diferentes opciones de análisis nutricional disponibles.",
            "Vamos a ver qué agentes pueden dar apoyo especializado en tu consulta.",
            "Mi análisis sugiere consultar con expertos para una recomendación integral.",
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Mensaje {i}: {message}")

            print("\n🔷 PRIME:")
            prime_result = nexus._apply_nexus_prime_adaptations(message)
            print(prime_result)

            print("\n🔶 LONGEVITY:")
            longevity_result = nexus._apply_nexus_longevity_adaptations(message)
            print(longevity_result)
            print("-" * 30)

    except Exception as e:
        print(f"❌ Error en pruebas síncronas: {e}")


def test_nexus_coordination_language_transformation():
    """
    Prueba específica para la transformación de lenguaje de coordinación de NEXUS.
    """
    print("🎭 Pruebas de transformación de lenguaje de coordinación")
    print("-" * 50)

    try:
        nexus = NGXNexusOrchestrator()

        # Términos de coordinación específicos de NEXUS
        coordination_phrases = {
            "te ayudo a": {
                "prime": "coordino los recursos para",
                "longevity": "te acompaño a",
            },
            "podemos explorar": {
                "prime": "analizaré estratégicamente",
                "longevity": "exploraremos juntos",
            },
            "agentes": {
                "prime": "especialistas de alto rendimiento",
                "longevity": "expertos en bienestar",
            },
            "análisis": {
                "prime": "evaluación estratégica ejecutiva",
                "longevity": "análisis integral de bienestar",
            },
        }

        base_message = "Te ayudo a resolver esto. Podemos explorar las opciones y consultar con nuestros agentes para hacer un análisis completo."

        print(f"Mensaje original: {base_message}")
        print()

        print("🔷 PRIME - Transforma a dirección estratégica:")
        prime_result = nexus._apply_nexus_prime_adaptations(base_message)
        print(prime_result)
        print()

        print("🔶 LONGEVITY - Transforma a guía empática:")
        longevity_result = nexus._apply_nexus_longevity_adaptations(base_message)
        print(longevity_result)
        print()

        print("📊 Análisis de transformaciones aplicadas:")
        for coordination, transformations in coordination_phrases.items():
            if coordination in base_message.lower():
                print(f"  • '{coordination}' →")
                print(f"    - PRIME: '{transformations['prime']}'")
                print(f"    - LONGEVITY: '{transformations['longevity']}'")

    except Exception as e:
        print(f"❌ Error en pruebas de transformación: {e}")


if __name__ == "__main__":
    print("🎯 NEXUS PersonalityAdapter Test Suite")
    print("=" * 70)

    # Ejecutar pruebas síncronas primero
    test_nexus_adaptations_sync()

    print("\n" + "=" * 70)

    # Ejecutar pruebas de transformación de lenguaje de coordinación
    test_nexus_coordination_language_transformation()

    print("\n" + "=" * 70)

    # Ejecutar pruebas asíncronas
    asyncio.run(test_nexus_personality_adaptations())
