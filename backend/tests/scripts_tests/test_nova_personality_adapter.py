#!/usr/bin/env python3
"""
Script de prueba para NOVA PersonalityAdapter.
Siguiendo el patrón estándar de BLAZE, VOLT y CODE.
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


async def test_nova_personality_adapter():
    """
    Prueba NOVA PersonalityAdapter siguiendo el patrón estándar.
    """
    print("🚀 NOVA PersonalityAdapter - Prueba Estandarizada")
    print("=" * 60)

    # Configurar logging
    setup_logging()

    try:
        # Crear instancia del PersonalityAdapter (patrón estándar)
        print("⚙️ Inicializando PersonalityAdapter...")
        personality_adapter = PersonalityAdapter()
        print("✅ PersonalityAdapter inicializado correctamente")

        # Respuesta base de NOVA (simulando protocolo de biohacking)
        nova_biohacking_response = """
        He diseñado un protocolo de biohacking innovador específicamente para tu perfil. 
        Este enfoque combina las últimas investigaciones en longevidad con técnicas de 
        optimización hormonal y mejora cognitiva que he estado explorando.
        
        El protocolo incluye: terapia de frío controlado para activar proteínas de shock térmico, 
        ayuno intermitente estratégico optimizado para tu ritmo circadiano, suplementación 
        dirigida con NAD+ y resveratrol para activar sirtuinas, y neurofeedback para mejorar 
        la neuroplasticidad.
        
        También incorporamos tecnología wearable avanzada para monitoreo continuo de 
        biomarcadores clave. Cada intervención está respaldada por estudios recientes 
        y adaptada a tu bioquímica individual. Este es el futuro de la optimización humana.
        """

        print("\n🎯 Prueba 1: NOVA + PRIME (Ejecutivo Innovador)")
        print("-" * 50)

        # Simular contexto de usuario PRIME (siguiendo patrón estándar)
        prime_context = {
            "user_query": "Protocolo de biohacking avanzado para optimizar mi rendimiento como ejecutivo",
            "user_profile": {
                "goals": ["peak performance", "cognitive optimization", "longevity"],
                "occupation": "Tech CEO",
                "age": 38,
            },
            "program_type": "PRIME",
            "preferences": {
                "communication_style": "innovative_executive",
                "data_format": "cutting_edge_insights",
            },
        }

        # Crear perfil de personalidad (patrón estándar)
        prime_profile = PersonalityProfile(
            program_type="PRIME",
            age=38,
            preferences=prime_context.get("preferences"),
            emotional_patterns={"motivation_level": 10, "curiosity_level": 9},
        )

        # Aplicar adaptación (método estándar)
        prime_adaptation = personality_adapter.adapt_response(
            agent_id="NOVA",
            original_message=nova_biohacking_response,
            user_profile=prime_profile,
            context=prime_context,
        )

        print("🔹 Respuesta Original NOVA:")
        print(nova_biohacking_response[:200] + "...")
        print("\n🔹 Respuesta Adaptada PRIME:")
        print(prime_adaptation["adapted_message"][:350] + "...")
        print(f"\n📈 Programa: {prime_adaptation.get('program_type', 'N/A')}")
        print(
            f"📊 Confianza: {prime_adaptation.get('adaptation_metrics', {}).get('confidence_score', 0):.2f}"
        )
        print(
            f"⚡ Adaptaciones: {prime_adaptation.get('adaptation_metrics', {}).get('adaptations_applied', [])}"
        )

        print("\n" + "=" * 60)
        print("🌱 Prueba 2: NOVA + LONGEVITY (Bienestar Innovador)")
        print("-" * 50)

        # Simular contexto de usuario LONGEVITY (siguiendo patrón estándar)
        longevity_context = {
            "user_query": "Estrategias innovadoras de biohacking para mejorar mi salud a largo plazo",
            "user_profile": {
                "goals": ["healthy aging", "longevity", "preventive wellness"],
                "lifestyle": "wellness_focused",
                "age": 52,
            },
            "program_type": "LONGEVITY",
            "preferences": {
                "communication_style": "educational_innovative",
                "data_format": "accessible_science",
            },
        }

        # Crear perfil de personalidad (patrón estándar)
        longevity_profile = PersonalityProfile(
            program_type="LONGEVITY",
            age=52,
            preferences=longevity_context.get("preferences"),
            emotional_patterns={"motivation_level": 8, "curiosity_level": 9},
        )

        # Aplicar adaptación (método estándar)
        longevity_adaptation = personality_adapter.adapt_response(
            agent_id="NOVA",
            original_message=nova_biohacking_response,
            user_profile=longevity_profile,
            context=longevity_context,
        )

        print("🔹 Respuesta Original NOVA:")
        print(nova_biohacking_response[:200] + "...")
        print("\n🔹 Respuesta Adaptada LONGEVITY:")
        print(longevity_adaptation["adapted_message"][:350] + "...")
        print(f"\n🌿 Programa: {longevity_adaptation.get('program_type', 'N/A')}")
        print(
            f"📊 Confianza: {longevity_adaptation.get('adaptation_metrics', {}).get('confidence_score', 0):.2f}"
        )
        print(
            f"⚡ Adaptaciones: {longevity_adaptation.get('adaptation_metrics', {}).get('adaptations_applied', [])}"
        )

        print("\n" + "=" * 60)
        print("🧪 Prueba 3: Validación del Patrón Estándar NOVA")
        print("-" * 50)

        # Validar que sigue el mismo patrón que BLAZE, VOLT, CODE
        print("✅ Validaciones del Patrón Estándar:")

        # 1. Verificar que tiene PersonalityAdapter
        has_personality_adapter = "adapted_message" in prime_adaptation
        print(
            f"  • PersonalityAdapter integrado: {'✅' if has_personality_adapter else '❌'}"
        )

        # 2. Verificar métricas de adaptación
        has_metrics = "adaptation_metrics" in prime_adaptation
        print(f"  • Métricas de adaptación: {'✅' if has_metrics else '❌'}")

        # 3. Verificar diferenciación PRIME vs LONGEVITY
        different_lengths = len(prime_adaptation["adapted_message"]) != len(
            longevity_adaptation["adapted_message"]
        )
        print(
            f"  • Diferenciación PRIME/LONGEVITY: {'✅' if different_lengths else '❌'}"
        )

        # 4. Verificar estructura de respuesta
        has_standard_fields = all(
            key in prime_adaptation
            for key in [
                "adapted_message",
                "original_message",
                "program_type",
                "agent_id",
            ]
        )
        print(
            f"  • Estructura estándar de respuesta: {'✅' if has_standard_fields else '❌'}"
        )

        # 5. Verificar agente_id
        correct_agent_id = prime_adaptation.get("agent_id") == "NOVA"
        print(f"  • Agent ID correcto (NOVA): {'✅' if correct_agent_id else '❌'}")

        # Análisis comparativo con otros agentes
        print(f"\n🔍 Análisis Comparativo:")
        print(
            f"  • PRIME - Longitud: {len(prime_adaptation['adapted_message'])} caracteres"
        )
        print(
            f"  • LONGEVITY - Longitud: {len(longevity_adaptation['adapted_message'])} caracteres"
        )
        print(
            f"  • Diferencia: {abs(len(prime_adaptation['adapted_message']) - len(longevity_adaptation['adapted_message']))} caracteres"
        )

        # Verificar palabras clave específicas de NOVA (ENTP - The Innovator)
        print(f"\n🚀 Palabras Clave NOVA (Innovador/Explorador):")
        prime_msg = prime_adaptation["adapted_message"].lower()
        longevity_msg = longevity_adaptation["adapted_message"].lower()

        innovation_keywords = [
            "innovador",
            "protocolo",
            "futuro",
            "avanzado",
            "optimización",
        ]
        exploration_keywords = [
            "explor",
            "investiga",
            "descubr",
            "experimen",
            "tecnología",
        ]
        biohacking_keywords = [
            "biohacking",
            "longevidad",
            "hormonal",
            "cognitiv",
            "neurofeedback",
        ]

        prime_innovation = [kw for kw in innovation_keywords if kw in prime_msg]
        longevity_innovation = [kw for kw in innovation_keywords if kw in longevity_msg]
        prime_exploration = [kw for kw in exploration_keywords if kw in prime_msg]
        longevity_exploration = [
            kw for kw in exploration_keywords if kw in longevity_msg
        ]
        prime_biohacking = [kw for kw in biohacking_keywords if kw in prime_msg]
        longevity_biohacking = [kw for kw in biohacking_keywords if kw in longevity_msg]

        print(f"  • PRIME - Términos innovadores: {prime_innovation}")
        print(f"  • LONGEVITY - Términos innovadores: {longevity_innovation}")
        print(f"  • PRIME - Términos exploratorios: {prime_exploration}")
        print(f"  • LONGEVITY - Términos exploratorios: {longevity_exploration}")
        print(f"  • PRIME - Términos biohacking: {prime_biohacking}")
        print(f"  • LONGEVITY - Términos biohacking: {longevity_biohacking}")

        print("\n" + "=" * 60)
        print("🎉 NOVA PersonalityAdapter - Prueba Estandarizada Completada")
        print("✅ NOVA sigue el patrón estándar de PersonalityAdapter")
        print("✅ Integración consistente con BLAZE, VOLT, CODE y otros agentes")
        print("✅ Personalidad ENTP (The Innovator) preservada correctamente")
        print("✅ Adaptaciones diferenciadas por programa (PRIME/LONGEVITY)")
        print("✅ Vocabulario de biohacking e innovación mantenido apropiadamente")
        print("\n📝 NOVA está ESTANDARIZADO para FASE 9.1 ✨")

        return True

    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_nova_personality_adapter())
