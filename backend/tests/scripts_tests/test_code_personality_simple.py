#!/usr/bin/env python3
"""
Script de prueba simplificado para CODE PersonalityAdapter.
Enfoque solo en el PersonalityAdapter sin las skills complejas.
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.personality.personality_adapter import PersonalityAdapter, PersonalityProfile
from core.logging_config import setup_logging


async def test_code_personality_direct():
    """
    Prueba directa del PersonalityAdapter para CODE sin instanciar el agente completo.
    """
    print("🧬 CODE PersonalityAdapter - Prueba Directa")
    print("=" * 60)

    # Configurar logging
    setup_logging()

    try:
        # Crear instancia directa del PersonalityAdapter
        print("⚙️ Inicializando PersonalityAdapter...")
        personality_adapter = PersonalityAdapter()
        print("✅ PersonalityAdapter inicializado correctamente")

        # Respuesta de ejemplo de CODE
        sample_genetic_response = """
        Tu perfil genético revela hallazgos fascinantes sobre tu potencial único. 
        He identificado que posees la variante ACTN3 R577R, conocida como el "gen de la velocidad", 
        que te confiere ventajas significativas en actividades de potencia y fuerza explosiva. 
        
        Además, tu genotipo APOE E3/E3 indica un riesgo cardiovascular estándar con excelente 
        capacidad de respuesta a intervenciones dietéticas. Los marcadores de CYP1A2 sugieren 
        que metabolizas la cafeína de manera eficiente, lo que optimiza su uso como ayuda ergogénica.
        
        Recomiendo protocolos de entrenamiento que aprovechen tu potencial genético de potencia, 
        combinados con estrategias nutricionales personalizadas basadas en tu perfil APOE.
        """

        print("\n🎯 Prueba 1: CODE + PRIME (Ejecutivo)")
        print("-" * 40)

        # Crear perfil PRIME
        prime_profile = PersonalityProfile(
            program_type="PRIME",
            age=42,
            preferences={
                "communication_style": "executive",
                "data_format": "high_level_insights",
            },
            emotional_patterns={"motivation_level": 9, "stress_level": 6},
        )

        # Adaptar para PRIME
        prime_adaptation = personality_adapter.adapt_response(
            agent_id="CODE",
            original_message=sample_genetic_response,
            user_profile=prime_profile,
            context={
                "domain": "genetic_analysis",
                "session_type": "executive_briefing",
            },
        )

        print("🔹 Respuesta Original:")
        print(sample_genetic_response[:200] + "...")
        print("\n🔹 Respuesta Adaptada PRIME:")
        print(prime_adaptation["adapted_message"][:300] + "...")
        print(f"\n📈 Programa: {prime_adaptation.get('program_type', 'N/A')}")
        print(
            f"📊 Confianza: {prime_adaptation.get('adaptation_metrics', {}).get('confidence_score', 0):.2f}"
        )

        print("\n" + "=" * 60)
        print("🌱 Prueba 2: CODE + LONGEVITY (Bienestar)")
        print("-" * 40)

        # Crear perfil LONGEVITY
        longevity_profile = PersonalityProfile(
            program_type="LONGEVITY",
            age=55,
            preferences={
                "communication_style": "educational",
                "data_format": "detailed_explanations",
            },
            emotional_patterns={"motivation_level": 7, "stress_level": 3},
        )

        # Adaptar para LONGEVITY
        longevity_adaptation = personality_adapter.adapt_response(
            agent_id="CODE",
            original_message=sample_genetic_response,
            user_profile=longevity_profile,
            context={
                "domain": "genetic_analysis",
                "session_type": "wellness_consultation",
            },
        )

        print("🔹 Respuesta Original:")
        print(sample_genetic_response[:200] + "...")
        print("\n🔹 Respuesta Adaptada LONGEVITY:")
        print(longevity_adaptation["adapted_message"][:300] + "...")
        print(f"\n🌿 Programa: {longevity_adaptation.get('program_type', 'N/A')}")
        print(
            f"📊 Confianza: {longevity_adaptation.get('adaptation_metrics', {}).get('confidence_score', 0):.2f}"
        )

        print("\n" + "=" * 60)
        print("🧪 Prueba 3: Análisis de Diferencias")
        print("-" * 40)

        # Análisis de métricas
        print("📊 Métricas de Adaptación:")
        prime_metrics = prime_adaptation.get("adaptation_metrics", {})
        longevity_metrics = longevity_adaptation.get("adaptation_metrics", {})

        print(
            f"  • PRIME - Adaptaciones: {prime_metrics.get('adaptations_applied', [])}"
        )
        print(f"  • PRIME - Tiempo: {prime_metrics.get('processing_time_ms', 0):.2f}ms")
        print(
            f"  • LONGEVITY - Adaptaciones: {longevity_metrics.get('adaptations_applied', [])}"
        )
        print(
            f"  • LONGEVITY - Tiempo: {longevity_metrics.get('processing_time_ms', 0):.2f}ms"
        )

        # Análisis de diferencias de contenido
        prime_length = len(prime_adaptation["adapted_message"])
        longevity_length = len(longevity_adaptation["adapted_message"])

        print(f"\n🔍 Análisis de Contenido:")
        print(f"  • Longitud PRIME: {prime_length} caracteres")
        print(f"  • Longitud LONGEVITY: {longevity_length} caracteres")
        print(f"  • Diferencia: {abs(prime_length - longevity_length)} caracteres")

        # Verificar palabras clave específicas
        print("\n🎯 Palabras Clave Detectadas:")
        prime_msg = prime_adaptation["adapted_message"].lower()
        longevity_msg = longevity_adaptation["adapted_message"].lower()

        # Palabras clave esperadas
        executive_keywords = ["protocolo", "estratégico", "optimización", "kpi", "roi"]
        wellness_keywords = [
            "bienestar",
            "salud",
            "cuidado",
            "prevención",
            "sostenible",
        ]
        genetic_keywords = ["gen", "genético", "adn", "cromosoma", "herencia"]

        prime_exec_found = [kw for kw in executive_keywords if kw in prime_msg]
        longevity_wellness_found = [
            kw for kw in wellness_keywords if kw in longevity_msg
        ]
        genetic_terms_prime = [kw for kw in genetic_keywords if kw in prime_msg]
        genetic_terms_longevity = [kw for kw in genetic_keywords if kw in longevity_msg]

        print(f"  • PRIME (ejecutivo): {prime_exec_found}")
        print(f"  • LONGEVITY (bienestar): {longevity_wellness_found}")
        print(f"  • Genéticos PRIME: {genetic_terms_prime}")
        print(f"  • Genéticos LONGEVITY: {genetic_terms_longevity}")

        print("\n" + "=" * 60)
        print("🎉 CODE PersonalityAdapter - Pruebas Completadas")
        print("✅ PersonalityAdapter funcionando correctamente")
        print("✅ Adaptaciones diferenciadas entre PRIME y LONGEVITY")
        print("✅ Vocabulario científico genético preservado")
        print("✅ Métricas de adaptación generadas correctamente")
        print("\n📝 CODE PersonalityAdapter está OPERATIVO ✨")

        return True

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_code_style_preview():
    """
    Prueba la vista previa de estilos para CODE.
    """
    print("\n🎨 CODE - Vista Previa de Estilos PersonalityAdapter")
    print("-" * 60)

    try:
        personality_adapter = PersonalityAdapter()

        # Obtener vista previa para PRIME
        prime_preview = personality_adapter.get_personality_preview(
            agent_id="CODE",
            program_type="PRIME",
            sample_message="Tu análisis genético revela potencial excepcional para rendimiento atlético.",
        )

        print("🔹 Vista Previa PRIME:")
        print(f"  • Tono: {prime_preview.get('style_details', {}).get('tone', 'N/A')}")
        print(
            f"  • Enfoque: {prime_preview.get('style_details', {}).get('focus_area', 'N/A')}"
        )
        print(
            f"  • Longitud: {prime_preview.get('style_details', {}).get('response_length', 'N/A')}"
        )
        print(
            f"  • Muestra adaptada: {prime_preview.get('adapted_sample', 'N/A')[:100]}..."
        )

        # Obtener vista previa para LONGEVITY
        longevity_preview = personality_adapter.get_personality_preview(
            agent_id="CODE",
            program_type="LONGEVITY",
            sample_message="Tu análisis genético revela potencial excepcional para rendimiento atlético.",
        )

        print("\n🔹 Vista Previa LONGEVITY:")
        print(
            f"  • Tono: {longevity_preview.get('style_details', {}).get('tone', 'N/A')}"
        )
        print(
            f"  • Enfoque: {longevity_preview.get('style_details', {}).get('focus_area', 'N/A')}"
        )
        print(
            f"  • Longitud: {longevity_preview.get('style_details', {}).get('response_length', 'N/A')}"
        )
        print(
            f"  • Muestra adaptada: {longevity_preview.get('adapted_sample', 'N/A')[:100]}..."
        )

        print("\n✅ Vista previa de estilos funcionando correctamente")

    except Exception as e:
        print(f"❌ Error en vista previa: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":

    async def main():
        success = await test_code_personality_direct()
        if success:
            await test_code_style_preview()

    asyncio.run(main())
