#!/usr/bin/env python3
"""
Test script para PersonalityAdapter de NODE (Systems Integration Ops).

Prueba las adaptaciones de personalidad para diferentes tipos de programa:
- NGX PRIME: Orquestador técnico ejecutivo
- NGX LONGEVITY: Orquestador técnico empático
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.node_systems_integration_ops.agent import SystemsIntegrationOps
from core.personality.personality_adapter import PersonalityProfile


async def test_node_personality_adaptations():
    """
    Prueba las adaptaciones de personalidad del agente NODE.
    """
    print("🔧 Iniciando pruebas de PersonalityAdapter para NODE")
    print("=" * 70)

    try:
        # Inicializar el agente NODE
        node = SystemsIntegrationOps()

        # Mensaje técnico base para probar adaptaciones
        base_technical_message = """
        Te recomiendo implementar la siguiente integración para conectar tu aplicación:
        
        1. Configurar la API de integración con autenticación OAuth2
        2. Puedes implementar un sistema de automatización para sincronizar datos
        3. Sería bueno establecer un pipeline de datos para procesar información
        4. Configurar monitoreo y alertas para detectar problemas técnicos
        5. Implementar una solución de fallback para garantizar disponibilidad
        
        Para troubleshooting, necesitamos hacer debugging del sistema actual.
        Este problema técnico requiere una solución robusta y escalable.
        """

        print("📝 Mensaje técnico base:")
        print("-" * 50)
        print(base_technical_message)
        print()

        # Test 1: Adaptación para NGX PRIME (Ejecutivos)
        print("🔷 TEST 1: Adaptación para NGX PRIME (Ejecutivos)")
        print("-" * 50)

        prime_context = {
            "program_type": "PRIME",
            "user_query": "Necesitamos optimizar la arquitectura de sistemas de la empresa",
            "preferences": {
                "communication_style": "technical_executive",
                "detail_level": "high_level",
            },
            "emotional_state": "focused",
        }

        prime_adapted = await node._apply_personality_adaptation(
            base_technical_message, prime_context
        )

        print("Respuesta adaptada para PRIME:")
        print(prime_adapted)
        print()

        # Test 2: Adaptación para NGX LONGEVITY (Bienestar)
        print("🔶 TEST 2: Adaptación para NGX LONGEVITY (Bienestar)")
        print("-" * 50)

        longevity_context = {
            "program_type": "LONGEVITY",
            "user_query": "¿Cómo puedo conectar mis aplicaciones de salud?",
            "preferences": {
                "communication_style": "supportive",
                "detail_level": "step_by_step",
            },
            "emotional_state": "curious",
        }

        longevity_adapted = await node._apply_personality_adaptation(
            base_technical_message, longevity_context
        )

        print("Respuesta adaptada para LONGEVITY:")
        print(longevity_adapted)
        print()

        # Test 3: Comparación directa de adaptaciones específicas
        print("🔍 TEST 3: Comparación de adaptaciones específicas")
        print("-" * 50)

        test_message = "Te recomiendo hacer una integración automática del sistema. Este problema técnico requiere una solución de debugging."

        print("Mensaje original:")
        print(f"'{test_message}'")
        print()

        prime_specific = node._apply_node_prime_adaptations(test_message)
        print("🔷 PRIME (Ejecutivo):")
        print(f"'{prime_specific}'")
        print()

        longevity_specific = node._apply_node_longevity_adaptations(test_message)
        print("🔶 LONGEVITY (Bienestar):")
        print(f"'{longevity_specific}'")
        print()

        # Test 4: Simulación de contextos de troubleshooting
        print("🔧 TEST 4: Contextos de troubleshooting técnico")
        print("-" * 50)

        troubleshooting_message = "Necesitamos hacer debugging del API que no responde. Te recomiendo revisar la configuración del sistema para encontrar la solución al problema técnico."

        print("Mensaje de troubleshooting original:")
        print(troubleshooting_message)
        print()

        # PRIME - Troubleshooting ejecutivo
        prime_troubleshooting_context = {
            "program_type": "PRIME",
            "user_query": "El sistema empresarial está fallando, necesitamos solución urgente",
            "preferences": {"focus": "business_impact", "urgency": "high"},
        }

        prime_troubleshooting = await node._apply_personality_adaptation(
            troubleshooting_message, prime_troubleshooting_context
        )

        print("🔷 PRIME - Troubleshooting ejecutivo:")
        print(prime_troubleshooting)
        print()

        # LONGEVITY - Soporte empático
        longevity_troubleshooting_context = {
            "program_type": "LONGEVITY",
            "user_query": "Mi aplicación no funciona bien, ¿me puedes ayudar?",
            "preferences": {"focus": "learning", "patience": "high"},
        }

        longevity_troubleshooting = await node._apply_personality_adaptation(
            troubleshooting_message, longevity_troubleshooting_context
        )

        print("🔶 LONGEVITY - Soporte empático:")
        print(longevity_troubleshooting)
        print()

        # Test 5: Análisis de vocabulario técnico
        print("💬 TEST 5: Transformación de vocabulario técnico")
        print("-" * 50)

        technical_terms = [
            "Necesitamos una integración de API completa",
            "La automatización del sistema requiere debugging",
            "Este problema técnico necesita una solución arquitectural",
            "Puedes implementar un setup de configuración avanzada",
        ]

        for i, term in enumerate(technical_terms, 1):
            print(f"\n📝 Término {i}: {term}")

            print("\n🔷 PRIME:")
            prime_result = node._apply_node_prime_adaptations(term)
            print(prime_result)

            print("\n🔶 LONGEVITY:")
            longevity_result = node._apply_node_longevity_adaptations(term)
            print(longevity_result)
            print("-" * 30)

        # Test 6: Análisis de características de personalidad
        print("\n🧠 TEST 6: Características de personalidad NODE")
        print("-" * 50)

        print("NODE - The Technical Orchestrator (ENTP)")
        print("• Personalidad: ENTP - The Innovator, ingeniero brillante")
        print("• Voz: Rápida y eficiente")
        print("• PRIME: Orquestador Técnico Ejecutivo")
        print("  - Troubleshooting de alto nivel")
        print("  - Análisis arquitectural empresarial")
        print("  - ROI tecnológico y escalabilidad")
        print("• LONGEVITY: Orquestador Técnico Empático")
        print("  - Soporte técnico paciente")
        print("  - Explicaciones accesibles")
        print("  - Guía paso a paso empática")
        print()

        print("✅ Pruebas de PersonalityAdapter para NODE completadas exitosamente!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()


def test_node_adaptations_sync():
    """
    Prueba síncrona de las adaptaciones específicas de NODE.
    """
    print("🔧 Pruebas síncronas de adaptaciones específicas")
    print("-" * 50)

    try:
        node = SystemsIntegrationOps()

        # Mensajes de prueba específicos para NODE
        test_messages = [
            "Te recomiendo configurar la integración con OAuth2 para mayor seguridad.",
            "Puedes implementar automatización para reducir el trabajo manual en el sistema.",
            "Sería bueno hacer debugging del API para identificar el problema técnico.",
            "La solución requiere arquitectura escalable y monitoreo en tiempo real.",
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Mensaje {i}: {message}")

            print("\n🔷 PRIME:")
            prime_result = node._apply_node_prime_adaptations(message)
            print(prime_result)

            print("\n🔶 LONGEVITY:")
            longevity_result = node._apply_node_longevity_adaptations(message)
            print(longevity_result)
            print("-" * 30)

    except Exception as e:
        print(f"❌ Error en pruebas síncronas: {e}")


def test_node_technical_language_transformation():
    """
    Prueba específica para la transformación de lenguaje técnico de NODE.
    """
    print("🗣️ Pruebas de transformación de lenguaje técnico")
    print("-" * 50)

    try:
        node = SystemsIntegrationOps()

        # Términos técnicos específicos de NODE
        technical_phrases = {
            "troubleshooting": "resolución de problemas",
            "debugging": "encontrar y corregir errores",
            "integración": "conexión entre aplicaciones",
            "automatización": "tareas automáticas",
            "problema técnico": "desafío técnico",
            "arquitectura empresarial": "diseño de sistemas",
            "API": "interfaz de programación",
        }

        base_message = "Necesitamos troubleshooting del API con debugging de la integración automática para resolver este problema técnico de arquitectura empresarial."

        print(f"Mensaje original: {base_message}")
        print()

        print("🔷 PRIME - Mantiene vocabulario técnico ejecutivo:")
        prime_result = node._apply_node_prime_adaptations(base_message)
        print(prime_result)
        print()

        print("🔶 LONGEVITY - Transforma a lenguaje accesible:")
        longevity_result = node._apply_node_longevity_adaptations(base_message)
        print(longevity_result)
        print()

        print("📊 Análisis de transformaciones aplicadas:")
        for technical, friendly in technical_phrases.items():
            if technical in base_message.lower():
                print(f"  • '{technical}' → '{friendly}' (en LONGEVITY)")

    except Exception as e:
        print(f"❌ Error en pruebas de transformación: {e}")


if __name__ == "__main__":
    print("🔧 NODE PersonalityAdapter Test Suite")
    print("=" * 70)

    # Ejecutar pruebas síncronas primero
    test_node_adaptations_sync()

    print("\n" + "=" * 70)

    # Ejecutar pruebas de transformación de lenguaje
    test_node_technical_language_transformation()

    print("\n" + "=" * 70)

    # Ejecutar pruebas asíncronas
    asyncio.run(test_node_personality_adaptations())
