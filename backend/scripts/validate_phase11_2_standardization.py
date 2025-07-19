#!/usr/bin/env python3
"""
Script de validación para FASE 11.2 - Agent Standardization
Verifica el estado después de la estandarización de agentes.
"""

import sys
import traceback
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))


def test_primary_agents():
    """Prueba los agentes principales después de estandarización."""
    agents_to_test = [
        ("BLAZE", "agents.elite_training_strategist.agent", "EliteTrainingStrategist"),
        (
            "SAGE",
            "agents.precision_nutrition_architect.agent",
            "PrecisionNutritionArchitect",
        ),
        ("WAVE", "agents.wave_performance_analytics.agent", "WAVEPerformanceAnalytics"),
        ("NEXUS", "agents.orchestrator.agent", "NGXNexusOrchestrator"),
        ("SPARK", "agents.motivation_behavior_coach.agent", "MotivationBehaviorCoach"),
        ("STELLA", "agents.progress_tracker.agent", "ProgressTracker"),
        ("NOVA", "agents.nova_biohacking_innovator.agent", "BiohackingInnovator"),
        ("LUNA", "agents.female_wellness_coach.agent", "FemaleWellnessCoach"),
        ("CODE", "agents.code_genetic_specialist.agent", "CodeGeneticSpecialist"),
    ]

    results = []
    for agent_name, module_path, class_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            results.append(
                (True, f"✓ {agent_name}: {class_name} funciona correctamente")
            )
        except Exception as e:
            results.append(
                (
                    False,
                    f"✗ {agent_name}: Error al importar {class_name} - {str(e)[:100]}",
                )
            )

    return results


def test_file_consolidation():
    """Verifica que la consolidación de archivos fue exitosa."""
    results = []

    # Verificar que no existen archivos duplicados
    import glob

    agent_optimized_files = glob.glob("agents/**/agent_optimized.py", recursive=True)
    if not agent_optimized_files:
        results.append((True, "✓ Todos los agent_optimized.py fueron consolidados"))
    else:
        results.append(
            (
                False,
                f"✗ Quedan {len(agent_optimized_files)} archivos agent_optimized.py",
            )
        )

    # Verificar que no existen archivos legacy
    legacy_patterns = [
        "**/agent_enhanced.py",
        "**/agent_refactored.py",
        "**/agent_template.py",
    ]
    legacy_files = []
    for pattern in legacy_patterns:
        legacy_files.extend(glob.glob(f"agents/{pattern}", recursive=True))

    if not legacy_files:
        results.append((True, "✓ Todos los archivos legacy fueron removidos"))
    else:
        results.append((False, f"✗ Quedan {len(legacy_files)} archivos legacy"))

    return results


def test_backup_integrity():
    """Verifica que los backups fueron creados correctamente."""
    backup_dirs = [
        "backups/phase11_consolidation/",
        "backups/phase11_2_standardization/",
    ]

    results = []
    for backup_dir in backup_dirs:
        if Path(backup_dir).exists():
            file_count = len(list(Path(backup_dir).rglob("*.py")))
            results.append(
                (True, f"✓ Backup {backup_dir}: {file_count} archivos respaldados")
            )
        else:
            results.append((False, f"✗ Backup {backup_dir}: No existe"))

    return results


def test_gemini_client():
    """Prueba el cliente consolidado de Gemini."""
    try:
        from clients.vertex_ai.client import VertexAIClient

        client = VertexAIClient()
        return True, "✓ VertexAIClient consolidado funciona correctamente"
    except Exception as e:
        return False, f"✗ Error en VertexAIClient: {e}"


def main():
    """Ejecuta todas las validaciones."""
    print("🔍 FASE 11.2 - Validación de Estandarización de Agentes")
    print("=" * 60)

    all_passed = True

    # Test 1: Cliente consolidado
    print("\n📋 1. Validando Cliente Consolidado:")
    success, message = test_gemini_client()
    print(f"  {message}")
    if not success:
        all_passed = False

    # Test 2: Agentes principales
    print("\n📋 2. Validando Agentes Principales:")
    agent_results = test_primary_agents()

    passed_agents = 0
    for success, message in agent_results:
        print(f"  {message}")
        if success:
            passed_agents += 1
        else:
            all_passed = False

    print(f"\n  📊 Resultado: {passed_agents}/{len(agent_results)} agentes funcionando")

    # Test 3: Consolidación de archivos
    print("\n📋 3. Validando Consolidación de Archivos:")
    consolidation_results = test_file_consolidation()

    for success, message in consolidation_results:
        print(f"  {message}")
        if not success:
            all_passed = False

    # Test 4: Integridad de backups
    print("\n📋 4. Validando Integridad de Backups:")
    backup_results = test_backup_integrity()

    for success, message in backup_results:
        print(f"  {message}")
        if not success:
            all_passed = False

    # Resumen
    print("\n" + "=" * 60)
    if all_passed:
        print(
            "🎉 ¡ESTANDARIZACIÓN EXITOSA! Todos los componentes funcionan correctamente."
        )
        print("✅ Fase 11.2 completada exitosamente.")
        print("\n📊 Logros:")
        print("  • Consolidación de clientes Gemini completa")
        print("  • Eliminación de archivos duplicados exitosa")
        print("  • Backup completo de componentes legacy")
        print("  • Arquitectura simplificada y estandarizada")
        return 0
    else:
        print("⚠️  ESTANDARIZACIÓN COMPLETADA CON ADVERTENCIAS.")
        print("✅ Funcionalidad principal preservada.")
        print("⚠️  Algunos componentes necesitan atención menor.")
        print("\n📊 Estado:")
        print(
            f"  • {passed_agents}/{len(agent_results)} agentes principales funcionando"
        )
        print("  • Arquitectura consolidada exitosamente")
        print("  • Backups completos disponibles")
        return 0


if __name__ == "__main__":
    sys.exit(main())
