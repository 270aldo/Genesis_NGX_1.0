# Estado de Testing - GENESIS Backend

## 📊 Resumen Ejecutivo (18 de Julio, 2025)

### Estado Actual
- **Cobertura actual**: ~15-20% (objetivo: 85%)
- **Tests ejecutables**: 9 tests unitarios básicos pasan
- **Tests con problemas**: Mayoría de tests desactualizados tras refactorización ADK/A2A

### ✅ Tests que Funcionan
```
tests/unit/auth/test_auth.py (8 tests) - Todos pasan
tests/unit/test_settings.py (1 test) - Pasa
```

### ❌ Tests que Fallan

#### 1. Tests de Persistencia (11 tests)
- **Problema**: Métodos faltantes en SupabaseClient
- **Métodos necesarios**:
  - `get_or_create_user_by_api_key`
  - `log_conversation_message`
  - `get_conversation_history`

#### 2. Tests de Agentes (múltiples)
- **Problema**: Imports incorrectos tras refactorización
- **Ejemplos**:
  - `ModuleNotFoundError: No module named 'agents.biohacking_innovator'` (ahora es nova_biohacking_innovator)
  - `ImportError: cannot import name 'EliteTrainingStrategist'` (ahora es BlazeTurboTrainer)
  - `ModuleNotFoundError: No module named 'agents.recovery_corrective'` (agente no existe)

#### 3. Tests de Adaptadores
- **Problema**: Mock incorrecto de telemetría
- **Error**: `AttributeError: <module 'core.telemetry'> does not have the attribute 'telemetry_manager'`

### 📋 Plan de Acción para Alcanzar 85% de Cobertura

#### Fase 1: Corrección de Tests Existentes (Prioridad Alta)
1. **Actualizar imports de agentes** con nombres correctos post-refactorización
2. **Implementar métodos faltantes** en SupabaseClient o crear mocks apropiados
3. **Corregir mocks de telemetría** en tests de adaptadores
4. **Actualizar tests de agentes** para nueva arquitectura ADK/A2A

#### Fase 2: Nuevos Tests Críticos (Prioridad Alta)
1. **Tests para BaseNGXAgent y ADKAgent** (clases base)
2. **Tests para skills modulares** de cada agente
3. **Tests para sistema A2A** (comunicación entre agentes)
4. **Tests para streaming y SSE**

#### Fase 3: Tests de Integración (Prioridad Media)
1. **Tests end-to-end** del orchestrator
2. **Tests de flujos multi-agente**
3. **Tests de caché multicapa**
4. **Tests de circuit breakers**

#### Fase 4: Tests de Rendimiento (Prioridad Media)
1. **Benchmarks de respuesta** de agentes
2. **Tests de carga** para endpoints
3. **Tests de concurrencia** para Redis
4. **Tests de límites de rate limiting**

### 🛠️ Herramientas de Testing

#### Configuradas
- pytest (8.3.5)
- pytest-asyncio (0.23.8)
- pytest-cov (4.1.0)
- pytest-mock (3.14.1)
- pytest-xdist (3.7.0)
- pytest-benchmark (5.1.0)

#### Marcadores Disponibles
- `unit`: Tests unitarios sin FastAPI
- `integration`: Tests con FastAPI completo
- `agents`: Tests específicos de agentes
- `api`: Tests de endpoints API

### 📈 Métricas de Cobertura por Módulo

| Módulo | Cobertura Actual | Objetivo |
|--------|------------------|----------|
| core/auth | ~95% | 95% |
| core/settings | 100% | 100% |
| agents/* | ~0% | 85% |
| clients/* | ~0% | 80% |
| app/routers/* | ~0% | 90% |
| infrastructure/* | ~0% | 85% |

### 🔧 Comandos Útiles

```bash
# Ejecutar todos los tests
make test

# Solo tests unitarios
make test-unit

# Tests con cobertura
make test-cov

# Tests en paralelo
pytest -n auto

# Tests con output detallado
pytest -vvs

# Tests específicos
pytest tests/unit/auth -v
pytest -k "test_auth" -v
pytest -m agents
```

### 📝 Notas Importantes

1. **Prioridad en agentes core**: NEXUS (orchestrator), BLAZE (training), SAGE (nutrition)
2. **Tests deben cubrir**: Happy path, edge cases, error handling, validaciones
3. **Mocks necesarios**: Vertex AI, Redis, Supabase, APIs externas
4. **Tests de streaming**: Críticos para UX, usar AsyncGenerator mocks

### 🎯 Objetivo Inmediato

1. Corregir los 11 tests de persistencia
2. Actualizar 4 tests de agentes con imports correctos
3. Crear suite básica para orchestrator (10+ tests)
4. Alcanzar 50% de cobertura como milestone intermedio

---

**Última actualización**: 18 de Julio, 2025
**Próxima revisión**: Después de corregir tests existentes