#!/usr/bin/env python3
"""
Sincroniza requirements.txt desde pyproject.toml

Este script exporta las dependencias de Poetry a requirements.txt
para mantener compatibilidad con entornos que no usan Poetry.
"""

import subprocess
import sys
import os
from pathlib import Path


def sync_requirements():
    """
    Exporta las dependencias de Poetry a requirements.txt
    """
    # Verificar que estamos en el directorio correcto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Verificar que Poetry está instalado
    try:
        subprocess.run(
            ["poetry", "--version"], check=True, capture_output=True, text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Poetry no está instalado.")
        print("   Instálalo con: pip install poetry")
        sys.exit(1)

    # Verificar que pyproject.toml existe
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml no encontrado")
        sys.exit(1)

    print("🔄 Sincronizando requirements.txt desde pyproject.toml...")

    try:
        # Primero, intentar instalar el plugin de export si no está disponible
        try:
            subprocess.run(
                ["poetry", "self", "add", "poetry-plugin-export"],
                capture_output=True,
                text=True,
                check=False,  # No fallar si ya está instalado
            )
        except Exception:
            pass  # Ignorar errores si el plugin ya está instalado

        # Exportar todas las dependencias (incluyendo dev)
        # Poetry export incluye las versiones exactas para reproducibilidad
        result = subprocess.run(
            [
                "poetry",
                "export",
                "--format",
                "requirements.txt",
                "--output",
                "requirements.txt",
                "--without-hashes",  # Omitir hashes para mejor compatibilidad
                "--with",
                "dev",  # Incluir dependencias de desarrollo
                "--with",
                "test",  # Incluir dependencias de testing
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Agregar encabezado al archivo
        with open("requirements.txt", "r") as f:
            content = f.read()

        header = """# AUTOGENERADO - NO EDITAR MANUALMENTE
# Este archivo se genera automáticamente desde pyproject.toml
# Para actualizar dependencias, edita pyproject.toml y ejecuta:
#   python scripts/sync_requirements.py
# 
# Para desarrollo, se recomienda usar Poetry:
#   pip install poetry
#   poetry install
#
# Generado con: poetry export

"""

        with open("requirements.txt", "w") as f:
            f.write(header + content)

        print("✅ requirements.txt sincronizado exitosamente")

        # Mostrar resumen
        lines = content.strip().split("\n")
        packages = [line for line in lines if line and not line.startswith("#")]
        print(f"📦 Total de paquetes exportados: {len(packages)}")

        # Crear también un requirements-prod.txt sin dependencias de dev
        print("\n🔄 Creando requirements-prod.txt (solo producción)...")

        result = subprocess.run(
            [
                "poetry",
                "export",
                "--format",
                "requirements.txt",
                "--output",
                "requirements-prod.txt",
                "--without-hashes",
                "--without",
                "dev",  # Excluir dependencias de desarrollo
                "--without",
                "test",  # Excluir dependencias de testing
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Agregar encabezado
        with open("requirements-prod.txt", "r") as f:
            content_prod = f.read()

        header_prod = """# AUTOGENERADO - NO EDITAR MANUALMENTE
# Este archivo contiene SOLO las dependencias de producción
# Para desarrollo completo, usa requirements.txt
#
# Generado con: poetry export (sin dev/test)

"""

        with open("requirements-prod.txt", "w") as f:
            f.write(header_prod + content_prod)

        lines_prod = content_prod.strip().split("\n")
        packages_prod = [
            line for line in lines_prod if line and not line.startswith("#")
        ]
        print(f"✅ requirements-prod.txt creado ({len(packages_prod)} paquetes)")

        print(f"\n📊 Resumen:")
        print(f"   - Dependencias totales: {len(packages)}")
        print(f"   - Solo producción: {len(packages_prod)}")
        print(f"   - Dev/Test: {len(packages) - len(packages_prod)}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error al exportar dependencias: {e}")
        if e.stderr:
            print(f"   Detalles: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


def add_to_git_hooks():
    """
    Agrega el script a los git hooks para sincronización automática
    """
    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        print("⚠️  Directorio .git/hooks no encontrado. ¿Estás en un repositorio git?")
        return

    pre_commit_hook = hooks_dir / "pre-commit"

    hook_content = """#!/bin/bash
# Sincronizar requirements.txt si pyproject.toml ha cambiado

if git diff --cached --name-only | grep -q "pyproject.toml"; then
    echo "📦 pyproject.toml modificado, sincronizando requirements.txt..."
    python scripts/sync_requirements.py
    git add requirements.txt requirements-prod.txt
fi
"""

    if pre_commit_hook.exists():
        print(
            "⚠️  Hook pre-commit ya existe. Agrega manualmente la sincronización si es necesario."
        )
    else:
        with open(pre_commit_hook, "w") as f:
            f.write(hook_content)
        pre_commit_hook.chmod(0o755)
        print("✅ Hook pre-commit creado para sincronización automática")


if __name__ == "__main__":
    import sys

    sync_requirements()

    # Solo preguntar si es terminal interactivo
    if sys.stdin.isatty():
        try:
            response = input(
                "\n¿Deseas agregar sincronización automática en git commits? (s/n): "
            )
            if response.lower() == "s":
                add_to_git_hooks()
        except (EOFError, KeyboardInterrupt):
            print("\nOmitiendo configuración de git hooks.")
    else:
        print(
            "\nPara agregar git hooks, ejecuta: python scripts/sync_requirements.py --add-hooks"
        )

    # Agregar opción de línea de comandos
    if "--add-hooks" in sys.argv:
        add_to_git_hooks()
