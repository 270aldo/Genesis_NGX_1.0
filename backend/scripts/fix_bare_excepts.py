#!/usr/bin/env python3
"""
Script para corregir bare excepts en el código.
Reemplaza 'except:' con 'except Exception:' de manera segura.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

def find_python_files(directory: str) -> List[Path]:
    """Encuentra todos los archivos Python en el directorio."""
    return list(Path(directory).rglob("*.py"))

def fix_bare_except_in_file(file_path: Path) -> int:
    """
    Corrige bare excepts en un archivo.
    Retorna el número de cambios realizados.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return 0
    
    # Buscar líneas con bare except
    lines = content.split('\n')
    modified = False
    changes = 0
    
    for i, line in enumerate(lines):
        # Detectar bare except (considerando espacios)
        if re.match(r'^\s*except\s*:\s*$', line):
            # Obtener la indentación
            indent = len(line) - len(line.lstrip())
            # Reemplazar con except Exception:
            lines[i] = ' ' * indent + 'except Exception:'
            modified = True
            changes += 1
    
    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"✅ Corregido {file_path}: {changes} bare except(s)")
        except Exception as e:
            print(f"❌ Error escribiendo {file_path}: {e}")
            return 0
    
    return changes

def main():
    """Función principal."""
    # Directorio base del backend
    backend_dir = Path(__file__).parent.parent
    
    # Excluir ciertos directorios
    exclude_dirs = {'.venv', '__pycache__', 'venv', '.git', 'node_modules'}
    
    total_files = 0
    total_changes = 0
    
    print("🔍 Buscando y corrigiendo bare excepts...")
    
    for py_file in find_python_files(backend_dir):
        # Saltar directorios excluidos
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        
        total_files += 1
        changes = fix_bare_except_in_file(py_file)
        total_changes += changes
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos procesados: {total_files}")
    print(f"   - Bare excepts corregidos: {total_changes}")
    
    return 0 if total_changes > 0 else 1

if __name__ == "__main__":
    sys.exit(main())