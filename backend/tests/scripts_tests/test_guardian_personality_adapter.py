#!/usr/bin/env python3
"""
Test script para PersonalityAdapter de GUARDIAN (Security Compliance Guardian).

Prueba las adaptaciones de personalidad para diferentes tipos de programa:
- NGX PRIME: Briefings ejecutivos de seguridad
- NGX LONGEVITY: Protección personal y familiar
"""

import asyncio
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.security_compliance_guardian.agent import SecurityComplianceGuardian
from core.personality.personality_adapter import PersonalityProfile


async def test_guardian_personality_adaptations():
    """
    Prueba las adaptaciones de personalidad del agente GUARDIAN.
    """
    print("🛡️ Iniciando pruebas de PersonalityAdapter para GUARDIAN")
    print("=" * 70)

    try:
        # Inicializar el agente GUARDIAN
        guardian = SecurityComplianceGuardian(agent_id="test_guardian_personality")

        # Mensaje de seguridad base para probar adaptaciones
        base_security_message = """
        Te recomiendo implementar las siguientes medidas de seguridad para proteger tu sistema:
        
        1. Configurar autenticación multifactor en todas las cuentas
        2. Actualizar regularmente el software y sistemas operativos
        3. Implementar un sistema de respaldo automático
        4. Monitorear el acceso a datos sensibles
        5. Establecer políticas de contraseñas seguras
        
        Es importante mantener estas vulnerabilidades bajo control para garantizar la seguridad.
        Deberías considerar realizar auditorías de seguridad periódicas.
        """

        print("📝 Mensaje base de seguridad:")
        print("-" * 50)
        print(base_security_message)
        print()

        # Test 1: Adaptación para NGX PRIME (Ejecutivos)
        print("🔷 TEST 1: Adaptación para NGX PRIME (Ejecutivos)")
        print("-" * 50)

        prime_context = {
            "program_type": "PRIME",
            "user_query": "Necesito una evaluación de seguridad para mi empresa",
            "preferences": {
                "communication_style": "executive",
                "detail_level": "high_level",
            },
            "emotional_state": "focused",
        }

        prime_adapted = await guardian._apply_personality_adaptation(
            base_security_message, prime_context
        )

        print("Respuesta adaptada para PRIME:")
        print(prime_adapted)
        print()

        # Test 2: Adaptación para NGX LONGEVITY (Bienestar)
        print("🔶 TEST 2: Adaptación para NGX LONGEVITY (Bienestar)")
        print("-" * 50)

        longevity_context = {
            "program_type": "LONGEVITY",
            "user_query": "¿Cómo puedo proteger mi información personal?",
            "preferences": {
                "communication_style": "educational",
                "detail_level": "detailed",
            },
            "emotional_state": "concerned",
        }

        longevity_adapted = await guardian._apply_personality_adaptation(
            base_security_message, longevity_context
        )

        print("Respuesta adaptada para LONGEVITY:")
        print(longevity_adapted)
        print()

        # Test 3: Comparación directa de adaptaciones específicas
        print("🔍 TEST 3: Comparación de adaptaciones específicas")
        print("-" * 50)

        test_message = "Esta vulnerabilidad es importante para la seguridad de tu sistema. Te recomiendo implementar medidas de seguridad inmediatamente."

        print("Mensaje original:")
        print(f"'{test_message}'")
        print()

        prime_specific = guardian._apply_guardian_prime_adaptations(test_message)
        print("🔷 PRIME (Ejecutivo):")
        print(f"'{prime_specific}'")
        print()

        longevity_specific = guardian._apply_guardian_longevity_adaptations(
            test_message
        )
        print("🔶 LONGEVITY (Bienestar):")
        print(f"'{longevity_specific}'")
        print()

        # Test 4: Simulación de contextos de cumplimiento
        print("📋 TEST 4: Contextos de cumplimiento normativo")
        print("-" * 50)

        compliance_message = "Para el cumplimiento de GDPR, es importante implementar medidas de protección de datos. Te recomiendo revisar las políticas de privacidad."

        print("Mensaje de cumplimiento original:")
        print(compliance_message)
        print()

        # PRIME - Cumplimiento ejecutivo
        prime_compliance_context = {
            "program_type": "PRIME",
            "user_query": "Necesitamos cumplir con regulaciones empresariales",
            "preferences": {"focus": "regulatory_compliance"},
        }

        prime_compliance = await guardian._apply_personality_adaptation(
            compliance_message, prime_compliance_context
        )

        print("🔷 PRIME - Cumplimiento ejecutivo:")
        print(prime_compliance)
        print()

        # LONGEVITY - Protección personal
        longevity_compliance_context = {
            "program_type": "LONGEVITY",
            "user_query": "¿Cómo proteger mis datos personales?",
            "preferences": {"focus": "personal_protection"},
        }

        longevity_compliance = await guardian._apply_personality_adaptation(
            compliance_message, longevity_compliance_context
        )

        print("🔶 LONGEVITY - Protección personal:")
        print(longevity_compliance)
        print()

        # Test 5: Análisis de características de personalidad
        print("🧠 TEST 5: Características de personalidad GUARDIAN")
        print("-" * 50)

        print("GUARDIAN - The Digital Protector (ISTJ)")
        print("• Personalidad: ISTJ - The Logistician, confiable guardián")
        print("• Voz: Autoridad tranquilizadora")
        print("• PRIME: Protector Digital Ejecutivo")
        print("  - Briefings técnicos de seguridad")
        print("  - Análisis de riesgos de negocio")
        print("  - Cumplimiento regulatorio crítico")
        print("• LONGEVITY: Protector Digital Cálido")
        print("  - Explicaciones educativas de seguridad")
        print("  - Protección personal y familiar")
        print("  - Guía tranquilizadora paso a paso")
        print()

        print(
            "✅ Pruebas de PersonalityAdapter para GUARDIAN completadas exitosamente!"
        )
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()


def test_guardian_adaptations_sync():
    """
    Prueba síncrona de las adaptaciones específicas de GUARDIAN.
    """
    print("🔧 Pruebas síncronas de adaptaciones específicas")
    print("-" * 50)

    try:
        guardian = SecurityComplianceGuardian()

        # Mensajes de prueba
        test_messages = [
            "Te recomiendo implementar contraseñas seguras para proteger tu cuenta.",
            "Esta vulnerabilidad es importante y deberías considerar parcharla inmediatamente.",
            "Para el cumplimiento normativo, es importante seguir las mejores prácticas.",
            "Recomiendo realizar una auditoría de seguridad para identificar riesgos.",
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Mensaje {i}: {message}")

            print("\n🔷 PRIME:")
            prime_result = guardian._apply_guardian_prime_adaptations(message)
            print(prime_result)

            print("\n🔶 LONGEVITY:")
            longevity_result = guardian._apply_guardian_longevity_adaptations(message)
            print(longevity_result)
            print("-" * 30)

    except Exception as e:
        print(f"❌ Error en pruebas síncronas: {e}")


if __name__ == "__main__":
    print("🛡️ GUARDIAN PersonalityAdapter Test Suite")
    print("=" * 70)

    # Ejecutar pruebas síncronas primero
    test_guardian_adaptations_sync()

    print("\n" + "=" * 70)

    # Ejecutar pruebas asíncronas
    asyncio.run(test_guardian_personality_adaptations())
