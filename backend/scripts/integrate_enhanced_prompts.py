#!/usr/bin/env python3
"""
Script para integrar los prompts mejorados en los archivos agent.py.

Este script actualiza los archivos agent.py para usar los prompts mejorados
con consideraciones de seguridad en lugar de los prompts originales.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapeo de agentes a sus nombres de variable
AGENT_MAPPINGS = {
    "elite_training_strategist": "blaze",
    "precision_nutrition_architect": "sage",
    "female_wellness_coach": "luna",
    "progress_tracker": "stella",
    "motivation_behavior_coach": "spark",
    "nova_biohacking_innovator": "nova",
    "wave_performance_analytics": "wave",
    "code_genetic_specialist": "code"
}

def add_import_to_agent(agent_file: Path, agent_folder: str, agent_var: str) -> bool:
    """
    Añade el import del enhanced_prompt al archivo agent.py.
    
    Args:
        agent_file: Path al archivo agent.py
        agent_folder: Nombre de la carpeta del agente
        agent_var: Nombre de variable del agente (ej: blaze, sage)
        
    Returns:
        bool: True si se modificó el archivo
    """
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya tiene el import
        if "enhanced_prompt" in content:
            print(f"⏭️  {agent_var.upper()} ya importa enhanced_prompt")
            return False
        
        # Buscar donde insertar el import (después de otros imports de agents)
        import_line = f"from agents.{agent_folder}.enhanced_prompt import get_enhanced_{agent_var}_prompt\n"
        
        # Buscar el mejor lugar para insertar
        # Opción 1: Después de otros imports from agents
        pattern = r'(from agents\.[^\n]+\n)'
        matches = list(re.finditer(pattern, content))
        
        if matches:
            # Insertar después del último import de agents
            last_match = matches[-1]
            insert_pos = last_match.end()
            content = content[:insert_pos] + import_line + content[insert_pos:]
        else:
            # Opción 2: Después de los imports generales
            pattern = r'(import [^\n]+\n)'
            matches = list(re.finditer(pattern, content))
            if matches:
                last_match = matches[-1]
                insert_pos = last_match.end()
                content = content[:insert_pos] + "\n" + import_line + content[insert_pos:]
        
        # Guardar el archivo actualizado
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Import añadido a {agent_var.upper()}")
        return True
        
    except Exception as e:
        print(f"❌ Error procesando {agent_var.upper()}: {e}")
        return False

def update_instruction_usage(agent_file: Path, agent_var: str) -> bool:
    """
    Actualiza el uso de DEFAULT_INSTRUCTION para usar la versión mejorada.
    
    Args:
        agent_file: Path al archivo agent.py
        agent_var: Nombre de variable del agente
        
    Returns:
        bool: True si se modificó el archivo
    """
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el patrón de DEFAULT_INSTRUCTION
        # Patrón 1: En el __init__ method
        pattern1 = r'(_instruction = instruction or self\.DEFAULT_INSTRUCTION)'
        replacement1 = f'_instruction = instruction or get_enhanced_{agent_var}_prompt()'
        
        modified = False
        if re.search(pattern1, content):
            content = re.sub(pattern1, replacement1, content)
            modified = True
            print(f"✅ Actualizado uso de instrucción en __init__ para {agent_var.upper()}")
        
        # Patrón 2: Asignación directa de DEFAULT_INSTRUCTION
        pattern2 = r'(instruction\s*=\s*self\.DEFAULT_INSTRUCTION)'
        replacement2 = f'instruction = get_enhanced_{agent_var}_prompt()'
        
        if re.search(pattern2, content):
            content = re.sub(pattern2, replacement2, content)
            modified = True
            print(f"✅ Actualizado uso directo de DEFAULT_INSTRUCTION para {agent_var.upper()}")
        
        if modified:
            # Guardar archivo
            with open(agent_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            print(f"ℹ️  No se encontraron usos de DEFAULT_INSTRUCTION para actualizar en {agent_var.upper()}")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando instrucciones para {agent_var.upper()}: {e}")
        return False

def main():
    """Función principal."""
    backend_dir = Path(__file__).parent.parent
    agents_dir = backend_dir / "agents"
    
    imports_added = 0
    instructions_updated = 0
    
    print("🚀 Integrando prompts mejorados en archivos agent.py...")
    print("-" * 60)
    
    for agent_folder, agent_var in AGENT_MAPPINGS.items():
        agent_path = agents_dir / agent_folder
        agent_file = agent_path / "agent.py"
        enhanced_file = agent_path / "enhanced_prompt.py"
        
        if not agent_file.exists():
            print(f"⚠️  No se encontró agent.py para {agent_folder}")
            continue
            
        if not enhanced_file.exists():
            print(f"⚠️  No se encontró enhanced_prompt.py para {agent_folder}")
            continue
        
        print(f"\n📝 Procesando {agent_var.upper()}...")
        
        # Añadir import
        if add_import_to_agent(agent_file, agent_folder, agent_var):
            imports_added += 1
        
        # Actualizar uso de instrucciones
        if update_instruction_usage(agent_file, agent_var):
            instructions_updated += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Imports añadidos: {imports_added}")
    print(f"✅ Instrucciones actualizadas: {instructions_updated}")
    print("\n📝 Próximos pasos:")
    print("1. Revisar los cambios en cada agent.py")
    print("2. Completar los prompts base en enhanced_prompt.py")
    print("3. Añadir ejemplos few-shot específicos")
    print("4. Ejecutar tests para verificar funcionamiento")
    print("5. Probar respuestas de seguridad de cada agente")

if __name__ == "__main__":
    main()