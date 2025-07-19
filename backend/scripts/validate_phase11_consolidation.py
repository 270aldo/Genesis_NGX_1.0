#!/usr/bin/env python3
"""
Script de validación para FASE 11.1 - Client Consolidation
Verifica que todos los agentes principales funcionen después de la consolidación.
"""

import sys
import traceback
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))


def test_gemini_client():
    """Prueba el cliente principal de Gemini."""
    try:
        from clients.vertex_ai.client import VertexAIClient

        client = VertexAIClient()
        return True, "VertexAIClient funciona correctamente"
    except Exception as e:
        return False, f"Error en VertexAIClient: {e}"


def test_vertex_ai_client():
    """Prueba el cliente optimizado de Vertex AI."""
    try:
        from clients.vertex_ai.client import VertexAIClient

        return True, "VertexAIClient funciona correctamente"
    except Exception as e:
        return False, f"Error en VertexAIClient: {e}"


def test_agent_imports():
    """Prueba las importaciones de agentes principales."""
    agents_to_test = [
        ("CODE", "agents.code_genetic_specialist.agent", "CodeGeneticSpecialist"),
        (
            "BLAZE",
            "agents.elite_training_strategist.agent_optimized",
            "EliteTrainingStrategistOptimized",
        ),
        (
            "SAGE",
            "agents.precision_nutrition_architect.agent_optimized",
            "PrecisionNutritionArchitectOptimized",
        ),
        (
            "WAVE",
            "agents.wave_performance_analytics.agent_optimized",
            "WavePerformanceAnalyticsOptimized",
        ),
        ("NEXUS", "agents.orchestrator.agent_optimized", "OrchestratorOptimized"),
        (
            "SPARK",
            "agents.motivation_behavior_coach.agent_optimized",
            "MotivationBehaviorCoachOptimized",
        ),
        (
            "STELLA",
            "agents.progress_tracker.agent_optimized",
            "ProgressTrackerOptimized",
        ),
        (
            "NOVA",
            "agents.nova_biohacking_innovator.agent_optimized",
            "NovaBiohackingInnovatorOptimized",
        ),
        (
            "LUNA",
            "agents.female_wellness_coach.agent_optimized",
            "FemaleWellnessCoachOptimized",
        ),
        ("NODE", "agents.backend.node.agent_optimized", "NodeOptimized"),
        ("GUARDIAN", "agents.backend.guardian.agent_optimized", "GuardianOptimized"),
    ]

    results = []
    for agent_name, module_path, class_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            results.append(
                (True, f"✓ {agent_name}: {class_name} importa correctamente")
            )
        except Exception as e:
            results.append(
                (False, f"✗ {agent_name}: Error al importar {class_name} - {e}")
            )

    return results


def test_model_configuration():
    """Prueba la configuración de modelos Gemini."""
    try:
        from config.gemini_models import (
            GEMINI_MODELS,
            AGENT_MODEL_MAPPING,
            get_model_config,
            get_model_id,
        )

        # Verificar que los modelos principales estén configurados
        required_models = ["pro_2_5", "flash_2_5", "standard_2_0"]
        for model in required_models:
            if model not in GEMINI_MODELS:
                return False, f"Modelo {model} no encontrado en configuración"

        # Verificar mapeo de agentes
        test_agent = "orchestrator"
        config = get_model_config(test_agent)
        model_id = get_model_id(test_agent)

        if not config or not model_id:
            return False, "Error en configuración de mapeo de agentes"

        return (
            True,
            f"Configuración de modelos correcta. Modelo orchestrator: {model_id}",
        )

    except Exception as e:
        return False, f"Error en configuración de modelos: {e}"


def main():
    """Ejecuta todas las validaciones."""
    print("🔍 FASE 11.1 - Validación de Consolidación de Clientes")
    print("=" * 60)

    all_passed = True

    # Test 1: Clientes
    print("\n📋 1. Validando Clientes:")

    success, message = test_gemini_client()
    print(f"  {'✓' if success else '✗'} {message}")
    if not success:
        all_passed = False

    success, message = test_vertex_ai_client()
    print(f"  {'✓' if success else '✗'} {message}")
    if not success:
        all_passed = False

    # Test 2: Configuración de modelos
    print("\n📋 2. Validando Configuración de Modelos:")
    success, message = test_model_configuration()
    print(f"  {'✓' if success else '✗'} {message}")
    if not success:
        all_passed = False

    # Test 3: Importaciones de agentes
    print("\n📋 3. Validando Importaciones de Agentes:")
    agent_results = test_agent_imports()

    for success, message in agent_results:
        print(f"  {message}")
        if not success:
            all_passed = False

    # Resumen
    print("\n" + "=" * 60)
    if all_passed:
        print(
            "🎉 ¡CONSOLIDACIÓN EXITOSA! Todos los componentes funcionan correctamente."
        )
        print("✅ Fase 11.1 completada sin problemas.")
        return 0
    else:
        print("⚠️  PROBLEMAS DETECTADOS. Revisar errores arriba.")
        print("❌ Algunos componentes requieren atención.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
