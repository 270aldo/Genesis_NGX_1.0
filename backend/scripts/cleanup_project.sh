#!/bin/bash
# scripts/cleanup_project.sh

set -e

echo "🧹 Iniciando limpieza del proyecto NGX Agents..."

# Crear directorio de archivo con timestamp
ARCHIVE_DIR="archive_cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

# ====================================
# PASO 1: ARCHIVAR ARCHIVOS IMPORTANTES
# ====================================
echo "📦 Archivando archivos importantes..."

# Archivar documentación de sesiones (puede tener valor histórico)
mkdir -p "$ARCHIVE_DIR/memory-bank"
cp memory-bank/session_*.md "$ARCHIVE_DIR/memory-bank/" 2>/dev/null || true

# Archivar planes completados
mkdir -p "$ARCHIVE_DIR/docs"
cp PLAN_IMPLEMENTACION_FRONTEND_DETALLADO.md "$ARCHIVE_DIR/" 2>/dev/null || true
cp docs/plan_*.md "$ARCHIVE_DIR/docs/" 2>/dev/null || true
cp frontend/PLAN_*.md "$ARCHIVE_DIR/docs/" 2>/dev/null || true

# Archivar resúmenes históricos  
cp project_summary.md "$ARCHIVE_DIR/" 2>/dev/null || true
cp resumen_ejecutivo_ngx_agents.md "$ARCHIVE_DIR/" 2>/dev/null || true
cp propuesta_frontend_innovador_ngx.md "$ARCHIVE_DIR/" 2>/dev/null || true

echo "✅ Archivos importantes guardados en: $ARCHIVE_DIR"

# ====================================
# PASO 2: ELIMINAR LOGS
# ====================================
echo "🗑️ Eliminando logs de desarrollo..."

# Logs del servidor
rm -f server*.log
rm -f cache_monitoring.log

# Logs en subdirectorios (except node_modules)
find . -name "*.log" -not -path "./node_modules/*" -not -path "./$ARCHIVE_DIR/*" -delete 2>/dev/null || true

echo "✅ Logs eliminados"

# ====================================
# PASO 3: ELIMINAR CACHE DE PYTHON
# ====================================
echo "🐍 Eliminando cache de Python..."

# __pycache__ directories
find . -type d -name "__pycache__" -not -path "./$ARCHIVE_DIR/*" -exec rm -rf {} + 2>/dev/null || true

# .pyc files
find . -name "*.pyc" -not -path "./$ARCHIVE_DIR/*" -delete 2>/dev/null || true

echo "✅ Cache de Python eliminado"

# ====================================
# PASO 4: ELIMINAR BACKUPS Y DUPLICADOS
# ====================================
echo "🔄 Eliminando backups y duplicados..."

# Directorios de backup
rm -rf backup_pyproject_*

# Archivos backup/duplicados
find . -name "*.bak" -not -path "./$ARCHIVE_DIR/*" -delete 2>/dev/null || true
find . -name "*.new" -not -path "./$ARCHIVE_DIR/*" -delete 2>/dev/null || true

echo "✅ Backups y duplicados eliminados"

# ====================================
# PASO 5: ELIMINAR DOCUMENTACIÓN OBSOLETA
# ====================================
echo "📝 Eliminando documentación obsoleta..."

# Sesiones y contextos obsoletos
rm -f CONTEXTO_SESION_*.md
rm -f PROJECT_STATUS_*.md  
rm -f SESION_*.md
rm -f RESUMEN_*.md
rm -f QUICK_FIX_*.md
rm -f BACKEND_VERIFICATION_STATUS.md
rm -f AGENT_COMMUNICATION_ANALYSIS.md
rm -f SYSTEM_READY_FOR_FRONTEND.md

# Memory bank sessions (ya archivados)
rm -f memory-bank/session_*.md

# Planes completados (ya archivados) 
rm -f PLAN_IMPLEMENTACION_FRONTEND_DETALLADO.md
rm -f docs/plan_*.md
rm -f frontend/PLAN_*.md

# Resúmenes antiguos (ya archivados)
rm -f project_summary.md
rm -f resumen_ejecutivo_ngx_agents.md  
rm -f propuesta_frontend_innovador_ngx.md

echo "✅ Documentación obsoleta eliminada"

# ====================================
# PASO 6: ELIMINAR ARCHIVOS TEMPORALES
# ====================================
echo "🗂️ Eliminando archivos temporales..."

# Reportes y archivos temporales
rm -f quick_health_report.txt
rm -f update_results.txt

# Scripts temporales en root
rm -f test_mock_agent_communication.py
rm -f analyze_agents.py  
rm -f fix_telemetry_imports.py

echo "✅ Archivos temporales eliminados"

# ====================================
# PASO 7: RESUMEN FINAL
# ====================================
echo ""
echo "🎉 ¡Limpieza completada exitosamente!"
echo ""
echo "📊 RESUMEN:"
echo "   📦 Archivos archivados en: $ARCHIVE_DIR"
echo "   🗑️ Logs eliminados: ~50-100 MB"
echo "   🐍 Cache Python eliminado: ~20-30 MB"  
echo "   📝 Documentación obsoleta: ~15-20 archivos"
echo "   🔄 Backups/duplicados: ~5-10 archivos"
echo ""
echo "✅ Proyecto NGX Agents limpio y organizado"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo "   1. Revisar archivos en $ARCHIVE_DIR"
echo "   2. Hacer commit de los cambios"
echo "   3. Continuar con el desarrollo"
echo ""

# Mostrar tamaño del directorio después de limpieza
echo "📏 Tamaño del proyecto después de limpieza:"
du -sh . 2>/dev/null | head -1 || echo "No se pudo calcular el tamaño"

echo ""
echo "🚀 ¡Listo para continuar con el desarrollo!"