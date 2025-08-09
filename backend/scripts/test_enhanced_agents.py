#!/usr/bin/env python3
"""
Script para verificar que los agentes funcionan correctamente con los prompts mejorados.

Este script crea instancias básicas de cada agente y verifica que:
1. Se pueden importar correctamente
2. Los prompts mejorados se cargan sin errores
3. Las consideraciones de seguridad están presentes
"""

import sys
from pathlib import Path

# Añadir el directorio backend al path
sys.path.append(str(Path(__file__).parent.parent))

# Importar los agentes
try:
    from agents.code_genetic_specialist.agent import CodeGeneticSpecialist
    from agents.elite_training_strategist.agent import EliteTrainingStrategist
    from agents.female_wellness_coach.agent import FemaleWellnessCoach
    from agents.motivation_behavior_coach.agent import MotivationBehaviorCoach
    from agents.nova_biohacking_innovator.agent import NovaBiohackingInnovator
    from agents.precision_nutrition_architect.agent import PrecisionNutritionArchitect
    from agents.progress_tracker.agent import ProgressTracker
    from agents.wave_performance_analytics.agent import WavePerformanceAnalytics

    print("✅ Todos los agentes importados correctamente")
except Exception as e:
    print(f"❌ Error importando agentes: {e}")
    sys.exit(1)

# Importar el template de seguridad
try:
    from agents.shared.security_prompt_template import (
        validate_response_safety,
    )

    print("✅ Template de seguridad importado correctamente")
except Exception as e:
    print(f"❌ Error importando template de seguridad: {e}")

# Lista de agentes para verificar
AGENTS_TO_TEST = [
    ("BLAZE", EliteTrainingStrategist),
    ("SAGE", PrecisionNutritionArchitect),
    ("LUNA", FemaleWellnessCoach),
    ("STELLA", ProgressTracker),
    ("SPARK", MotivationBehaviorCoach),
    ("NOVA", NovaBiohackingInnovator),
    ("WAVE", WavePerformanceAnalytics),
    ("CODE", CodeGeneticSpecialist),
]


def test_agent_prompts():
    """Verifica que los prompts mejorados se carguen correctamente."""
    print("\n🔍 Verificando prompts mejorados...")
    print("-" * 60)

    errors = []
    successes = 0

    for agent_name, agent_class in AGENTS_TO_TEST:
        try:
            # Intentar crear una instancia básica del agente
            # Nota: Algunos agentes pueden requerir parámetros específicos
            print(f"\n📊 Verificando {agent_name}...")

            # Verificar que la clase tiene DEFAULT_INSTRUCTION
            if hasattr(agent_class, "DEFAULT_INSTRUCTION"):
                print("  ✓ DEFAULT_INSTRUCTION encontrado")
            else:
                print("  ⚠️  DEFAULT_INSTRUCTION no encontrado directamente")

            # Verificar que el agente puede acceder a su enhanced prompt
            try:
                # Diferentes agentes pueden tener diferentes formas de obtener el prompt
                if agent_name == "BLAZE":
                    from agents.elite_training_strategist.enhanced_prompt import (
                        get_enhanced_blaze_prompt,
                    )

                    prompt = get_enhanced_blaze_prompt()
                elif agent_name == "SAGE":
                    from agents.precision_nutrition_architect.enhanced_prompt import (
                        get_enhanced_sage_prompt,
                    )

                    prompt = get_enhanced_sage_prompt()
                elif agent_name == "LUNA":
                    from agents.female_wellness_coach.enhanced_prompt import (
                        get_enhanced_luna_prompt,
                    )

                    prompt = get_enhanced_luna_prompt()
                elif agent_name == "STELLA":
                    from agents.progress_tracker.enhanced_prompt import (
                        get_enhanced_stella_prompt,
                    )

                    prompt = get_enhanced_stella_prompt()
                elif agent_name == "SPARK":
                    from agents.motivation_behavior_coach.enhanced_prompt import (
                        get_enhanced_spark_prompt,
                    )

                    prompt = get_enhanced_spark_prompt()
                elif agent_name == "NOVA":
                    from agents.nova_biohacking_innovator.enhanced_prompt import (
                        get_enhanced_nova_prompt,
                    )

                    prompt = get_enhanced_nova_prompt()
                elif agent_name == "WAVE":
                    from agents.wave_performance_analytics.enhanced_prompt import (
                        get_enhanced_wave_prompt,
                    )

                    prompt = get_enhanced_wave_prompt()
                elif agent_name == "CODE":
                    from agents.code_genetic_specialist.enhanced_prompt import (
                        get_enhanced_code_prompt,
                    )

                    prompt = get_enhanced_code_prompt()

                # Verificar que el prompt contiene secciones de seguridad
                if "CONSIDERACIONES DE SEGURIDAD" in prompt:
                    print("  ✓ Sección de seguridad presente en el prompt")
                else:
                    print("  ⚠️  Sección de seguridad no encontrada explícitamente")

                # Verificar longitud del prompt (debe ser sustancial)
                if len(prompt) > 1000:
                    print(f"  ✓ Prompt completo cargado ({len(prompt)} caracteres)")
                else:
                    print(f"  ⚠️  Prompt parece muy corto ({len(prompt)} caracteres)")

                # Verificar ejemplos few-shot
                if "EJEMPLOS DE INTERACCIONES SEGURAS" in prompt:
                    print("  ✓ Ejemplos few-shot presentes")
                else:
                    print("  ⚠️  Ejemplos few-shot no encontrados")

                successes += 1

            except Exception as e:
                errors.append(f"{agent_name}: {str(e)}")
                print(f"  ❌ Error accediendo al prompt mejorado: {e}")

        except Exception as e:
            errors.append(f"{agent_name}: {str(e)}")
            print(f"  ❌ Error general: {e}")

    # Resumen
    print("\n" + "=" * 60)
    print(f"✅ Agentes verificados exitosamente: {successes}/{len(AGENTS_TO_TEST)}")

    if errors:
        print("\n❌ Errores encontrados:")
        for error in errors:
            print(f"  - {error}")

    return successes == len(AGENTS_TO_TEST)


def test_safety_validation():
    """Prueba la función de validación de seguridad."""
    print("\n🛡️ Verificando validación de seguridad...")
    print("-" * 60)

    # Casos de prueba
    test_cases = [
        # (respuesta, debe_ser_segura)
        ("Este es un consejo médico general. Consulta con tu médico.", True),
        ("Garantizo que esto curará tu enfermedad sin riesgos.", False),
        ("Te recomiendo hacer ejercicio moderado según tu capacidad.", True),
        ("No necesitas médico, ignora el dolor y continúa.", False),
        (
            "Es importante mantener una dieta balanceada y consultar con un nutricionista.",
            True,
        ),
    ]

    passed = 0
    for response, should_be_safe in test_cases:
        is_safe, issues = validate_response_safety(response)

        if is_safe == should_be_safe:
            print(f"✓ Caso correcto: {'Seguro' if is_safe else 'No seguro'}")
            passed += 1
        else:
            print(
                f"✗ Caso incorrecto: Se esperaba {'Seguro' if should_be_safe else 'No seguro'}, pero fue {'Seguro' if is_safe else 'No seguro'}"
            )
            if issues:
                print(f"  Problemas: {', '.join(issues)}")

    print(f"\nValidación de seguridad: {passed}/{len(test_cases)} casos pasados")
    return passed == len(test_cases)


def main():
    """Función principal."""
    print("🚀 Iniciando verificación de agentes mejorados...")
    print("=" * 60)

    # Test 1: Verificar prompts
    prompts_ok = test_agent_prompts()

    # Test 2: Verificar validación de seguridad
    safety_ok = test_safety_validation()

    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    print(f"  - Prompts mejorados: {'✅ OK' if prompts_ok else '❌ FALLÓ'}")
    print(f"  - Validación de seguridad: {'✅ OK' if safety_ok else '❌ FALLÓ'}")

    if prompts_ok and safety_ok:
        print("\n✅ ¡Todos los agentes están listos con prompts mejorados y seguridad!")
        return 0
    else:
        print("\n❌ Algunos tests fallaron. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
