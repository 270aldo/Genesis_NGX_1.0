#!/usr/bin/env python3
"""
Script de migración para actualizar los agentes de NGX a los nuevos modelos Gemini.

Este script actualiza las configuraciones de modelo de:
- Gemini 1.5 Pro → Gemini 2.5 Pro (agentes complejos)
- Gemini 2.0 Flash → Gemini 2.5 Flash (agentes rápidos)
- Mantiene Gemini 2.0 para agentes backend específicos
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import logging
import json
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Mapeo de modelos antiguos a nuevos
MODEL_MIGRATION_MAP = {
    "gemini-1.5-pro": "gemini-2.5-pro",
    "gemini-1.5-pro-vision": "gemini-2.5-pro",
    "gemini-2.0-pro-exp": "gemini-2.5-pro",
    "gemini-2.0-flash-exp": "gemini-2.5-flash",
    "gemini-2.0-exp": "gemini-2.0-exp",  # Mantener 2.0 para algunos casos
}

# Agentes y sus modelos asignados
AGENT_MODEL_ASSIGNMENTS = {
    # Gemini 2.5 Pro
    "orchestrator": "gemini-2.5-pro",
    "code_genetic_specialist": "gemini-2.5-pro",
    "precision_nutrition_architect": "gemini-2.5-pro",
    "elite_training_strategist": "gemini-2.5-pro",
    # Gemini 2.5 Flash
    "wave_performance_analytics": "gemini-2.5-flash",
    "motivation_behavior_coach": "gemini-2.5-flash",
    "progress_tracker": "gemini-2.5-flash",
    "female_wellness_coach": "gemini-2.5-flash",
    "nova_biohacking_innovator": "gemini-2.5-flash",
    # Gemini 2.0
    "backend/node": "gemini-2.0-exp",
    "backend/guardian": "gemini-2.0-exp",
}


def find_agent_files() -> List[Path]:
    """Encuentra todos los archivos de configuración de agentes."""
    agent_files = []
    agents_dir = Path(__file__).parent.parent / "agents"

    # Patrones de archivos a buscar
    patterns = ["config.py", "core/config.py", "agent.py", "agent_optimized.py"]

    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith("__"):
            for pattern in patterns:
                file_path = agent_dir / pattern
                if file_path.exists():
                    agent_files.append(file_path)

    return agent_files


def update_model_in_file(
    file_path: Path, dry_run: bool = False
) -> List[Tuple[str, str]]:
    """Actualiza las referencias de modelo en un archivo."""
    changes = []

    try:
        with open(file_path, "r") as f:
            content = f.read()

        original_content = content

        # Buscar y reemplazar referencias de modelo
        for old_model, new_model in MODEL_MIGRATION_MAP.items():
            if old_model in content:
                # Determinar el modelo correcto basado en el agente
                agent_name = file_path.parent.name
                if file_path.parent.parent.name == "backend":
                    agent_name = f"backend/{agent_name}"

                assigned_model = AGENT_MODEL_ASSIGNMENTS.get(agent_name, new_model)

                # Solo actualizar si es necesario
                if old_model != assigned_model:
                    content = content.replace(f'"{old_model}"', f'"{assigned_model}"')
                    content = content.replace(f"'{old_model}'", f"'{assigned_model}'")
                    content = content.replace(
                        f"model_id: {old_model}", f"model_id: {assigned_model}"
                    )
                    content = content.replace(
                        f"model_name={old_model}", f"model_name={assigned_model}"
                    )
                    changes.append((old_model, assigned_model))

        # Actualizar referencias específicas en configuraciones
        if "GEMINI_MODEL" in content:
            for agent, model in AGENT_MODEL_ASSIGNMENTS.items():
                if agent in str(file_path):
                    content = content.replace(
                        'GEMINI_MODEL = "gemini-',
                        f'GEMINI_MODEL = "{model.split("-", 1)[1]}',
                    )

        if content != original_content and not dry_run:
            with open(file_path, "w") as f:
                f.write(content)
            logger.info(f"✓ Actualizado: {file_path}")
            for old, new in changes:
                logger.info(f"  {old} → {new}")
        elif content != original_content:
            logger.info(f"[DRY RUN] Actualizaría: {file_path}")
            for old, new in changes:
                logger.info(f"  {old} → {new}")

    except Exception as e:
        logger.error(f"Error actualizando {file_path}: {e}")

    return changes


def create_migration_report(all_changes: Dict[Path, List[Tuple[str, str]]]) -> None:
    """Crea un reporte de la migración."""
    report_path = Path(__file__).parent.parent / "migration_report_gemini_models.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_files_updated": len(all_changes),
            "models_migrated": {},
        },
        "details": {},
    }

    # Contar migraciones por modelo
    model_counts = {}
    for file_path, changes in all_changes.items():
        for old_model, new_model in changes:
            key = f"{old_model} → {new_model}"
            model_counts[key] = model_counts.get(key, 0) + 1

        report["details"][str(file_path)] = [
            {"from": old, "to": new} for old, new in changes
        ]

    report["summary"]["models_migrated"] = model_counts

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"\n📊 Reporte guardado en: {report_path}")


def main(dry_run: bool = False):
    """Ejecuta la migración de modelos."""
    logger.info("🚀 Iniciando migración de modelos Gemini...")
    logger.info(f"Modo: {'DRY RUN' if dry_run else 'EJECUCIÓN REAL'}")

    # Encontrar archivos de agentes
    agent_files = find_agent_files()
    logger.info(f"📁 Encontrados {len(agent_files)} archivos de agentes")

    # Actualizar archivos
    all_changes = {}
    for file_path in agent_files:
        changes = update_model_in_file(file_path, dry_run)
        if changes:
            all_changes[file_path] = changes

    # Actualizar archivo principal de configuración
    gemini_models_path = Path(__file__).parent.parent / "config" / "gemini_models.py"
    if gemini_models_path.exists():
        logger.info("\n📋 Archivo de configuración ya actualizado")

    # Crear reporte
    if not dry_run and all_changes:
        create_migration_report(all_changes)

    # Resumen
    logger.info("\n✅ Migración completada!")
    logger.info(f"📈 Archivos actualizados: {len(all_changes)}")

    # Mostrar distribución final
    logger.info("\n📊 Distribución final de modelos:")
    logger.info("  Gemini 2.5 Pro: NEXUS, CODE, SAGE, BLAZE")
    logger.info("  Gemini 2.5 Flash: WAVE, SPARK, STELLA, LUNA, NOVA")
    logger.info("  Gemini 2.0: NODE, GUARDIAN")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrar agentes a nuevos modelos Gemini"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar en modo simulación sin hacer cambios",
    )

    args = parser.parse_args()
    main(dry_run=args.dry_run)
