#!/bin/bash

# Script consolidado de limpieza para GENESIS
# Combina todas las funciones de limpieza en un solo script

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}=== GENESIS Cleanup Script ===${NC}"
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -a, --all          Ejecutar todas las limpiezas"
    echo "  -c, --cache        Limpiar archivos de caché"
    echo "  -t, --tests        Limpiar archivos de pruebas temporales"
    echo "  -p, --pycache      Limpiar __pycache__ y .pyc"
    echo "  -l, --logs         Limpiar archivos de log"
    echo "  -b, --backups      Limpiar archivos de respaldo (.bak, .backup)"
    echo "  -d, --dry-run      Mostrar qué se eliminaría sin hacerlo"
    echo "  -h, --help         Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --all           # Limpieza completa"
    echo "  $0 --cache --logs  # Solo caché y logs"
    echo "  $0 --dry-run --all # Ver qué se eliminaría"
}

# Variables globales
DRY_RUN=false
TASKS=()

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            TASKS=("cache" "tests" "pycache" "logs" "backups")
            shift
            ;;
        -c|--cache)
            TASKS+=("cache")
            shift
            ;;
        -t|--tests)
            TASKS+=("tests")
            shift
            ;;
        -p|--pycache)
            TASKS+=("pycache")
            shift
            ;;
        -l|--logs)
            TASKS+=("logs")
            shift
            ;;
        -b|--backups)
            TASKS+=("backups")
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Si no se especificaron tareas, mostrar ayuda
if [ ${#TASKS[@]} -eq 0 ]; then
    show_help
    exit 0
fi

# Función para ejecutar comandos
execute_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} $1"
    else
        eval "$1"
    fi
}

# Función para limpiar caché
clean_cache() {
    echo -e "${GREEN}Limpiando archivos de caché...${NC}"
    execute_cmd "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true"
    execute_cmd "find . -type f -name '*.pyc' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name '*.pyo' -delete 2>/dev/null || true"
    execute_cmd "find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true"
    execute_cmd "find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true"
    execute_cmd "find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true"
}

# Función para limpiar archivos de pruebas
clean_tests() {
    echo -e "${GREEN}Limpiando archivos temporales de pruebas...${NC}"
    execute_cmd "find . -type f -name '.coverage' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name 'coverage.xml' -delete 2>/dev/null || true"
    execute_cmd "find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true"
    execute_cmd "find . -type f -name '*.test.log' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name 'test_*.json' -delete 2>/dev/null || true"
}

# Función para limpiar pycache
clean_pycache() {
    echo -e "${GREEN}Limpiando __pycache__ y archivos compilados...${NC}"
    execute_cmd "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true"
    execute_cmd "find . -type f -name '*.pyc' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name '*.pyo' -delete 2>/dev/null || true"
}

# Función para limpiar logs
clean_logs() {
    echo -e "${GREEN}Limpiando archivos de log...${NC}"
    execute_cmd "find . -type f -name '*.log' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name '*.log.*' -delete 2>/dev/null || true"
    execute_cmd "rm -rf logs/* 2>/dev/null || true"
}

# Función para limpiar backups
clean_backups() {
    echo -e "${GREEN}Limpiando archivos de respaldo...${NC}"
    execute_cmd "find . -type f -name '*.bak' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name '*.backup' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name '*_old.*' -delete 2>/dev/null || true"
    execute_cmd "find . -type f -name '*_original.*' -delete 2>/dev/null || true"
}

# Función principal
main() {
    echo -e "${BLUE}=== Iniciando limpieza de GENESIS ===${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}Modo DRY RUN activado - no se eliminarán archivos${NC}"
    fi
    
    # Ejecutar tareas seleccionadas
    for task in "${TASKS[@]}"; do
        case $task in
            cache)
                clean_cache
                ;;
            tests)
                clean_tests
                ;;
            pycache)
                clean_pycache
                ;;
            logs)
                clean_logs
                ;;
            backups)
                clean_backups
                ;;
        esac
    done
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
    
    # Mostrar estadísticas si no es dry run
    if [ "$DRY_RUN" = false ]; then
        echo -e "${BLUE}Espacio liberado:${NC}"
        du -sh . 2>/dev/null | awk '{print "Tamaño actual del proyecto: " $1}'
    fi
}

# Ejecutar función principal
main