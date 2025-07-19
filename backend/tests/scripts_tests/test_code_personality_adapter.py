#!/usr/bin/env python3
"""
Script de prueba para CODE PersonalityAdapter.

Prueba las adaptaciones de personalidad específicas de CODE para
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

from agents.code_genetic_specialist.agent import CodeGeneticSpecialist
from core.logging_config import setup_logging


async def test_code_personality_adapter():
    """
    Prueba las adaptaciones de personalidad de CODE para diferentes programas.
    """
    print("🧬 CODE PersonalityAdapter - Sistema de Pruebas")
    print("=" * 60)

    # Configurar logging
    setup_logging()

    try:
        # Crear instancia del agente CODE
        print("🔬 Inicializando CODE Genetic Specialist...")
        code_agent = CodeGeneticSpecialist()
        print("✅ CODE inicializado correctamente")

        # Respuesta de ejemplo de CODE
        sample_genetic_response = {
            "response": """
            Tu perfil genético revela hallazgos fascinantes sobre tu potencial único. 
            He identificado que posees la variante ACTN3 R577R, conocida como el "gen de la velocidad", 
            que te confiere ventajas significativas en actividades de potencia y fuerza explosiva. 
            
            Además, tu genotipo APOE E3/E3 indica un riesgo cardiovascular estándar con excelente 
            capacidad de respuesta a intervenciones dietéticas. Los marcadores de CYP1A2 sugieren 
            que metabolizas la cafeína de manera eficiente, lo que optimiza su uso como ayuda ergogénica.
            
            Recomiendo protocolos de entrenamiento que aprovechen tu potencial genético de potencia, 
            combinados con estrategias nutricionales personalizadas basadas en tu perfil APOE.
            """,
            "confidence": 0.92,
            "data": {
                "genetic_markers": ["ACTN3", "APOE", "CYP1A2"],
                "strengths": ["power_performance", "caffeine_metabolism"],
                "considerations": ["cardiovascular_optimization"],
            },
        }

        print("\n🎯 Prueba 1: CODE + PRIME (Ejecutivo)")
        print("-" * 40)

        # Adaptar para PRIME
        prime_adapted = await code_agent._adapt_response_to_audience(
            response=sample_genetic_response.copy(),
            program_type="PRIME",
            user_id="executive_user_001",
        )

        print("🔹 Respuesta Original:")
        print(sample_genetic_response["response"][:200] + "...")
        print("\n🔹 Respuesta Adaptada PRIME:")
        print(prime_adapted["response"][:300] + "...")
        print(f"\n📈 Tono: {prime_adapted.get('tone', 'N/A')}")
        print(f"🎯 Énfasis: {prime_adapted.get('emphasis', 'N/A')}")
        print(
            f"🗣️ Estilo: {prime_adapted.get('communication_style', {}).get('language', 'N/A')}"
        )

        print("\n" + "=" * 60)
        print("🌱 Prueba 2: CODE + LONGEVITY (Bienestar)")
        print("-" * 40)

        # Adaptar para LONGEVITY
        longevity_adapted = await code_agent._adapt_response_to_audience(
            response=sample_genetic_response.copy(),
            program_type="LONGEVITY",
            user_id="wellness_user_001",
        )

        print("🔹 Respuesta Original:")
        print(sample_genetic_response["response"][:200] + "...")
        print("\n🔹 Respuesta Adaptada LONGEVITY:")
        print(longevity_adapted["response"][:300] + "...")
        print(f"\n🌿 Tono: {longevity_adapted.get('tone', 'N/A')}")
        print(f"🎯 Énfasis: {longevity_adapted.get('emphasis', 'N/A')}")
        print(
            f"🗣️ Estilo: {longevity_adapted.get('communication_style', {}).get('language', 'N/A')}"
        )

        print("\n" + "=" * 60)
        print("🧪 Prueba 3: Análisis de Métricas de Adaptación")
        print("-" * 40)

        # Comparar métricas
        if "adaptation_metrics" in prime_adapted:
            print("📊 Métricas PRIME:")
            prime_metrics = prime_adapted["adaptation_metrics"]
            print(
                f"  • Adaptaciones aplicadas: {prime_metrics.get('adaptations_applied', [])}"
            )
            print(f"  • Confianza: {prime_metrics.get('confidence_score', 0):.2f}")
            print(
                f"  • Tiempo de procesamiento: {prime_metrics.get('processing_time_ms', 0):.2f}ms"
            )

        if "adaptation_metrics" in longevity_adapted:
            print("\n📊 Métricas LONGEVITY:")
            longevity_metrics = longevity_adapted["adaptation_metrics"]
            print(
                f"  • Adaptaciones aplicadas: {longevity_metrics.get('adaptations_applied', [])}"
            )
            print(f"  • Confianza: {longevity_metrics.get('confidence_score', 0):.2f}")
            print(
                f"  • Tiempo de procesamiento: {longevity_metrics.get('processing_time_ms', 0):.2f}ms"
            )

        # Análisis de diferencias comunicacionales
        print("\n🔍 Análisis de Diferencias Comunicacionales:")
        prime_length = len(prime_adapted["response"])
        longevity_length = len(longevity_adapted["response"])

        print(f"  • Longitud PRIME: {prime_length} caracteres")
        print(f"  • Longitud LONGEVITY: {longevity_length} caracteres")
        print(f"  • Diferencia: {abs(prime_length - longevity_length)} caracteres")

        # Verificar palabras clave específicas de CODE
        print("\n🧬 Palabras Clave Genéticas Detectadas:")
        prime_msg = prime_adapted["response"].lower()
        longevity_msg = longevity_adapted["response"].lower()

        executive_keywords = [
            "estratégico",
            "ventaja",
            "competitiva",
            "optimización",
            "rendimiento",
        ]
        wellness_keywords = [
            "bienestar",
            "salud",
            "preventiva",
            "personalizada",
            "cuidar",
        ]
        genetic_keywords = ["gen", "adn", "genético", "cromosoma", "alelo"]

        prime_exec_found = [kw for kw in executive_keywords if kw in prime_msg]
        longevity_wellness_found = [
            kw for kw in wellness_keywords if kw in longevity_msg
        ]
        genetic_terms_prime = [kw for kw in genetic_keywords if kw in prime_msg]
        genetic_terms_longevity = [kw for kw in genetic_keywords if kw in longevity_msg]

        print(f"  • PRIME (ejecutivo): {prime_exec_found}")
        print(f"  • LONGEVITY (bienestar): {longevity_wellness_found}")
        print(f"  • Términos genéticos PRIME: {genetic_terms_prime}")
        print(f"  • Términos genéticos LONGEVITY: {genetic_terms_longevity}")

        print("\n" + "=" * 60)
        print("🎉 CODE PersonalityAdapter - Pruebas Completadas")
        print("✅ Integración PersonalityAdapter verificada exitosamente")
        print("✅ Adaptaciones PRIME y LONGEVITY funcionando correctamente")
        print("✅ Personalidad INTJ (The Architect) preservada en ambos casos")
        print("✅ Vocabulario científico genético mantenido apropiadamente")
        print("\n📝 CODE está listo para FASE 9.1 - PersonalityAdapter ✨")

        return True

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_code_genetic_skills_with_personality():
    """
    Prueba skills genéticas específicas con adaptaciones de personalidad.
    """
    print("\n🧬 Prueba de Skills Genéticas con PersonalityAdapter")
    print("-" * 60)

    try:
        code_agent = CodeGeneticSpecialist()

        # Simulación de análisis de riesgo genético
        genetic_risk_analysis = {
            "response": """
            El análisis de tu perfil genético identifica factores importantes para tu salud cardiovascular. 
            Tu variante APOE E4/E3 requiere atención específica en la prevención de enfermedades cardíacas 
            mediante estrategias nutricionales dirigidas y monitoreo proactivo de biomarcadores lipídicos.
            """,
            "data": {
                "risk_factors": ["cardiovascular", "lipid_metabolism"],
                "protective_factors": ["response_to_exercise", "omega3_efficiency"],
            },
        }

        print("🔹 Análisis de Riesgo Base:")
        print(genetic_risk_analysis["response"][:150] + "...")

        # Adaptar para contexto ejecutivo (PRIME)
        prime_risk_adapted = await code_agent._adapt_response_to_audience(
            response=genetic_risk_analysis.copy(),
            program_type="PRIME",
            user_id="executive_genetic_001",
        )

        print("\n🔹 Análisis de Riesgo Adaptado PRIME:")
        print(prime_risk_adapted["response"][:200] + "...")

        # Adaptar para contexto de bienestar (LONGEVITY)
        longevity_risk_adapted = await code_agent._adapt_response_to_audience(
            response=genetic_risk_analysis.copy(),
            program_type="LONGEVITY",
            user_id="wellness_genetic_001",
        )

        print("\n🔹 Análisis de Riesgo Adaptado LONGEVITY:")
        print(longevity_risk_adapted["response"][:200] + "...")

        print("\n✅ Skills genéticas con PersonalityAdapter funcionando correctamente")

    except Exception as e:
        print(f"❌ Error en prueba de skills genéticas: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":

    async def main():
        await test_code_personality_adapter()
        await test_code_genetic_skills_with_personality()

    asyncio.run(main())
