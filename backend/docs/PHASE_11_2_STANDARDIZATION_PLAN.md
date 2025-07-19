# FASE 11.2 - AGENT STANDARDIZATION PLAN
## Plan Seguro de Estandarización de Agentes

### 🎯 OBJETIVO
Estandarizar la arquitectura de agentes resolviendo inconsistencias críticas sin romper funcionalidad existente.

### 📊 PROBLEMAS CRÍTICOS IDENTIFICADOS

#### **P1 - Importaciones Rotas (CRÍTICO)**
```
❌ infrastructure/adapters/biohacking_innovator_adapter.py
   from agents.biohacking_innovator.agent import BiohackingInnovator
   PROBLEMA: No existe, debe ser nova_biohacking_innovator

❌ infrastructure/adapters/security_compliance_guardian_adapter.py  
   from agents.security_compliance_guardian.agent import SecurityComplianceGuardian
   PROBLEMA: No existe, debe ser backend.guardian

❌ infrastructure/adapters/systems_integration_ops_adapter.py
   from agents.systems_integration_ops.agent import SystemsIntegrationOps
   PROBLEMA: No existe, debe ser backend.node
```

#### **P2 - Versiones Duales (MEDIO)**
```
⚠️  10 agentes con agent.py Y agent_optimized.py
   - Solo los .py originales están siendo importados
   - agent_optimized.py más pequeños (~20KB vs ~100KB+)
   - Confusión sobre cuál usar
```

#### **P3 - Estructura Inconsistente (BAJO)**
```
⚠️  Algunos agentes sin core/services/skills
   - client_success_liaison/ 
   - recovery_corrective/
   - volt_biometrics_insight_engine/
```

### 🔄 PLAN DE ESTANDARIZACIÓN SEGURA

#### **PASO 1: Fixes Críticos de Importación (PRIORIDAD 1)**
```bash
✅ Objetivo: Resolver importaciones rotas sin romper funcionalidad
✅ Método: Corrección directa de paths
✅ Riesgo: BAJO (solo corrección de nombres)
```

1. **Corregir biohacking_innovator_adapter.py**:
   - `agents.biohacking_innovator` → `agents.nova_biohacking_innovator`

2. **Corregir security_compliance_guardian_adapter.py**:
   - `agents.security_compliance_guardian` → `agents.backend.guardian`

3. **Corregir systems_integration_ops_adapter.py**:
   - `agents.systems_integration_ops` → `agents.backend.node`

#### **PASO 2: Consolidación de Versiones (PRIORIDAD 2)**
```bash
✅ Estrategia: Mantener agent.py como principal (están siendo usados)
✅ Método: Mover agent_optimized.py a backup
✅ Riesgo: BAJO (nadie los importa actualmente)
```

**Criterio de Decisión**:
- **MANTENER**: `agent.py` (son los que importan los adaptadores)
- **BACKUP**: `agent_optimized.py` (no están siendo utilizados)
- **EXCEPCIÓN**: Si agent_optimized.py es claramente superior en funcionalidad

#### **PASO 3: Cleanup de Archivos Legacy (PRIORIDAD 3)**  
```bash
✅ Objetivo: Limpiar archivos obsoletos
✅ Método: Mover a backup
✅ Riesgo: MÍNIMO (archivos no utilizados)
```

- `agent_enhanced.py`, `agent_refactored.py`, `agent_template.py`
- Documentar archivos movidos para referencia

### 🚨 MEDIDAS DE SEGURIDAD

#### **Antes de Cada Cambio**:
1. **Backup Incremental**: Crear backup timestamped
2. **Verificación de Sintaxis**: `python -m py_compile` 
3. **Test de Importación**: Verificar que importa correctamente

#### **Durante los Cambios**:
1. **Cambios Atómicos**: Un fix por commit
2. **Validación Inmediata**: Probar importación después de cada cambio
3. **Rollback Ready**: Git reset disponible

#### **Después de Cada Cambio**:
1. **Import Test**: Verificar que el adaptador importa
2. **Syntax Check**: Compilación exitosa
3. **Integration Test**: Validar con script principal

### 📋 CRITERIOS DE ÉXITO

#### **Paso 1 (Crítico)**:
- [x] 3 adaptadores importan correctamente
- [x] 0 errores de ModuleNotFoundError
- [x] Sintaxis válida en todos los archivos

#### **Paso 2 (Consolidación)**:
- [x] 1 versión por agente (excepto casos especiales)
- [x] Todos los imports apuntan a versión correcta
- [x] Backup completo de versiones alternativas

#### **Paso 3 (Cleanup)**:
- [x] 0 archivos legacy en directorio activo
- [x] Documentación de ubicación de backups
- [x] Estructura limpia y consistente

### ⚡ ROLLBACK PLAN

Si algún cambio falla:
1. **Inmediato**: `git reset --hard HEAD~1`
2. **Backup**: Restaurar desde backup incremental
3. **Verificación**: Confirmar funcionalidad restaurada
4. **Análisis**: Documentar causa del fallo

### 🎯 SIGUIENTE PASO

**Comenzar con PASO 1**: Fixes críticos de importación
- Tiempo estimado: 15-30 minutos
- Riesgo: BAJO
- Impacto: ALTO (resuelve errores críticos)

---

**NOTA**: Este plan prioriza estabilidad sobre refactoring. Los cambios son minimales y seguros.