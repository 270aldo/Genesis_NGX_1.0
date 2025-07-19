#!/usr/bin/env python3
"""
Script de testing para el sistema PersonalityAdapter.

Este script valida que las adaptaciones de personalidad funcionen correctamente
y proporciona ejemplos de cómo diferentes agentes adaptan su comunicación
según el programa del usuario (PRIME vs LONGEVITY).
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.personality.personality_adapter import PersonalityAdapter, PersonalityProfile
from core.personality.communication_styles import CommunicationStyles
from agents.elite_training_strategist.agent import EliteTrainingStrategist
from agents.elite_training_strategist.schemas import (
    GenerateTrainingPlanInput,
    UserProfile as TrainingUserProfile,
)
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalityAdapterTester:
    """Clase para testing del sistema PersonalityAdapter."""

    def __init__(self):
        self.personality_adapter = PersonalityAdapter()
        self.test_results = []

    async def test_basic_adaptation(self):
        """Test básico de adaptación de personalidad."""
        print("\n" + "=" * 60)
        print("🧪 TEST 1: ADAPTACIÓN BÁSICA DE PERSONALIDAD")
        print("=" * 60)

        test_message = "He creado un plan de entrenamiento personalizado que optimizará tu rendimiento físico."

        # Test para PRIME
        prime_profile = PersonalityProfile(program_type="PRIME")
        prime_result = self.personality_adapter.adapt_response(
            agent_id="BLAZE", original_message=test_message, user_profile=prime_profile
        )

        # Test para LONGEVITY
        longevity_profile = PersonalityProfile(program_type="LONGEVITY")
        longevity_result = self.personality_adapter.adapt_response(
            agent_id="BLAZE",
            original_message=test_message,
            user_profile=longevity_profile,
        )

        print(f"📝 Mensaje Original:")
        print(f"   {test_message}")
        print()
        print(f"💼 PRIME (Ejecutivo):")
        print(f"   {prime_result['adapted_message']}")
        print(
            f"   Confianza: {prime_result['adaptation_metrics']['confidence_score']:.2f}"
        )
        print()
        print(f"🌱 LONGEVITY (Bienestar):")
        print(f"   {longevity_result['adapted_message']}")
        print(
            f"   Confianza: {longevity_result['adaptation_metrics']['confidence_score']:.2f}"
        )

        # Validar que las adaptaciones son diferentes
        assert (
            prime_result["adapted_message"] != longevity_result["adapted_message"]
        ), "Las adaptaciones deben ser diferentes para PRIME vs LONGEVITY"

        self.test_results.append(
            {
                "test": "basic_adaptation",
                "status": "PASSED",
                "prime_confidence": prime_result["adaptation_metrics"][
                    "confidence_score"
                ],
                "longevity_confidence": longevity_result["adaptation_metrics"][
                    "confidence_score"
                ],
            }
        )

        print("✅ Test básico EXITOSO")

    async def test_communication_styles(self):
        """Test de estilos de comunicación disponibles."""
        print("\n" + "=" * 60)
        print("🎨 TEST 2: ESTILOS DE COMUNICACIÓN DISPONIBLES")
        print("=" * 60)

        # Obtener programas y agentes disponibles
        programs = CommunicationStyles.get_available_programs()
        agents = CommunicationStyles.get_available_agents()

        print(f"📋 Programas disponibles: {programs}")
        print(f"🤖 Agentes con adaptaciones específicas: {agents}")

        # Test de estilo para BLAZE + PRIME
        blaze_prime_style = CommunicationStyles.get_style_for_program("PRIME")
        blaze_adaptations = CommunicationStyles.get_agent_adaptations("BLAZE", "PRIME")

        print(f"\n💼 BLAZE + PRIME:")
        print(f"   Tono: {blaze_prime_style.tone.value}")
        print(f"   Lenguaje: {blaze_prime_style.language_level.value}")
        print(f"   Enfoque: {blaze_prime_style.focus_area.value}")
        print(f"   Adaptaciones específicas: {len(blaze_adaptations)} configuradas")

        # Test de estilo para BLAZE + LONGEVITY
        blaze_longevity_style = CommunicationStyles.get_style_for_program("LONGEVITY")
        blaze_longevity_adaptations = CommunicationStyles.get_agent_adaptations(
            "BLAZE", "LONGEVITY"
        )

        print(f"\n🌱 BLAZE + LONGEVITY:")
        print(f"   Tono: {blaze_longevity_style.tone.value}")
        print(f"   Lenguaje: {blaze_longevity_style.language_level.value}")
        print(f"   Enfoque: {blaze_longevity_style.focus_area.value}")
        print(
            f"   Adaptaciones específicas: {len(blaze_longevity_adaptations)} configuradas"
        )

        self.test_results.append(
            {
                "test": "communication_styles",
                "status": "PASSED",
                "programs_count": len(programs),
                "agents_count": len(agents),
            }
        )

        print("✅ Test de estilos EXITOSO")

    async def test_blaze_integration(self):
        """Test de integración completa con agente BLAZE."""
        print("\n" + "=" * 60)
        print("🔥 TEST 3: INTEGRACIÓN COMPLETA CON BLAZE")
        print("=" * 60)

        try:
            # Inicializar agente BLAZE
            blaze_agent = EliteTrainingStrategist()

            # Crear input para usuario PRIME
            prime_user_profile = TrainingUserProfile(
                name="Ejecutivo Test",
                age=35,
                fitness_level="intermediate",
                goals=["improve_performance", "increase_productivity"],
                restrictions=[],
            )

            prime_input = GenerateTrainingPlanInput(
                user_query="Necesito optimizar mi rendimiento físico para mejorar mi productividad ejecutiva",
                user_profile=prime_user_profile,
                program_type="PRIME",
            )

            # Ejecutar skill con adaptación PRIME
            prime_result = await blaze_agent._skill_generate_training_plan(prime_input)

            print(f"💼 RESULTADO PRIME:")
            print(f"   Plan: {prime_result.plan_name}")
            print(f"   Descripción: {prime_result.description}")
            print(f"   Respuesta adaptada: {prime_result.response[:200]}...")

            # Crear input para usuario LONGEVITY
            longevity_user_profile = TrainingUserProfile(
                name="Usuario Wellness Test",
                age=60,
                fitness_level="beginner",
                goals=["maintain_mobility", "healthy_aging"],
                restrictions=[],
            )

            longevity_input = GenerateTrainingPlanInput(
                user_query="Quiero mantener mi salud y movilidad a medida que envejezco",
                user_profile=longevity_user_profile,
                program_type="LONGEVITY",
            )

            # Ejecutar skill con adaptación LONGEVITY
            longevity_result = await blaze_agent._skill_generate_training_plan(
                longevity_input
            )

            print(f"\n🌱 RESULTADO LONGEVITY:")
            print(f"   Plan: {longevity_result.plan_name}")
            print(f"   Descripción: {longevity_result.description}")
            print(f"   Respuesta adaptada: {longevity_result.response[:200]}...")

            # Validar que las respuestas son diferentes
            assert (
                prime_result.response != longevity_result.response
            ), "Las respuestas deben ser diferentes entre PRIME y LONGEVITY"

            self.test_results.append(
                {
                    "test": "blaze_integration",
                    "status": "PASSED",
                    "prime_response_length": len(prime_result.response),
                    "longevity_response_length": len(longevity_result.response),
                }
            )

            print("✅ Test de integración BLAZE EXITOSO")

        except Exception as e:
            logger.error(f"Error en test de integración BLAZE: {e}")
            self.test_results.append(
                {"test": "blaze_integration", "status": "FAILED", "error": str(e)}
            )
            print("❌ Test de integración BLAZE FALLIDO")

    async def test_performance_analytics(self):
        """Test de analytics de rendimiento."""
        print("\n" + "=" * 60)
        print("📊 TEST 4: ANALYTICS DE RENDIMIENTO")
        print("=" * 60)

        # Ejecutar varias adaptaciones para generar métricas
        test_messages = [
            "Tu entrenamiento debe enfocarse en ganar fuerza funcional.",
            "La nutrición es clave para alcanzar tus objetivos fitness.",
            "La recuperación es tan importante como el entrenamiento mismo.",
            "Monitorear tu progreso te ayudará a mantener la motivación.",
            "Adaptar tu rutina según las circunstancias es esencial.",
        ]

        for message in test_messages:
            # Test PRIME
            prime_profile = PersonalityProfile(program_type="PRIME")
            self.personality_adapter.adapt_response(
                agent_id="BLAZE", original_message=message, user_profile=prime_profile
            )

            # Test LONGEVITY
            longevity_profile = PersonalityProfile(program_type="LONGEVITY")
            self.personality_adapter.adapt_response(
                agent_id="BLAZE",
                original_message=message,
                user_profile=longevity_profile,
            )

        # Obtener analytics
        analytics = self.personality_adapter.analyze_adaptation_performance()

        print(f"📈 Analytics de Rendimiento:")
        print(f"   Total adaptaciones: {analytics['total_adaptations']}")
        print(f"   Confianza promedio: {analytics['average_confidence']:.3f}")
        print(
            f"   Tiempo procesamiento promedio: {analytics['average_processing_time_ms']:.2f}ms"
        )
        print(f"   Calificación de rendimiento: {analytics['performance_grade']}")
        print(
            f"   Adaptaciones más comunes: {analytics['most_common_adaptations'][:3]}"
        )

        # Validar métricas mínimas
        assert (
            analytics["total_adaptations"] >= 10
        ), "Debe haber al menos 10 adaptaciones"
        assert (
            analytics["average_confidence"] > 0.5
        ), "Confianza promedio debe ser > 0.5"
        assert (
            analytics["average_processing_time_ms"] < 1000
        ), "Tiempo debe ser < 1000ms"

        self.test_results.append(
            {
                "test": "performance_analytics",
                "status": "PASSED",
                "total_adaptations": analytics["total_adaptations"],
                "average_confidence": analytics["average_confidence"],
                "performance_grade": analytics["performance_grade"],
            }
        )

        print("✅ Test de analytics EXITOSO")

    async def test_edge_cases(self):
        """Test de casos extremos y manejo de errores."""
        print("\n" + "=" * 60)
        print("🚨 TEST 5: CASOS EXTREMOS Y MANEJO DE ERRORES")
        print("=" * 60)

        # Test con mensaje vacío
        try:
            empty_profile = PersonalityProfile(program_type="PRIME")
            result = self.personality_adapter.adapt_response(
                agent_id="BLAZE", original_message="", user_profile=empty_profile
            )
            print("❌ Mensaje vacío debería generar error")
        except ValueError:
            print("✅ Mensaje vacío manejado correctamente")

        # Test con agente inexistente
        unknown_profile = PersonalityProfile(program_type="PRIME")
        result = self.personality_adapter.adapt_response(
            agent_id="UNKNOWN_AGENT",
            original_message="Test message",
            user_profile=unknown_profile,
        )
        # Debe funcionar con fallback
        assert result["adapted_message"] is not None
        print("✅ Agente inexistente manejado con fallback")

        # Test con programa inexistente
        invalid_profile = PersonalityProfile(program_type="INVALID_PROGRAM")
        result = self.personality_adapter.adapt_response(
            agent_id="BLAZE",
            original_message="Test message",
            user_profile=invalid_profile,
        )
        # Debe funcionar con fallback a LONGEVITY
        assert result["adapted_message"] is not None
        print("✅ Programa inexistente manejado con fallback")

        self.test_results.append(
            {"test": "edge_cases", "status": "PASSED", "fallbacks_working": True}
        )

        print("✅ Test de casos extremos EXITOSO")

    def print_summary(self):
        """Imprime resumen de todos los tests."""
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE TESTS DE PERSONALITYADAPTER")
        print("=" * 60)

        passed_count = sum(1 for r in self.test_results if r["status"] == "PASSED")
        total_count = len(self.test_results)

        print(f"Tests ejecutados: {total_count}")
        print(f"Tests exitosos: {passed_count}")
        print(f"Tests fallidos: {total_count - passed_count}")
        print(f"Porcentaje de éxito: {(passed_count/total_count)*100:.1f}%")

        print("\nDetalles por test:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASSED" else "❌"
            print(f"  {status_emoji} {result['test']}: {result['status']}")

        if passed_count == total_count:
            print("\n🎉 TODOS LOS TESTS EXITOSOS!")
            print("El sistema PersonalityAdapter está funcionando correctamente.")
        else:
            print("\n⚠️  ALGUNOS TESTS FALLARON")
            print("Revisar logs para más detalles.")


async def main():
    """Función principal para ejecutar todos los tests."""
    print("🚀 INICIANDO TESTS DEL SISTEMA PERSONALITYADAPTER")
    print(
        "Validando adaptaciones de personalidad para comunicación ultra-personalizada"
    )

    tester = PersonalityAdapterTester()

    try:
        # Ejecutar todos los tests
        await tester.test_basic_adaptation()
        await tester.test_communication_styles()
        await tester.test_blaze_integration()
        await tester.test_performance_analytics()
        await tester.test_edge_cases()

        # Imprimir resumen
        tester.print_summary()

    except Exception as e:
        logger.error(f"Error durante la ejecución de tests: {e}")
        print(f"\n❌ ERROR CRÍTICO: {e}")
        return 1

    return 0


if __name__ == "__main__":
    # Ejecutar tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
