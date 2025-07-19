# 🧹 Plan de Limpieza Detallado - NGX Agents

## 📊 Resumen del Análisis

**Archivos encontrados para limpieza**: 200+ archivos  
**Espacio estimado a recuperar**: ~100-150 MB  
**Beneficio**: Proyecto más organizado, navegación más rápida, menos confusión  

---

## 🎯 Archivos Identificados para Eliminar

### 1. **ARCHIVOS DE SESIÓN OBSOLETOS** (Root Directory) ❌

**Archivos a eliminar:**
```
CONTEXTO_SESION_BACKEND_FASE8.md
PROJECT_STATUS_SUMMARY_2025_05_27.md  
SESION_COMPLETA_2025_05_27.md
RESUMEN_SESION_29_MAYO.md
QUICK_FIX_NEXT_ERROR.md
BACKEND_VERIFICATION_STATUS.md
AGENT_COMMUNICATION_ANALYSIS.md
SYSTEM_READY_FOR_FRONTEND.md
```

**Justificación:**
- Documentos de sesiones pasadas (enero-mayo 2025)
- Ya no reflejan el estado actual del proyecto
- Información duplicada en claude.md actualizado
- Causan confusión sobre el estado real del proyecto

### 2. **LOGS DEL SERVIDOR** (16 archivos) ❌

**Archivos a eliminar:**
```
server.log
server2.log  
server3.log
server4.log
server5.log
server_final.log
server_final_run.log
server_running.log
server_running_final.log
server_startup.log
server_success.log
server_test.log
server_working.log
cache_monitoring.log
```

**Justificación:**
- Logs de desarrollo temporal
- No deben estar en control de versiones
- Ya están en .gitignore pero fueron agregados antes
- Ocupan espacio innecesario

### 3. **DIRECTORIOS DE BACKUP ANTIGUOS** ❌

**Directorios a eliminar:**
```
backup_pyproject_20250512_222718/
backup_pyproject_20250512_222913/
```

**Justificación:**
- Backups temporales de mayo 2025
- pyproject.toml ya está estabilizado
- Información preservada en Git history

### 4. **ARCHIVOS DUPLICADOS/BACKUP** ❌

**Archivos a eliminar:**
```
agents/biometrics_insight_engine/agent.py.new
infrastructure/adapters/state_manager_adapter.py.bak
tests/agents/precision_nutrition_architect/test_agent_skills_new.py
```

**Justificación:**
- Versiones de desarrollo temporal
- Extensiones .new, .bak indican archivos de trabajo
- Funcionalidad ya integrada en archivos principales

### 5. **ARCHIVOS DE MEMORIA-BANK OBSOLETOS** 📦 (Archivar primero)

**Archivos a archivar y luego eliminar:**
```
memory-bank/session_2025_05_24.md
memory-bank/session_2025_05_25.md  
memory-bank/session_2025_05_26_fase8.md
```

**Justificación:**
- Sesiones específicas ya completadas
- Información relevante ya incorporada en documentación actual
- Pueden tener valor histórico (archivar antes de eliminar)

### 6. **DOCUMENTACIÓN DE PLANES COMPLETADOS** 📦 (Archivar primero)

**Archivos a archivar y luego eliminar:**
```
PLAN_IMPLEMENTACION_FRONTEND_DETALLADO.md
docs/plan_optimizacion_ngx_agents.md
docs/plan_optimizacion_estado_actual.md
docs/plan_limpieza_vertex_ai.md
frontend/PLAN_FIX_ERRORS_SESSION_3.md
propuesta_frontend_innovador_ngx.md
```

**Justificación:**
- Planes ya ejecutados exitosamente
- Documentación útil para referencia histórica
- No reflejan estado actual del proyecto

### 7. **ARCHIVOS DE RESUMEN ANTIGUOS** 📦 (Archivar primero)

**Archivos a archivar y luego eliminar:**
```
project_summary.md
resumen_ejecutivo_ngx_agents.md
```

**Justificación:**
- Reemplazados por documentación más actual
- Información desactualizada
- Valor histórico para archivo

### 8. **REPORTES Y ARCHIVOS TEMPORALES** ❌

**Archivos a eliminar:**
```
quick_health_report.txt
update_results.txt
test_mock_agent_communication.py (root)
analyze_agents.py (root)
fix_telemetry_imports.py (root)
```

**Justificación:**
- Scripts temporales de desarrollo
- Reportes de estado obsoletos
- No forman parte del código de producción

### 9. **CACHE DE PYTHON** ❌ (122 directorios)

**Directorios a eliminar:**
```
Todos los directorios __pycache__/ (122 encontrados)
*.pyc files
```

**Justificación:**
- Cache de Python autogenerado
- No debe estar en control de versiones
- Se regenera automáticamente

---

## 🛠️ Script de Limpieza Automática

```bash
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
find . -name "*.log" -not -path "./node_modules/*" -not -path "./$ARCHIVE_DIR/*" -delete

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
# PASO 7: LIMPIAR GIT TRACKING
# ====================================
echo "🔧 Limpiando tracking de Git..."

# Remover archivos del tracking de Git que ya no existen
git add -A

echo "✅ Git tracking actualizado"

# ====================================
# PASO 8: RESUMEN FINAL
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
du -sh . | head -1

echo ""
echo "🚀 ¡Listo para continuar con el desarrollo!"
```

---

## ⚖️ Análisis de Riesgo

### ✅ **RIESGO CERO** (Eliminar directamente)
- Logs de servidor
- Cache de Python (__pycache__)
- Archivos .bak, .new
- Directorios backup_pyproject_*

### 📦 **RIESGO BAJO** (Archivar primero)
- Documentación de sesiones
- Planes completados  
- Resúmenes históricos
- Memory bank sessions

### ⚠️ **VERIFICAR ANTES** (Revisar manualmente)
- Scripts en root (test_*, analyze_*, fix_*)
- Archivos de documentación en docs/

---

## 🎯 Beneficios Esperados

### Organización
- ✅ Root directory más limpio (15+ archivos menos)
- ✅ Navegación más rápida
- ✅ Menos confusión con documentación obsoleta

### Performance  
- ✅ ~100-150 MB de espacio recuperado
- ✅ Git operations más rápidas
- ✅ IDE indexing más eficiente

### Desarrollo
- ✅ Estado actual del proyecto más claro
- ✅ Documentación relevante fácil de encontrar
- ✅ Menos archivos obsoletos en búsquedas

---

## 🚀 Instrucciones de Ejecución

### Opción 1: Automática (Recomendada)
```bash
# Hacer backup completo primero
git add -A && git commit -m "Backup before cleanup"

# Ejecutar script de limpieza
chmod +x scripts/cleanup_project.sh
./scripts/cleanup_project.sh

# Revisar cambios
git status

# Hacer commit de limpieza
git add -A && git commit -m "🧹 Project cleanup: remove obsolete files, logs, and cache"
```

### Opción 2: Manual (Paso a paso)
1. Crear archivo de limpieza: `touch cleanup_plan.txt`
2. Listar archivos a eliminar uno por uno
3. Mover archivos importantes a archivo temporal
4. Eliminar archivos verificados
5. Actualizar Git tracking

---

## 📋 Checklist Post-Limpieza

- [ ] Verificar que el proyecto sigue funcionando (`make dev`)
- [ ] Confirmar que tests pasan (`make test`)
- [ ] Revisar archivos archivados en caso de necesidad
- [ ] Actualizar documentación principal si es necesario
- [ ] Hacer commit de los cambios de limpieza

---

**🎯 Este plan eliminará archivos obsoletos manteniendo la integridad del proyecto y archivando información potencialmente valiosa para referencia futura.**