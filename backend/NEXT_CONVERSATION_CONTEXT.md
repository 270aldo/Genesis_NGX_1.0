# Contexto para Próxima Conversación - GENESIS Testing

## 🎯 Objetivo Principal
Llevar GENESIS de 15% a 85% de cobertura de tests siguiendo el plan maestro establecido.

## 📊 Estado Actual (18 de Julio, 2025)

### Completado ✅
1. **Refactorización ADK/A2A**: Todos los 11 agentes refactorizados
2. **Dependencias**: Verificadas y corregidas (ElevenLabs, Google Vision opcional)
3. **Documentación**: README, CLAUDE.md, TESTING_STATUS.md actualizados
4. **Análisis de Tests**: Identificados problemas y creado plan de acción

### Pendiente ❌
1. **Tests rotos**: 11 de persistencia + 4 de agentes con imports incorrectos
2. **Cobertura**: Solo 15-20% (objetivo 85%)
3. **Tests ADK/A2A**: No existen tests para nueva arquitectura
4. **Monitoreo**: Prometheus/Grafana no configurados

## 🔧 Tareas Inmediatas (Por Orden)

### 1. Corregir Tests Existentes
```python
# Cambios de imports necesarios:
agents.biohacking_innovator → agents.nova_biohacking_innovator
EliteTrainingStrategist → BlazeTurboTrainer
agents.recovery_corrective → ELIMINAR (no existe)

# Mock de telemetría:
core.telemetry.telemetry_manager → core.telemetry_loader.telemetry
```

### 2. Implementar/Mockear en SupabaseClient
```python
def get_or_create_user_by_api_key(self, api_key: str) -> dict
def log_conversation_message(self, user_id: str, role: str, message: str) -> dict
def get_conversation_history(self, user_id: str, limit: int = 10) -> list
```

### 3. Crear Tests Base ADK/A2A
```python
# Test de herencia dual obligatoria
def test_agent_must_inherit_from_both_bases():
    class InvalidAgent(BaseNGXAgent):  # Falta ADKAgent
        pass
    # Debe fallar

# Test de métodos requeridos
def test_agent_required_methods():
    # process(), get_capabilities(), handle_error()
```

## 🏗️ Arquitectura Clave

### Herencia de Agentes (CRÍTICO)
```python
# CORRECTO - SIEMPRE ASÍ
class NombreAgente(BaseNGXAgent, ADKAgent):
    """Hereda de AMBAS clases base"""
    
# INCORRECTO - NUNCA
class NombreAgente(BaseNGXAgent):  # Falta ADKAgent
```

### Estructura de Archivos
```
agents/
└── agent_name/
    ├── agent.py         # < 400 líneas
    ├── config.py        # Pydantic config
    ├── prompts.py       # Prompts centralizados
    └── skills/          # Una skill por archivo
```

### Nombres Correctos de Agentes
| Directorio | Clase | Nombre |
|------------|-------|--------|
| orchestrator | NexusCentralCommand | NEXUS |
| elite_training_strategist | BlazeTurboTrainer | BLAZE |
| precision_nutrition_architect | SageNutritionalWisdom | SAGE |
| code_genetic_specialist | CodeGeneticSpecialist | CODE |
| wave_performance_analytics | WavePerformanceAnalytics | WAVE |
| female_wellness_coach | LunaFeminineBalance | LUNA |
| progress_tracker | StellaProgressTracker | STELLA |
| motivation_behavior_coach | SparkMotivationalCoach | SPARK |
| nova_biohacking_innovator | NovaBiohackingInnovator | NOVA |
| backend/guardian | GuardianSecurityOps | GUARDIAN |
| backend/node | NodeSystemIntegration | NODE |

## 📈 Métricas de Éxito

### Milestone 1 (50% cobertura)
- [ ] Tests existentes corregidos y pasando
- [ ] Tests base para ADK/A2A
- [ ] Tests básicos para NEXUS, BLAZE, SAGE
- [ ] Al menos 1 test por skill principal

### Milestone 2 (85% cobertura)
- [ ] Tests completos para todos los agentes
- [ ] Tests de integración A2A
- [ ] Tests de streaming/SSE
- [ ] Tests de rendimiento y carga

## 🛠️ Comandos Útiles
```bash
# Desarrollo de tests
make test                    # Ejecutar todos
make test-unit              # Solo unitarios
make test-agents            # Solo agentes
make test-cov               # Con cobertura

# Debugging
pytest -vvs                 # Verbose output
pytest -k "test_name"       # Test específico
pytest --pdb                # Debugger en failures
pytest -x                   # Stop en primer failure

# Cobertura
pytest --cov=agents --cov-report=html
open htmlcov/index.html
```

## 📝 Notas Importantes

1. **Prioridad**: NEXUS > BLAZE > SAGE (agentes más críticos)
2. **No modificar**: Estructura ADK/A2A ya establecida
3. **Mocks necesarios**: Vertex AI, Redis, Supabase, ElevenLabs
4. **Tests async**: Usar pytest-asyncio correctamente
5. **Fixtures**: Reutilizar para agentes similares

## 🚀 Primera Acción Recomendada
```bash
# 1. Corregir imports en tests de agentes
find tests -name "*.py" -exec grep -l "biohacking_innovator\|EliteTrainingStrategist\|recovery_corrective" {} \;

# 2. Ejecutar tests corregidos
pytest tests/test_agents -v --tb=short

# 3. Ver cobertura actual real
pytest --cov=. --cov-report=term-missing
```

## 🔗 Referencias
- `/backend/CLAUDE.md` - Guía principal de desarrollo
- `/backend/TESTING_STATUS.md` - Plan detallado de testing
- `/backend/DEPENDENCIES_STATUS.md` - Estado de dependencias
- `/backend/agents/*/agent.py` - Implementaciones refactorizadas

---

**RECORDAR**: El objetivo es tener un backend robusto y bien testeado para soportar la integración con todo el ecosistema NGX. Los tests son la base de la confiabilidad.