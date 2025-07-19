#!/usr/bin/env python3
"""
Script simplificado para verificar que los prompts mejorados se pueden importar correctamente.
"""

import sys
from pathlib import Path

# Añadir el directorio backend al path
sys.path.append(str(Path(__file__).parent.parent))

print("🚀 Verificando prompts mejorados...")
print("=" * 60)

# Lista de prompts para verificar
PROMPTS_TO_CHECK = [
    ("BLAZE", "agents.elite_training_strategist.enhanced_prompt", "get_enhanced_blaze_prompt"),
    ("SAGE", "agents.precision_nutrition_architect.enhanced_prompt", "get_enhanced_sage_prompt"),
    ("LUNA", "agents.female_wellness_coach.enhanced_prompt", "get_enhanced_luna_prompt"),
    ("STELLA", "agents.progress_tracker.enhanced_prompt", "get_enhanced_stella_prompt"),
    ("SPARK", "agents.motivation_behavior_coach.enhanced_prompt", "get_enhanced_spark_prompt"),
    ("NOVA", "agents.nova_biohacking_innovator.enhanced_prompt", "get_enhanced_nova_prompt"),
    ("WAVE", "agents.wave_performance_analytics.enhanced_prompt", "get_enhanced_wave_prompt"),
    ("CODE", "agents.code_genetic_specialist.enhanced_prompt", "get_enhanced_code_prompt"),
]

success_count = 0
errors = []

for agent_name, module_path, function_name in PROMPTS_TO_CHECK:
    print(f"\n📊 Verificando {agent_name}...")
    
    try:
        # Importar dinámicamente
        module = __import__(module_path, fromlist=[function_name])
        get_prompt_func = getattr(module, function_name)
        
        # Obtener el prompt
        prompt = get_prompt_func()
        
        # Verificaciones básicas
        checks = {
            "Longitud > 1000 caracteres": len(prompt) > 1000,
            "Contiene 'CONSIDERACIONES DE SEGURIDAD'": "CONSIDERACIONES DE SEGURIDAD" in prompt,
            "Contiene 'EJEMPLOS DE INTERACCIONES'": "EJEMPLOS DE INTERACCIONES" in prompt,
            "Contiene nombre del agente": agent_name in prompt.upper()
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                all_passed = False
        
        if all_passed:
            success_count += 1
            print(f"  ✨ {agent_name} - Prompt mejorado verificado correctamente!")
        else:
            errors.append(f"{agent_name}: Algunas verificaciones fallaron")
            
    except Exception as e:
        print(f"  ❌ Error importando: {e}")
        errors.append(f"{agent_name}: {str(e)}")

# Resumen final
print("\n" + "=" * 60)
print(f"📊 RESULTADO: {success_count}/{len(PROMPTS_TO_CHECK)} prompts verificados exitosamente")

if errors:
    print("\n❌ Errores encontrados:")
    for error in errors:
        print(f"  - {error}")
else:
    print("\n✅ ¡Todos los prompts mejorados están funcionando correctamente!")

# Verificar el template de seguridad
print("\n🛡️ Verificando template de seguridad...")
try:
    from agents.shared.security_prompt_template import SECURITY_SECTION, validate_response_safety
    print("  ✅ Template de seguridad importado correctamente")
    print(f"  ✅ Sección de seguridad tiene {len(SECURITY_SECTION)} caracteres")
    
    # Test rápido de validación
    safe_response = "Consulta con tu médico para obtener asesoría profesional."
    unsafe_response = "Garantizo que esto curará tu enfermedad sin riesgos."
    
    is_safe1, _ = validate_response_safety(safe_response)
    is_safe2, _ = validate_response_safety(unsafe_response)
    
    if is_safe1 and not is_safe2:
        print("  ✅ Función de validación funcionando correctamente")
    else:
        print("  ⚠️  Función de validación puede necesitar ajustes")
        
except Exception as e:
    print(f"  ❌ Error con template de seguridad: {e}")