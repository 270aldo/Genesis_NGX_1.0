#!/usr/bin/env python3
"""
Script para ejecutar tests de agentes con diferentes configuraciones.

Uso:
    python run_agent_tests.py                    # Ejecutar todos los tests
    python run_agent_tests.py --agent sage      # Tests de un agente específico
    python run_agent_tests.py --coverage        # Con reporte de cobertura
    python run_agent_tests.py --fast           # Solo tests rápidos (sin integration)
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd: list, description: str = "") -> int:
    """Ejecuta un comando y retorna el código de salida"""
    if description:
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
    
    print(f"Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Ejecutar tests de agentes NGX")
    parser.add_argument(
        "--agent",
        help="Ejecutar tests de un agente específico",
        choices=[
            "all", "orchestrator", "sage", "blaze", "luna", 
            "stella", "spark", "nova", "wave", "code"
        ],
        default="all"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generar reporte de cobertura"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Ejecutar solo tests unitarios (excluir integration y slow)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Salida verbosa"
    )
    parser.add_argument(
        "--failfast",
        "-x",
        action="store_true",
        help="Detener en el primer fallo"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generar reporte HTML de cobertura"
    )
    
    args = parser.parse_args()
    
    # Cambiar al directorio backend
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Construir comando base
    cmd = ["pytest"]
    
    # Agregar opciones
    if args.verbose:
        cmd.append("-v")
    
    if args.failfast:
        cmd.append("-x")
    
    # Configurar marcadores
    markers = []
    if args.fast:
        markers.extend(["-m", "not integration and not slow"])
    else:
        markers.extend(["-m", "agents"])
    
    # Configurar cobertura
    if args.coverage:
        cmd.extend([
            "--cov=agents",
            "--cov=core",
            "--cov=app",
            "--cov-report=term-missing:skip-covered",
            f"--cov-fail-under=70"  # Meta inicial: 70%, objetivo: 85%
        ])
        
        if args.html:
            cmd.append("--cov-report=html")
    
    # Determinar qué tests ejecutar
    if args.agent == "all":
        # Ejecutar todos los tests de agentes
        test_paths = [
            "tests/agents/test_all_agents.py",
            "tests/agents/test_base_agent.py"
        ]
    else:
        # Mapear nombres cortos a paths
        agent_paths = {
            "orchestrator": "tests/agents/orchestrator/",
            "sage": "tests/agents/precision_nutrition_architect/",
            "blaze": "tests/agents/elite_training_strategist/",
            "luna": "tests/agents/female_wellness_coach/",
            "stella": "tests/agents/progress_tracker/",
            "spark": "tests/agents/motivation_behavior_coach/",
            "nova": "tests/agents/nova_biohacking_innovator/",
            "wave": "tests/agents/wave_performance_analytics/",
            "code": "tests/agents/code_genetic_specialist/"
        }
        
        test_path = agent_paths.get(args.agent)
        if test_path and Path(test_path).exists():
            test_paths = [test_path]
        else:
            # Si no existe el directorio, buscar en test_all_agents.py
            test_paths = ["tests/agents/test_all_agents.py"]
            markers.extend(["-k", f"Test{args.agent.title()}"])
    
    # Agregar marcadores si existen
    if markers:
        cmd.extend(markers)
    
    # Agregar paths de tests
    cmd.extend(test_paths)
    
    # Ejecutar tests principales
    print("\n" + "🚀 EJECUTANDO TESTS DE AGENTES NGX".center(60, "="))
    print(f"\nAgente(s): {args.agent}")
    print(f"Cobertura: {'Sí' if args.coverage else 'No'}")
    print(f"Modo: {'Rápido (solo unit)' if args.fast else 'Completo'}")
    
    exit_code = run_command(cmd, "Tests de Agentes")
    
    # Si se solicitó cobertura HTML, mostrar mensaje
    if args.coverage and args.html and exit_code == 0:
        print("\n✅ Reporte de cobertura HTML generado en: htmlcov/index.html")
        print("   Para verlo, ejecuta: python -m http.server -d htmlcov 8080")
    
    # Ejecutar tests adicionales si todo salió bien y no es modo fast
    if exit_code == 0 and not args.fast and args.agent == "all":
        # Tests de integración A2A
        print("\n" + "🔄 TESTS DE INTEGRACIÓN A2A".center(60, "="))
        a2a_cmd = ["pytest", "-v", "-m", "a2a", "tests/adapters/"]
        exit_code = run_command(a2a_cmd, "Tests A2A")
    
    # Resumen final
    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        
        if args.coverage:
            print("\n📊 Para ver detalles de cobertura:")
            print("   - Terminal: La cobertura se mostró arriba")
            if args.html:
                print("   - HTML: htmlcov/index.html")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("\nPara más detalles, ejecuta con --verbose")
    
    print("="*60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())