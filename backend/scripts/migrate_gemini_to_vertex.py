#!/usr/bin/env python3
"""
Script para migrar automáticamente de VertexAIClient a VertexAIClient.

Este script actualiza todos los imports y usos de VertexAIClient para usar
el cliente de Vertex AI más robusto y con mejores características.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

def find_python_files(directory: str) -> List[Path]:
    """Encuentra todos los archivos Python en el directorio."""
    return list(Path(directory).rglob("*.py"))

def migrate_imports_in_file(file_path: Path) -> Tuple[bool, Dict[str, int]]:
    """
    Migra los imports de vertex_ai_client a vertex_ai en un archivo.
    Retorna (modified, stats) donde stats contiene el conteo de cambios.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return False, {}
    
    original_content = content
    stats = {
        'import_changes': 0,
        'class_changes': 0,
        'method_changes': 0
    }
    
    # Patrones de reemplazo
    replacements = [
        # Imports básicos
        (r'from clients\.vertex_ai_client import VertexAIClient', 
         'from clients.vertex_ai.client import VertexAIClient'),
        (r'from clients\.vertex_ai_client import vertex_ai_client', 
         'from clients.vertex_ai.client import vertex_ai_client'),
        (r'import clients\.vertex_ai_client', 
         'import clients.vertex_ai.client'),
        
        # Nombres de clase
        (r'\bGeminiClient\b', 'VertexAIClient'),
        (r'\bgemini_client\b(?!\.py)', 'vertex_ai_client'),
        
        # Métodos específicos que cambian
        (r'\.generate_text\(', '.generate_content('),
        (r'\.analyze_intent\(', '.analyze_content('),
    ]
    
    for pattern, replacement in replacements:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            
            if 'import' in pattern:
                stats['import_changes'] += len(matches)
            elif 'Client' in pattern:
                stats['class_changes'] += len(matches)
            else:
                stats['method_changes'] += len(matches)
    
    # Cambios específicos en parámetros
    content = re.sub(
        r'model_name\s*=\s*["\']gemini-2\.5-pro["\']',
        'model_name="gemini-2.0-pro-001"',
        content
    )
    
    modified = content != original_content
    
    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, stats
        except Exception as e:
            print(f"❌ Error escribiendo {file_path}: {e}")
            return False, {}
    
    return False, stats

def update_requirements(backend_dir: Path) -> bool:
    """Actualiza requirements.txt para remover google-generativeai."""
    req_file = backend_dir / "requirements.txt"
    if not req_file.exists():
        return False
    
    try:
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        new_lines = [line for line in lines if 'google-generativeai' not in line]
        
        if len(new_lines) < len(lines):
            with open(req_file, 'w') as f:
                f.writelines(new_lines)
            print("✅ Removida dependencia google-generativeai de requirements.txt")
            return True
    except Exception as e:
        print(f"❌ Error actualizando requirements.txt: {e}")
    
    return False

def main():
    """Función principal."""
    backend_dir = Path(__file__).parent.parent
    
    # Excluir ciertos directorios
    exclude_dirs = {'.venv', '__pycache__', 'venv', '.git', 'node_modules'}
    
    total_files = 0
    modified_files = 0
    total_stats = {
        'import_changes': 0,
        'class_changes': 0,
        'method_changes': 0
    }
    
    print("🔄 Migrando de VertexAIClient a VertexAIClient...")
    print("-" * 60)
    
    for py_file in find_python_files(backend_dir):
        # Saltar directorios excluidos
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        
        # Saltar el archivo gemini_client.py mismo
        if py_file.name == 'gemini_client.py':
            continue
        
        total_files += 1
        modified, stats = migrate_imports_in_file(py_file)
        
        if modified:
            modified_files += 1
            for key in stats:
                total_stats[key] += stats[key]
            
            print(f"✅ Migrado: {py_file.relative_to(backend_dir)}")
            if any(stats.values()):
                print(f"   - Imports: {stats['import_changes']}, "
                      f"Clases: {stats['class_changes']}, "
                      f"Métodos: {stats['method_changes']}")
    
    # Actualizar requirements
    update_requirements(backend_dir)
    
    # Eliminar el archivo gemini_client.py
    gemini_client_file = backend_dir / "clients" / "gemini_client.py"
    if gemini_client_file.exists():
        try:
            gemini_client_file.unlink()
            print(f"\n🗑️  Eliminado archivo: {gemini_client_file.relative_to(backend_dir)}")
        except Exception as e:
            print(f"\n❌ Error eliminando gemini_client.py: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Resumen de la migración:")
    print(f"   - Archivos procesados: {total_files}")
    print(f"   - Archivos modificados: {modified_files}")
    print(f"   - Cambios de imports: {total_stats['import_changes']}")
    print(f"   - Cambios de clases: {total_stats['class_changes']}")
    print(f"   - Cambios de métodos: {total_stats['method_changes']}")
    print("\n✅ Migración completada!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())