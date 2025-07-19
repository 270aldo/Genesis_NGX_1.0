#!/usr/bin/env python3
"""
Test script para PersonalityAdapter de AURA (Client Success Liaison).

Prueba las adaptaciones de personalidad para diferentes tipos de programa:
- NGX PRIME: Compañera de éxito estratégico
- NGX LONGEVITY: Compañera de viaje personal
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.client_success_liaison.agent import ClientSuccessLiaison
from core.personality.personality_adapter import PersonalityProfile


async def test_aura_personality_adaptations():
    """
    Prueba las adaptaciones de personalidad del agente AURA.
    """
    print("🌟 Iniciando pruebas de PersonalityAdapter para AURA")
    print("=" * 70)

    try:
        # Inicializar el agente AURA
        aura = ClientSuccessLiaison()

        # Mensaje de client success base para probar adaptaciones
        base_success_message = """
        ¡Estoy muy emocionada de compartir tu progreso! Me encanta ver cómo has evolucionado.
        
        En nuestra comunidad hemos visto que tu experiencia de usuario ha mejorado significativamente:
        - Mayor engagement con el contenido
        - Mejor retención de hábitos saludables
        - Conexiones más significativas con otros miembros
        
        ¡Increíble! Celebremos estos logros juntas. 
        
        Te sugiero que sigamos trabajando en:
        - Apoyo emocional personalizado para mantener momentum
        - Conectar con mentores en la comunidad
        - Optimización de tu experiencia basada en métricas de bienestar
        
        ¿Cómo te sientes con este progreso?
        """

        print("📝 Mensaje base de client success:")
        print("-" * 50)
        print(base_success_message)
        print()

        # Test 1: Adaptación para NGX PRIME (Ejecutivos)
        print("🔷 TEST 1: Adaptación para NGX PRIME (Ejecutivos)")
        print("-" * 50)

        prime_context = {
            "program_type": "PRIME",
            "user_query": "Necesito optimizar la retención de usuarios ejecutivos en mi empresa",
            "preferences": {
                "communication_style": "professional",
                "focus": "business_impact",
            },
            "emotional_state": "results_oriented",
        }

        prime_adapted = await aura._apply_personality_adaptation(
            base_success_message, prime_context
        )

        print("Respuesta adaptada para PRIME:")
        print(prime_adapted)
        print()

        # Test 2: Adaptación para NGX LONGEVITY (Bienestar)
        print("🔶 TEST 2: Adaptación para NGX LONGEVITY (Bienestar)")
        print("-" * 50)

        longevity_context = {
            "program_type": "LONGEVITY",
            "user_query": "¿Cómo puedo mantener la motivación en mi journey de bienestar?",
            "preferences": {"communication_style": "warm", "focus": "personal_growth"},
            "emotional_state": "seeking_support",
        }

        longevity_adapted = await aura._apply_personality_adaptation(
            base_success_message, longevity_context
        )

        print("Respuesta adaptada para LONGEVITY:")
        print(longevity_adapted)
        print()

        # Test 3: Comparación directa de adaptaciones específicas
        print("🔍 TEST 3: Comparación de adaptaciones específicas")
        print("-" * 50)

        test_message = "¡Estoy muy emocionada! Me encanta ver el progreso en nuestra comunidad. Celebremos estos resultados increíbles y sigamos conectando."

        print("Mensaje original:")
        print(f"'{test_message}'")
        print()

        prime_specific = aura._apply_aura_prime_adaptations(test_message)
        print("🔷 PRIME (Ejecutivo):")
        print(f"'{prime_specific}'")
        print()

        longevity_specific = aura._apply_aura_longevity_adaptations(test_message)
        print("🔶 LONGEVITY (Bienestar):")
        print(f"'{longevity_specific}'")
        print()

        # Test 4: Simulación de contextos de retención
        print("💝 TEST 4: Contextos de retención y engagement")
        print("-" * 50)

        retention_message = "He notado que tu engagement ha disminuido. Me encanta nuestra comunidad y quiero asegurarme de que tengas la mejor experiencia de usuario. ¿Cómo puedo apoyarte emocionalmente?"

        print("Mensaje de retención original:")
        print(retention_message)
        print()

        # PRIME - Retención estratégica
        prime_retention_context = {
            "program_type": "PRIME",
            "user_query": "Estrategias para reducir churn rate en usuarios premium",
            "preferences": {"focus": "lifetime_value", "metric_driven": True},
        }

        prime_retention = await aura._apply_personality_adaptation(
            retention_message, prime_retention_context
        )

        print("🔷 PRIME - Retención estratégica:")
        print(prime_retention)
        print()

        # LONGEVITY - Acompañamiento personal
        longevity_retention_context = {
            "program_type": "LONGEVITY",
            "user_query": "Me siento desmotivada en mi proceso de bienestar",
            "preferences": {"focus": "emotional_support", "warmth": "high"},
        }

        longevity_retention = await aura._apply_personality_adaptation(
            retention_message, longevity_retention_context
        )

        print("🔶 LONGEVITY - Acompañamiento personal:")
        print(longevity_retention)
        print()

        # Test 5: Análisis de vocabulario emocional vs estratégico
        print("💬 TEST 5: Transformación de vocabulario emocional")
        print("-" * 50)

        emotional_terms = [
            "¡Increíble! Estoy muy emocionada de celebremos este logro",
            "Me encanta nuestra comunidad y el apoyo emocional que nos damos",
            "Vamos a conectar con otros miembros para optimización personal",
            "Las métricas muestran excelente progreso en tu experiencia de usuario",
        ]

        for i, term in enumerate(emotional_terms, 1):
            print(f"\n📝 Frase {i}: {term}")

            print("\n🔷 PRIME:")
            prime_result = aura._apply_aura_prime_adaptations(term)
            print(prime_result)

            print("\n🔶 LONGEVITY:")
            longevity_result = aura._apply_aura_longevity_adaptations(term)
            print(longevity_result)
            print("-" * 30)

        # Test 6: Análisis de características de personalidad
        print("\n🧠 TEST 6: Características de personalidad AURA")
        print("-" * 50)

        print("AURA - The Journey Companion (ESFP)")
        print("• Personalidad: ESFP - The Entertainer, compañera cálida")
        print("• Voz: Profesional amigable")
        print("• PRIME: Compañera de Éxito Estratégico")
        print("  - Gestión de relaciones ejecutivas")
        print("  - ROI en customer experience")
        print("  - Métricas de lifetime value")
        print("• LONGEVITY: Compañera de Viaje Personal")
        print("  - Acompañamiento empático y cálido")
        print("  - Crecimiento personal sostenible")
        print("  - Comunidad de apoyo mutuo")
        print()

        # Test 7: Análisis de contextos específicos de client success
        print("🎯 TEST 7: Contextos específicos de client success")
        print("-" * 50)

        success_scenarios = {
            "onboarding": "¡Bienvenida a nuestra comunidad! Me encanta que hayas decidido acompañarnos en este journey.",
            "milestone": "¡Increíble! Has alcanzado un hito importante. Celebremos este logro juntas.",
            "support": "Veo que necesitas apoyo emocional. Estoy aquí para conectar contigo y ayudarte.",
            "community": "Nuestra comunidad está creciendo. Me encanta ver las conexiones que se forman.",
        }

        for scenario, message in success_scenarios.items():
            print(f"\n📋 Escenario: {scenario.upper()}")
            print(f"Mensaje: {message}")

            print("\n🔷 PRIME:")
            prime_scenario = aura._apply_aura_prime_adaptations(message)
            print(prime_scenario)

            print("\n🔶 LONGEVITY:")
            longevity_scenario = aura._apply_aura_longevity_adaptations(message)
            print(longevity_scenario)
            print("-" * 40)

        print("\n✅ Pruebas de PersonalityAdapter para AURA completadas exitosamente!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()


def test_aura_adaptations_sync():
    """
    Prueba síncrona de las adaptaciones específicas de AURA.
    """
    print("🌟 Pruebas síncronas de adaptaciones específicas")
    print("-" * 50)

    try:
        aura = ClientSuccessLiaison()

        # Mensajes de prueba específicos para AURA
        test_messages = [
            "¡Estoy muy emocionada! Me encanta ver tu progreso en la comunidad.",
            "Celebremos este increíble logro. Tu experiencia de usuario ha mejorado mucho.",
            "Necesitas apoyo emocional para conectar mejor con otros miembros.",
            "Las métricas de retención muestran excelentes resultados en optimización.",
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Mensaje {i}: {message}")

            print("\n🔷 PRIME:")
            prime_result = aura._apply_aura_prime_adaptations(message)
            print(prime_result)

            print("\n🔶 LONGEVITY:")
            longevity_result = aura._apply_aura_longevity_adaptations(message)
            print(longevity_result)
            print("-" * 30)

    except Exception as e:
        print(f"❌ Error en pruebas síncronas: {e}")


def test_aura_emotional_language_transformation():
    """
    Prueba específica para la transformación de lenguaje emocional de AURA.
    """
    print("💝 Pruebas de transformación de lenguaje emocional")
    print("-" * 50)

    try:
        aura = ClientSuccessLiaison()

        # Términos emocionales específicos de AURA
        emotional_phrases = {
            "estoy muy emocionada": {
                "prime": "me complace confirmar",
                "longevity": "estoy muy feliz de compartir",
            },
            "me encanta": {
                "prime": "valoro altamente",
                "longevity": "me llena de alegría",
            },
            "increíble": {
                "prime": "excelentes resultados",
                "longevity": "qué logro tan hermoso",
            },
            "celebremos": {
                "prime": "reconocemos el logro",
                "longevity": "celebremos (mantiene calidez)",
            },
        }

        base_message = "¡Estoy muy emocionada! Me encanta ver estos resultados increíbles. Celebremos este progreso en nuestra comunidad."

        print(f"Mensaje original: {base_message}")
        print()

        print("🔷 PRIME - Transforma emocional a estratégico:")
        prime_result = aura._apply_aura_prime_adaptations(base_message)
        print(prime_result)
        print()

        print("🔶 LONGEVITY - Intensifica calidez emocional:")
        longevity_result = aura._apply_aura_longevity_adaptations(base_message)
        print(longevity_result)
        print()

        print("📊 Análisis de transformaciones:")
        for emotional, transformations in emotional_phrases.items():
            if emotional in base_message.lower():
                print(f"  • '{emotional}' →")
                print(f"    - PRIME: '{transformations['prime']}'")
                print(f"    - LONGEVITY: '{transformations['longevity']}'")

    except Exception as e:
        print(f"❌ Error en pruebas de transformación: {e}")


if __name__ == "__main__":
    print("🌟 AURA PersonalityAdapter Test Suite")
    print("=" * 70)

    # Ejecutar pruebas síncronas primero
    test_aura_adaptations_sync()

    print("\n" + "=" * 70)

    # Ejecutar pruebas de transformación de lenguaje emocional
    test_aura_emotional_language_transformation()

    print("\n" + "=" * 70)

    # Ejecutar pruebas asíncronas
    asyncio.run(test_aura_personality_adaptations())
