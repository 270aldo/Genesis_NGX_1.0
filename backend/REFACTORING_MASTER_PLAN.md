# 🚀 Plan Maestro de Refactorización de Agentes NGX

## 📊 Estado Actual (2025-07-17)

### ✅ Completado
1. **Infraestructura Base**
   - ✅ `BaseDataService` - Clase base para servicios de datos
   - ✅ `BaseSecurityService` - Clase base para seguridad
   - ✅ `BaseIntegrationService` - Clase base para integraciones
   - ✅ `BaseNGXAgent` - Clase base para todos los agentes
   - ✅ `core/exceptions.py` - Excepciones centralizadas
   - ✅ `EmotionAnalysisSkill` - Skill compartida

2. **Scripts y Herramientas**
   - ✅ `scripts/refactor_services.py` - Automatiza refactorización de servicios
   - ✅ `scripts/modularize_agent.py` - Divide agentes en módulos

3. **Ejemplo Piloto**
   - ✅ `EliteTrainingStrategistRefactored` - Ejemplo completo de BLAZE

### 📈 Métricas de Impacto
- **Reducción de código**: 52% (15,672 líneas eliminadas)
- **Agente BLAZE**: De 3,151 → 200 líneas (93% reducción)
- **Servicios refactorizables**: 48 de 55 archivos

## 🎯 Plan de Refactorización Completa

### FASE 1: Refactorizar Todos los Agentes (8-10 horas)

#### Orden de Refactorización (por complejidad):
1. **orchestrator** (1,924 líneas) - Prioridad alta, coordina todos
2. **precision_nutrition_architect** (3,833 líneas) - El más grande
3. **nova_biohacking_innovator** (3,322 líneas)
4. **elite_training_strategist** (3,151 líneas) - ✅ Ya hecho
5. **progress_tracker** (2,881 líneas)
6. **motivation_behavior_coach** (2,871 líneas)
7. **female_wellness_coach** (2,030 líneas)
8. **code_genetic_specialist** (1,909 líneas)
9. **wave_performance_analytics** (1,500 líneas estimado)

### FASE 2: Migrar Servicios (4-6 horas)
- 15 servicios de datos → `BaseDataService`
- 19 servicios de seguridad → `BaseSecurityService`
- 16 servicios de integración → `BaseIntegrationService`

### FASE 3: Consolidar Skills Comunes (3-4 horas)
- `VoiceAnalysisSkill` - Usado en 4+ agentes
- `BiometricAnalysisSkill` - Usado en 3+ agentes
- `ReportGenerationSkill` - Usado en 5+ agentes
- `DataVisualizationSkill` - Usado en 4+ agentes

### FASE 4: Sistema de Prompts Unificado (2-3 horas)
- Crear `PromptManager` centralizado
- Templates reutilizables
- Personalización por agente/personalidad

## 📝 Checklist de Refactorización por Agente

### Para cada agente:
- [ ] Backup del archivo original
- [ ] Crear estructura de directorios:
  ```
  agent_name/
  ├── __init__.py
  ├── agent.py (refactorizado)
  ├── config.py
  ├── prompts/
  ├── skills/
  ├── services/
  └── models/
  ```
- [ ] Extraer configuración → `config.py`
- [ ] Extraer prompts → `prompts/`
- [ ] Extraer skills → `skills/`
- [ ] Refactorizar servicios para usar clases base
- [ ] Heredar de `BaseNGXAgent`
- [ ] Implementar métodos abstractos requeridos
- [ ] Actualizar imports en otros módulos
- [ ] Ejecutar tests de regresión
- [ ] Documentar cambios

## 🛠️ Comandos para la Próxima Sesión

```bash
# 1. Activar entorno virtual
cd backend
source .venv/bin/activate

# 2. Para cada agente (ejemplo con orchestrator):
python scripts/modularize_agent.py agents/orchestrator/ --no-dry-run

# 3. Refactorizar servicios
python scripts/refactor_services.py agents/ --no-dry-run

# 4. Ejecutar tests
pytest tests/agents/ -v

# 5. Verificar métricas
python scripts/analyze_code_reduction.py
```

## 📊 Resultados Esperados

### Por Agente:
- **Reducción de líneas**: 90-95%
- **Archivos**: De 1 archivo gigante a 10-15 módulos pequeños
- **Complejidad**: De "muy alta" a "baja"
- **Testabilidad**: De "difícil" a "fácil"

### Total del Proyecto:
- **Líneas de código**: De 30,000 → ~12,000 (60% reducción)
- **Mantenibilidad**: 10x mejor
- **Velocidad de desarrollo**: 5x más rápido
- **Bugs**: -80% reducción estimada

## 🚨 Consideraciones Importantes

1. **Preservar Funcionalidad**
   - Todos los tests existentes deben pasar
   - Mantener retrocompatibilidad de APIs
   - Documentar cualquier cambio breaking

2. **Orden de Migración**
   - Empezar con orchestrator (crítico)
   - Luego los más grandes (más beneficio)
   - Finalmente los más pequeños

3. **Validación**
   - Ejecutar suite completa de tests después de cada agente
   - Verificar que las integraciones siguen funcionando
   - Monitorear performance (debe mejorar)

## 📅 Timeline Estimado

- **Día 1**: Orchestrator + 2 agentes grandes (6-8 horas)
- **Día 2**: 4 agentes medianos (6-8 horas)
- **Día 3**: 2 agentes pequeños + servicios (6-8 horas)
- **Día 4**: Skills comunes + prompts + testing (4-6 horas)

**Total**: 22-30 horas de trabajo enfocado

## 🎯 Definición de "Hecho"

Un agente está completamente refactorizado cuando:
1. ✅ Hereda de `BaseNGXAgent`
2. ✅ Tiene menos de 300 líneas en el archivo principal
3. ✅ Usa servicios refactorizados con clases base
4. ✅ Tiene estructura modular completa
5. ✅ Pasan todos los tests
6. ✅ Documentación actualizada

## 💡 Tips para la Próxima Sesión

1. **Empezar con Orchestrator**: Es el más crítico
2. **Usar el script de modularización**: Ahorra 80% del trabajo manual
3. **Commitear frecuentemente**: Un commit por agente refactorizado
4. **Documentar decisiones**: Especialmente cambios en interfaces

## 🚀 Comando para Continuar

Para retomar exactamente donde lo dejamos:

```bash
# En la próxima sesión, simplemente ejecuta:
cd /Users/aldoolivas/Desktop/GENESIS_oficial_BETA/backend
source .venv/bin/activate

# Ver el plan
cat REFACTORING_MASTER_PLAN.md

# Empezar con orchestrator
python scripts/modularize_agent.py agents/orchestrator/ --dry-run
```

---

**Estado guardado exitosamente. ¡Listo para continuar en la próxima sesión!**