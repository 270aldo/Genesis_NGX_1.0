#!/usr/bin/env python3
"""
Script para mejorar todos los prompts de agentes con consideraciones de seguridad.

Este script agrega secciones de seguridad, ejemplos few-shot y formato de salida
a todos los prompts de los agentes del sistema.
"""

import os
from pathlib import Path
from typing import Dict, List

# Importar el template de seguridad
import sys
sys.path.append(str(Path(__file__).parent.parent))
from agents.shared.security_prompt_template import get_security_enhanced_prompt

# Definir configuración para cada agente
AGENT_CONFIGS = {
    "elite_training_strategist": {
        "domain": "training",
        "agent_name": "BLAZE",
        "few_shot_focus": "planes de entrenamiento seguros"
    },
    "precision_nutrition_architect": {
        "domain": "nutrition", 
        "agent_name": "SAGE",
        "few_shot_focus": "recomendaciones nutricionales responsables"
    },
    "female_wellness_coach": {
        "domain": "wellness",
        "agent_name": "LUNA",
        "few_shot_focus": "salud femenina con sensibilidad"
    },
    "progress_tracker": {
        "domain": "performance",
        "agent_name": "STELLA",
        "few_shot_focus": "monitoreo de progreso objetivo"
    },
    "motivation_behavior_coach": {
        "domain": "wellness",
        "agent_name": "SPARK",
        "few_shot_focus": "apoyo psicológico apropiado"
    },
    "nova_biohacking_innovator": {
        "domain": "performance",
        "agent_name": "NOVA",
        "few_shot_focus": "biohacking basado en evidencia"
    },
    "wave_performance_analytics": {
        "domain": "performance",
        "agent_name": "WAVE",
        "few_shot_focus": "análisis de datos precisos"
    },
    "code_genetic_specialist": {
        "domain": "wellness",
        "agent_name": "CODE",
        "few_shot_focus": "interpretación genética responsable"
    }
}

def create_enhanced_prompt_file(agent_dir: str, config: Dict[str, str]) -> bool:
    """
    Crea un archivo enhanced_prompt.py para un agente específico.
    
    Args:
        agent_dir: Directorio del agente
        config: Configuración del agente
        
    Returns:
        bool: True si se creó exitosamente
    """
    agent_name = config["agent_name"]
    domain = config["domain"]
    few_shot_focus = config["few_shot_focus"]
    
    template = f'''"""
Prompt mejorado con seguridad para {agent_name}.
Generado automáticamente por enhance_agent_prompts.py
"""

from agents.shared.security_prompt_template import get_security_enhanced_prompt

# Definir el prompt base del agente
BASE_INSTRUCTION = """
[AQUÍ VA EL PROMPT ORIGINAL DEL AGENTE {agent_name}]
"""

# Ejemplos few-shot específicos para {agent_name}
FEW_SHOT_EXAMPLES = """
EJEMPLOS DE INTERACCIONES SEGURAS - {agent_name}:

[Ejemplo 1: Manejo de situación normal]
Usuario: [Pregunta típica del dominio]
{agent_name}: [Respuesta que demuestra {few_shot_focus}]

[Ejemplo 2: Manejo de situación de riesgo]
Usuario: [Pregunta que requiere precaución]
{agent_name}: [Respuesta que prioriza seguridad y deriva a profesionales]

[Ejemplo 3: Manejo de expectativas irreales]
Usuario: [Solicitud poco realista o peligrosa]
{agent_name}: [Respuesta educativa que reencuadra expectativas]
"""

# Formato de salida esperado
OUTPUT_FORMAT = """
FORMATO DE RESPUESTAS - {agent_name}:

1. ESTRUCTURA CLARA:
   - Usa Markdown para organización
   - Separa secciones lógicamente
   - Destaca información crítica de seguridad

2. TONO Y ESTILO:
   - Profesional pero accesible
   - Empático y comprensivo
   - Claro sobre limitaciones

3. CONTENIDO ESENCIAL:
   - Siempre incluir consideraciones de seguridad relevantes
   - Proporcionar alternativas cuando sea necesario
   - Indicar cuándo se requiere supervisión profesional
"""

# Generar el prompt completo con seguridad
ENHANCED_{agent_name.upper()}_INSTRUCTION = get_security_enhanced_prompt(
    f"{{BASE_INSTRUCTION}}\\n\\n{{FEW_SHOT_EXAMPLES}}\\n\\n{{OUTPUT_FORMAT}}",
    agent_domain="{domain}"
)

def get_enhanced_{agent_name.lower()}_prompt() -> str:
    """
    Retorna el prompt mejorado de {agent_name} con todas las consideraciones de seguridad.
    
    Returns:
        str: Prompt completo con seguridad integrada
    """
    return ENHANCED_{agent_name.upper()}_INSTRUCTION
'''
    
    output_path = Path(agent_dir) / "enhanced_prompt.py"
    
    try:
        # Solo crear si no existe para no sobrescribir trabajo manual
        if not output_path.exists():
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"✅ Creado enhanced_prompt.py para {agent_name}")
            return True
        else:
            print(f"⏭️  enhanced_prompt.py ya existe para {agent_name}")
            return False
    except Exception as e:
        print(f"❌ Error creando prompt para {agent_name}: {e}")
        return False

def update_agent_to_use_enhanced_prompt(agent_dir: str, agent_name: str) -> bool:
    """
    Actualiza el agent.py para importar y usar el prompt mejorado.
    
    Args:
        agent_dir: Directorio del agente
        agent_name: Nombre del agente
        
    Returns:
        bool: True si se actualizó exitosamente
    """
    agent_file = Path(agent_dir) / "agent.py"
    
    if not agent_file.exists():
        print(f"⚠️  No se encontró agent.py en {agent_dir}")
        return False
    
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya está usando enhanced_prompt
        if "enhanced_prompt" in content:
            print(f"⏭️  {agent_name} ya usa enhanced_prompt")
            return False
        
        # Agregar import al inicio del archivo
        import_line = f"from agents.{Path(agent_dir).name}.enhanced_prompt import get_enhanced_{agent_name.lower()}_prompt\n"
        
        # Buscar donde insertar el import (después de otros imports de agents)
        import_pos = content.find("from agents.")
        if import_pos == -1:
            import_pos = content.find("import ")
        
        if import_pos != -1:
            # Encontrar el final de la línea
            line_end = content.find("\n", import_pos)
            content = content[:line_end+1] + import_line + content[line_end+1:]
        
        # TODO: Actualizar DEFAULT_INSTRUCTION para usar get_enhanced_prompt()
        # Esto requiere análisis más cuidadoso de cada archivo
        
        print(f"ℹ️  Import agregado a {agent_name} - Requiere actualización manual de DEFAULT_INSTRUCTION")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando {agent_name}: {e}")
        return False

def main():
    """Función principal."""
    backend_dir = Path(__file__).parent.parent
    agents_dir = backend_dir / "agents"
    
    created_count = 0
    
    print("🚀 Mejorando prompts de agentes con seguridad...")
    print("-" * 60)
    
    for agent_folder, config in AGENT_CONFIGS.items():
        agent_path = agents_dir / agent_folder
        
        if agent_path.exists():
            if create_enhanced_prompt_file(str(agent_path), config):
                created_count += 1
        else:
            print(f"⚠️  No se encontró directorio para {agent_folder}")
    
    print("\n" + "=" * 60)
    print(f"✅ Creados {created_count} archivos enhanced_prompt.py")
    print("\n📝 Próximos pasos:")
    print("1. Revisar y personalizar los prompts generados")
    print("2. Agregar ejemplos few-shot específicos")
    print("3. Actualizar agent.py para usar los prompts mejorados")
    print("4. Probar exhaustivamente las respuestas de seguridad")

if __name__ == "__main__":
    main()