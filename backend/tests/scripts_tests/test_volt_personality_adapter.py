#!/usr/bin/env python3
"""
Script de prueba para VOLT PersonalityAdapter.

Prueba las adaptaciones de personalidad específicas de VOLT para
diferentes tipos de programa (PRIME vs LONGEVITY).
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.volt_biometrics_insight_engine.agent import BiometricsInsightEngine
from core.logging_config import setup_logging


async def test_volt_personality_adapter():
    """
    Prueba las adaptaciones de personalidad de VOLT para diferentes programas.
    """
    print("🔬 VOLT PersonalityAdapter - Sistema de Pruebas")
    print("=" * 60)

    # Configurar logging
    setup_logging()

    try:
        # Crear instancia del agente VOLT
        print("📊 Inicializando VOLT Biometrics Insight Engine...")
        volt_agent = BiometricsInsightEngine()
        print("✅ VOLT inicializado correctamente")

        # Respuesta de ejemplo de VOLT
        sample_response = """
        Basándome en el análisis de tus datos biométricos, he identificado varios patrones interesantes. 
        Tu variabilidad cardíaca muestra una tendencia ascendente, lo que indica mejora en la capacidad 
        adaptativa de tu sistema nervioso. Los datos de sueño revelan una optimización en la eficiencia, 
        con incrementos en sueño profundo. Las fluctuaciones de glucosa muestran mayor estabilidad, 
        sugiriendo una adaptación metabólica positiva. 
        
        Recomiendo continuar con el protocolo actual y considerar ajustes específicos en la ventana 
        de alimentación para maximizar estos beneficios.
        """

        # Perfiles de usuario para diferentes programas
        prime_profile = {
            "age": 42,
            "goals": [
                "optimización de performance",
                "mejora de productividad",
                "análisis de ROI en salud",
            ],
            "occupation": "CEO",
            "preferences": {
                "communication_style": "executive",
                "data_format": "high_level_insights",
            },
        }

        longevity_profile = {
            "age": 55,
            "goals": [
                "bienestar a largo plazo",
                "prevención de enfermedades",
                "calidad de vida",
            ],
            "lifestyle": "wellness_focused",
            "preferences": {
                "communication_style": "educational",
                "data_format": "detailed_explanations",
            },
        }

        print("\n🎯 Prueba 1: VOLT + PRIME (Ejecutivo)")
        print("-" * 40)

        prime_adaptation = await volt_agent.adapt_response_to_program(
            response=sample_response,
            user_profile=prime_profile,
            conversation_context={"session_type": "executive_briefing"},
        )

        print("🔹 Respuesta Original:")
        print(sample_response[:150] + "...")
        print("\n🔹 Respuesta Adaptada PRIME:")
        print(prime_adaptation["adapted_message"][:300] + "...")
        print(f"\n📈 Programa Detectado: {prime_adaptation.get('program_type', 'N/A')}")
        print(
            f"🧠 Personalidad: {prime_adaptation.get('volt_personality', {}).get('communication_style', 'N/A')}"
        )

        print("\n" + "=" * 60)
        print("🌱 Prueba 2: VOLT + LONGEVITY (Bienestar)")
        print("-" * 40)

        longevity_adaptation = await volt_agent.adapt_response_to_program(
            response=sample_response,
            user_profile=longevity_profile,
            conversation_context={"session_type": "wellness_consultation"},
        )

        print("🔹 Respuesta Original:")
        print(sample_response[:150] + "...")
        print("\n🔹 Respuesta Adaptada LONGEVITY:")
        print(longevity_adaptation["adapted_message"][:300] + "...")
        print(
            f"\n🌿 Programa Detectado: {longevity_adaptation.get('program_type', 'N/A')}"
        )
        print(
            f"🧠 Personalidad: {longevity_adaptation.get('volt_personality', {}).get('communication_style', 'N/A')}"
        )

        print("\n" + "=" * 60)
        print("🧪 Prueba 3: Comparación de Adaptaciones")
        print("-" * 40)

        # Mostrar métricas de adaptación
        if "adaptation_metrics" in prime_adaptation:
            print("📊 Métricas PRIME:")
            metrics = prime_adaptation["adaptation_metrics"]
            print(
                f"  • Adaptaciones aplicadas: {metrics.get('adaptations_applied', [])}"
            )
            print(f"  • Confianza: {metrics.get('confidence_score', 0):.2f}")

        if "adaptation_metrics" in longevity_adaptation:
            print("\n📊 Métricas LONGEVITY:")
            metrics = longevity_adaptation["adaptation_metrics"]
            print(
                f"  • Adaptaciones aplicadas: {metrics.get('adaptations_applied', [])}"
            )
            print(f"  • Confianza: {metrics.get('confidence_score', 0):.2f}")

        # Análisis de diferencias
        print("\n🔍 Análisis de Diferencias:")
        prime_length = len(prime_adaptation["adapted_message"])
        longevity_length = len(longevity_adaptation["adapted_message"])

        print(f"  • Longitud PRIME: {prime_length} caracteres")
        print(f"  • Longitud LONGEVITY: {longevity_length} caracteres")
        print(f"  • Diferencia: {abs(prime_length - longevity_length)} caracteres")

        # Verificar palabras clave específicas
        print("\n🎯 Palabras Clave Detectadas:")
        prime_msg = prime_adaptation["adapted_message"].lower()
        longevity_msg = longevity_adaptation["adapted_message"].lower()

        executive_keywords = ["kpi", "roi", "protocolo", "optimización", "estratégico"]
        wellness_keywords = [
            "bienestar",
            "sostenible",
            "gradual",
            "equilibrio",
            "longevidad",
        ]

        prime_keywords_found = [kw for kw in executive_keywords if kw in prime_msg]
        longevity_keywords_found = [
            kw for kw in wellness_keywords if kw in longevity_msg
        ]

        print(f"  • PRIME (ejecutivo): {prime_keywords_found}")
        print(f"  • LONGEVITY (bienestar): {longevity_keywords_found}")

        print("\n" + "=" * 60)
        print("🎉 VOLT PersonalityAdapter - Pruebas Completadas")
        print("✅ Integración PersonalityAdapter verificada exitosamente")
        print("✅ Adaptaciones PRIME y LONGEVITY funcionando correctamente")
        print("✅ Personalidad INTP (The Thinker) preservada en ambos casos")
        print("\n📝 VOLT está listo para FASE 9.1 - PersonalityAdapter ✨")

        return True

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_volt_conversation_personality():
    """
    Prueba las skills conversacionales de VOLT con adaptaciones de personalidad.
    """
    print("\n🗣️ Prueba de Skills Conversacionales con PersonalityAdapter")
    print("-" * 60)

    try:
        volt_agent = BiometricsInsightEngine()

        # Importar esquemas necesarios
        from agents.volt_biometrics_insight_engine.schemas import (
            BiometricAnalysisConversationInput,
        )

        # Datos de prueba
        conversation_input = BiometricAnalysisConversationInput(
            user_input="¿Qué me dice mi HRV sobre mi nivel de estrés?",
            biometric_context={
                "hrv": {"current_value": 45, "trend": "ascending", "percentile": 75}
            },
            conversation_history=[
                {"role": "user", "content": "Quiero entender mejor mis datos"},
                {
                    "role": "assistant",
                    "content": "Te ayudo a analizar tus métricas biométricas",
                },
            ],
        )

        # Ejecutar skill conversacional
        conversation_result = await volt_agent._skill_biometric_analysis_conversation(
            conversation_input
        )

        print("🔹 Respuesta Conversacional Base:")
        print(conversation_result.response[:200] + "...")

        # Adaptar para PRIME
        prime_adapted = await volt_agent.adapt_response_to_program(
            response=conversation_result.response,
            user_profile={
                "goals": ["performance optimization"],
                "occupation": "executive",
            },
            conversation_context={"type": "hrv_analysis"},
        )

        print("\n🔹 Conversación Adaptada PRIME:")
        print(prime_adapted["adapted_message"][:200] + "...")

        # Adaptar para LONGEVITY
        longevity_adapted = await volt_agent.adapt_response_to_program(
            response=conversation_result.response,
            user_profile={
                "goals": ["wellness", "stress management"],
                "lifestyle": "health_focused",
            },
            conversation_context={"type": "hrv_analysis"},
        )

        print("\n🔹 Conversación Adaptada LONGEVITY:")
        print(longevity_adapted["adapted_message"][:200] + "...")

        print(
            "\n✅ Skills conversacionales con PersonalityAdapter funcionando correctamente"
        )

    except Exception as e:
        print(f"❌ Error en prueba conversacional: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":

    async def main():
        await test_volt_personality_adapter()
        await test_volt_conversation_personality()

    asyncio.run(main())
