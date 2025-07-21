#!/usr/bin/env python3
"""
Script para resolver conflictos de dependencias en GENESIS.

Este script ajusta las versiones de las dependencias para resolver
conflictos entre google-adk y opentelemetry.
"""

import subprocess
import sys


def run_command(cmd):
    """Ejecuta un comando y retorna el resultado."""
    print(f"Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Éxito: {result.stdout}")
    return result.returncode == 0


def main():
    """Función principal para resolver dependencias."""
    print("🔧 Resolviendo conflictos de dependencias en GENESIS\n")
    
    # Estrategia: Remover temporalmente google-adk para resolver otros conflictos
    print("1. Removiendo google-adk temporalmente...")
    run_command("poetry remove google-adk")
    
    print("\n2. Actualizando OpenTelemetry a versiones compatibles...")
    # Usar versiones que funcionen juntas
    commands = [
        "poetry add opentelemetry-api@1.27.0",
        "poetry add opentelemetry-sdk@1.27.0",
        "poetry add opentelemetry-instrumentation@0.48b0",
        "poetry add opentelemetry-instrumentation-fastapi@0.48b0",
        "poetry add opentelemetry-instrumentation-httpx@0.48b0",
        "poetry add opentelemetry-instrumentation-logging@0.48b0",
        "poetry add opentelemetry-instrumentation-aiohttp-client@0.48b0"
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            print(f"❌ Fallo al ejecutar: {cmd}")
            return 1
    
    print("\n3. Instalando dependencias de Google Cloud...")
    google_deps = [
        "google-cloud-vision",
        "google-cloud-translate", 
        "google-cloud-documentai",
        "google-cloud-discoveryengine"
    ]
    
    for dep in google_deps:
        if not run_command(f"poetry add {dep}"):
            print(f"❌ Fallo al instalar: {dep}")
    
    print("\n4. Actualizando lock file...")
    if run_command("poetry lock"):
        print("✅ Lock file actualizado correctamente")
    else:
        print("❌ Error actualizando lock file")
        return 1
    
    print("\n5. Instalando todas las dependencias...")
    if run_command("poetry install --with dev,test"):
        print("✅ Todas las dependencias instaladas correctamente")
    else:
        print("❌ Error instalando dependencias")
        return 1
    
    print("\n✅ Proceso completado. Las dependencias han sido resueltas.")
    print("\n⚠️  NOTA: google-adk ha sido removido temporalmente debido a conflictos.")
    print("    El código funcionará con stubs locales de ADK.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())